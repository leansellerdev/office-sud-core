from pydantic import BaseModel

from core.models.base import (
    AuthParams,
    FillInfoPageParams,
    PaymentPageParams,
    SelectOptionsPageParams,
    UploadFilesPageParams,
)
from core.models.statement import StatementFillInfoParams


class SetupParams(BaseModel):
    auth_params: AuthParams
    select_options_page_params: SelectOptionsPageParams
    fill_info_page_params: FillInfoPageParams | StatementFillInfoParams
    payment_page_params: PaymentPageParams
    upload_files_page_params: UploadFilesPageParams

    type: str
    db_scheme: str

    max_cases_per_day: int = 0
    result_dir_path: str = None
