import simplejson as json

from core.models import UploadFilesPageParams
from core.models.base import (
    AuthParams,
    FillInfoPageParams,
    PaymentPageParams,
    SelectOptionsPageParams,
)
from core.models.setup import SetupParams
from core.models.statement import StatementFillInfoParams


def read_config(config_name: str) -> SetupParams:
    config_name = str(config_name)

    if not config_name.endswith(".json"):
        raise TypeError("Config must be a JSON file")

    with open(config_name, "r", encoding="utf-8") as config_file:
        config_file = json.load(config_file)

    auth_params = AuthParams(
        bin=config_file["auth"]["creds"]["bin"],
        password=config_file["auth"]["creds"]["password"],
        nca_path=config_file["auth"]["nca"]["nca_path"],
        nca_password=config_file["auth"]["nca"]["nca_password"],
    )

    if config_file.get("type") == "statement":
        fill_info_params = StatementFillInfoParams(**config_file["fill_info_page"])
    else:
        fill_info_params = FillInfoPageParams(**config_file["fill_info_page"])

    select_options_params = SelectOptionsPageParams(
        **config_file["select_options_page"]
    )
    payment_params = PaymentPageParams(**config_file["payment_page"])
    upload_files_params = UploadFilesPageParams(**config_file["upload_files_page"])

    return SetupParams(
        auth_params=auth_params,
        select_options_page_params=select_options_params,
        fill_info_page_params=fill_info_params,
        payment_page_params=payment_params,
        upload_files_page_params=upload_files_params,
        type=config_file["type"],
        db_scheme=config_file["db_scheme"],
        result_dir_path=config_file["result_dir_path"],
        max_cases_per_day=config_file["max_cases_per_day"],
    )
