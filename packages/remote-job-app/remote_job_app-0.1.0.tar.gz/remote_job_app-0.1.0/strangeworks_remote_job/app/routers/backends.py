"""Routers for backends."""
from fastapi import APIRouter, Request

router = APIRouter(prefix="/backends", tags=["backends"])


@router.post("/list-backends")
def get_backend_list(request: Request):
    ...


@router.post("/get-backend-properties")
def get_backend_properties(request: Request):
    ...


@router.post("/get-backend-configuration")
def get_backend_configuration(request: Request):
    ...


@router.post("/get-backend-status")
def get_backend_status(request: Request):
    ...


@router.post("/get-backend-default-settings")
def get_backend_default_settings(request: Request):
    ...
