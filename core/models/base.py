from os import PathLike
from typing import Union

from pydantic import BaseModel


class AuthParams(BaseModel):
    bin: str
    password: str

    nca_path: str | PathLike
    nca_password: str


class SelectOptionsPageParams(BaseModel):
    case_type: str
    instance: str
    doc_type: str


class FillInfoPageParams(BaseModel):
    class AdditionalPerson(BaseModel):
        type: int
        side: int
        iin: str
        phone_number: Union[str, None]
        address: Union[str, None]

    district: str
    court: str
    court_name: str
    org_bin: str
    org_address: str
    org_requisites: Union[str, None] = None
    additional_persons: list[AdditionalPerson] = []


class PaymentPageParams(BaseModel):
    kbk: str
    is_online: bool = False


class UploadFilesPageParams(BaseModel):
    base_req: str
    additional_req: str
    file_list: list[str]
