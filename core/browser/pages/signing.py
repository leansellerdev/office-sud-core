import asyncio
import glob
import os
from pathlib import Path
from urllib.parse import parse_qs

from pydoll.browser.tab import Tab
from pydoll.constants import By
from pydoll.protocol.network.types import ErrorReason

from core.browser.constants.selectors import SigningPageSelectors
from core.browser.pages import OfficeSudBase
from core.models import SetupParams
from settings import PATH


class SigningPage(OfficeSudBase):
    selectors = SigningPageSelectors

    def __init__(self, params: SetupParams) -> None:
        super().__init__()
        self.PAGE_URL = self.BASE_URL + "form/requestType2/sign.xhtml"
        self.RESULT_PAGE = self.BASE_URL + "form/requestType2/sendResult.xhtml"

        self.params = params

    async def sign_statement(self, tab: Tab) -> None:
        await self.wait_page(tab, self.PAGE_URL)

        certificate_choice_button = await tab.find_or_wait_element(
            By.XPATH, self.selectors.SIGN_BUTTON, timeout=30
        )
        await certificate_choice_button.click()

        await self.nca_layer.choose_key(
            str(PATH / self.params.auth_params.nca_path),
            self.params.auth_params.password,
        )

    async def get_notification_code(self, tab: Tab) -> str:
        await self.wait_page(tab, self.RESULT_PAGE)
        await tab.enable_network_events()

        download_button = await tab.find_or_wait_element(
            By.CSS_SELECTOR,
            self.selectors.DOWNLOAD_RESULT_FILE_BUTTON,
            timeout=30,
        )
        await download_button.click()

        await asyncio.sleep(1)
        (
            request_id,
            notification_code,
        ) = await self._get_notification_code_from_logs(tab)
        await tab.fail_request(request_id, error_reason=ErrorReason.ABORTED)

        return notification_code

    @staticmethod
    async def _get_notification_code_from_logs(tab: Tab) -> tuple[str, str]:
        request_id = ""
        notification_code = ""
        network_logs = await tab.get_network_logs(filter="requestTalonDownload")
        for log in network_logs:
            request_id = log["params"]["requestId"]
            post_data = log["params"]["request"].get("postData", None)
            if post_data:
                params = parse_qs(post_data)
                notification_code = params["r"][0]
                break

        return request_id, notification_code  # type: ignore

    @staticmethod
    async def _wait_file_to_be_downloaded(
        download_path: Path | str, timeout: int = 120
    ) -> None:
        async with asyncio.timeout(timeout):
            while True:
                cr_files = glob.glob(os.path.join(download_path, "*.crdownload"))
                if not cr_files:
                    return

                await asyncio.sleep(0.5)
