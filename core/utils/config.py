import simplejson as json
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.models import UploadFilesPageParams
from core.models.base import (
    AuthParams,
    FillInfoPageParams,
    PaymentPageParams,
    SelectOptionsPageParams,
)
from core.models.setup import SetupParams
from core.models.statement import StatementFillInfoParams
from settings import CONFIGS, PATH


def read_config(config_name: str) -> SetupParams:
    config_name = str(config_name)

    if not config_name.endswith(".json"):
        raise TypeError("Config must be a JSON file")

    with open(config_name, "r", encoding="utf-8") as config_file:
        config_name = json.load(config_file)

    auth_params = AuthParams(
        bin=config_name["auth"]["creds"]["bin"],
        password=config_name["auth"]["creds"]["password"],
        nca_path=config_name["auth"]["nca"]["nca_path"],
        nca_password=config_name["auth"]["nca"]["nca_password"],
    )

    if config_name.get("type") == "statement":
        fill_info_params = StatementFillInfoParams(**config_name["fill_info_page"])
    else:
        fill_info_params = FillInfoPageParams(**config_name["fill_info_page"])

    select_options_params = SelectOptionsPageParams(
        **config_name["select_options_page"]
    )
    payment_params = PaymentPageParams(**config_name["payment_page"])
    upload_files_params = UploadFilesPageParams(**config_name["upload_files_page"])

    return SetupParams(
        auth_params=auth_params,
        select_options_page_params=select_options_params,
        fill_info_page_params=fill_info_params,
        payment_page_params=payment_params,
        upload_files_page_params=upload_files_params,
        type=config_name["type"],
        db_scheme=config_name["db_scheme"],
        result_dir_path=str(PATH / config_name["result_dir_path"]),
        max_cases_per_day=config_name["max_cases_per_day"],
    )


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str

    config: SetupParams = read_config(str(CONFIGS / "ccloan.json"))

    model_config = SettingsConfigDict(env_file=PATH / ".env")


settings = Settings()  # type: ignore
