"""Basic job service."""
import logging
from typing import Any, Tuple

from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.types.job import Status as JobStatus
from strangeworks_core.utils import is_empty_str
from sw_product_lib import service
from sw_product_lib.service import RequestContext

from strangeworks_remote_job.artifact import ArtifactGenerator
from strangeworks_remote_job.remote import RemoteJobAPI


def submit(
    ctx: RequestContext,
    remote_api: RemoteJobAPI,
    payload: dict[str, Any],
    artifact_generator: ArtifactGenerator | None = None,
    job_slug: str | None = None,
):
    """Submit a job.

    Parameters
    ----------
    ctx: RequestContext
        Used for making requests to the platform through product lib.
    remote_api: RemoteJobAPI
        Used for making job related requests to remote resources.
    payload: Dict[str, Any]
        Input data for the job.
    job_slug: str
        Job identifier. If passed in, the client must have created the job
        entry on the platform prior to making the submit call.

    Returns
    -------
    Job:
        Object that contains information about the job entry in platform.
    """
    # If a job slug was passed in, use that to retrieve job entry. Otherwise
    # create a new job entry on the platform.
    # Even if the job submission fails, there should be a record of it on the platform.
    sw_job = (
        service.get_job(ctx=ctx, job_slug=job_slug)
        if job_slug
        else service.create_job(
            ctx,
        )
    )

    if sw_job.status is not JobStatus.CREATED and job_slug:
        raise StrangeworksError(
            message=f"Job status (slug: {job_slug}) must be CREATED to submit a new job"
        )

    if remote_api.estimate_cost() > 0.0:
        logging.info(
            f"requesting job clearance for job request resource: {ctx.resource_slug} (job slug: {sw_job.slug})"  # noqa
        )

        if not service.request_job_clearance(ctx, remote_api.estimate_cost()):
            # did not get clearance. update job status to failed and raise error.
            service.update_job(
                ctx=ctx,
                job_slug=sw_job.slug,
                status=JobStatus.FAILED,
            )
            raise StrangeworksError(
                message=f"Job clearance denied for this resource {ctx.resource_slug}."
            )

    try:
        logging.info(f"submitting remote job request (job slug: {sw_job.slug})")
        job_id = remote_api.submit(payload)
        logging.info(
            f"job request submitted (job slug: {sw_job.slug}, remote id:{job_id})"
        )
        service.update_job(
            ctx=ctx,
            job_slug=sw_job.slug,
            external_identifier=job_id,
        )
        if artifact_generator:
            for artifact in artifact_generator(
                remote_id=job_id, input=payload, job_slug=sw_job.slug
            ):
                file = service.upload_job_artifact(
                    artifact.data,
                    ctx=ctx,
                    job_slug=sw_job.slug,
                    file_name=artifact.name,
                    json_schema=artifact.schema,
                    label=artifact.label,
                    sort_weight=artifact.sort_weight,
                    is_hidden=artifact.is_hidden,
                )

                artifact.post_hook(url=file.url, file_slug=file.slug)

    except Exception as err:
        service.update_job(
            ctx=ctx,
            job_slug=sw_job.slug,
            status=JobStatus.FAILED,
        )
        raise err

    return fetch_status(ctx, remote_api, sw_job.slug)


def fetch_status(
    ctx: RequestContext,
    remote_api: RemoteJobAPI,
    job_slug: str,
):
    """Fetch job status."""
    remote_id, current_status = _get_remote_id_and_status(ctx, job_slug)

    try:
        logging.info(
            f"fetching remote job status for job {job_slug} with remote id {remote_id})"
        )
        status = remote_api.fetch_status(remote_id)

        try:
            return service.update_job(
                ctx,
                job_slug=job_slug,
                status=remote_api.to_sw_status(status),
                remote_status=status,
            )
        except StrangeworksError as err:
            logging.error(
                f"error updating status for job (slug: {job_slug},  remote id: {remote_id}): {err.message})"  # noqa
            )
            raise err

    except Exception as err:
        service.update_job(
            ctx=ctx,
            job_slug=job_slug,
            status=JobStatus.FAILED,
        )

        raise err


def fetch_result(
    ctx: RequestContext,
    remote_api: RemoteJobAPI,
    job_slug: str,
    artifact_generator: ArtifactGenerator | None = None,
):
    """Fetch job result."""
    remote_id, current_status = _get_remote_id_and_status(ctx, job_slug)
    if current_status != JobStatus.COMPLETED and not current_status.is_terminal_state:
        # job status indicates it hastn completed and is not in a terminal state.
        # try fetching status again and return if it is not completed.
        logging.info(
            f"job (slug {job_slug}) is not in a completed state on the platform. Fetching remote status."  # noqa
        )
        updated_job = fetch_status(ctx, remote_api, job_slug)
        if updated_job.status != JobStatus.COMPLETED:
            # log and return
            logging.warn(f"job ({job_slug}) is not in a completed state")
            return updated_job

    logging.info(
        f"fetching remote job result for job {job_slug} (remote id {remote_id})"
    )
    remote_result = remote_api.fetch_result(remote_id)
    service.upload_job_artifact(
        remote_result,
        ctx=ctx,
        job_slug=job_slug,
        file_name="result.json",
    )

    if artifact_generator:
        for artifact in artifact_generator(
            remote_id=remote_id, input=remote_result, job_slug=job_slug
        ):
            file = service.upload_job_artifact(
                artifact.data,
                ctx=ctx,
                job_slug=job_slug,
                file_name=artifact.name,
                json_schema=artifact.schema,
                label=artifact.label,
                sort_weight=artifact.sort_weight,
                is_hidden=artifact.is_hidden,
            )

            artifact.post_hook(url=file.url, file_slug=file.slug)

    return service.get_job(ctx, job_slug)


def cancel(ctx: RequestContext, remote_api: RemoteJobAPI, job_slug: str):
    """Cancel a job.

    Parameters
    ----------
    ctx: RequestContext
        Used for making requests to the platform through product lib.
    remote_api: RemoteJobAPI
        Used for making job related requests to remote resources.
    job_slug: str
        Job identifier.
    """
    remote_id, current_status = _get_remote_id_and_status(ctx, job_slug)

    if current_status.is_terminal_state:
        # log and return
        logging.info(f"job ({job_slug}) is already in a terminal state")
        service.get_job(ctx, job_slug)

    remote_api.cancel(remote_id)

    return service.update_job(
        ctx=ctx,
        job_slug=job_slug,
        status=JobStatus.CANCELLED,
    )


def _get_remote_id_and_status(ctx, job_slug) -> Tuple[str, JobStatus]:
    sw_job = service.get_job(ctx, job_slug)
    if is_empty_str(sw_job.external_identifier):
        raise StrangeworksError(
            f"no external identifier found for job (slug: {job_slug})"
        )
    return (sw_job.external_identifier, sw_job.status)
