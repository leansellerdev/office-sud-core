from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions
from pydoll.browser.tab import Tab

from core.browser.pages import (
    FillInfoPage,
    LoginPage,
    PaymentPage,
    SelectOptionsPage,
    UploadFilesPage,
)
from core.browser.pages.signing import SigningPage
from core.models import SetupParams


class OfficeSudProcess:
    def __init__(
        self,
        config: SetupParams,
        /,
        chrome_options: ChromiumOptions = None,
        download_dir: str = None,
        headless_browser: bool = False,
    ) -> None:
        self.params: SetupParams = config

        self._chrome_options = chrome_options
        self._download_dir = download_dir
        self._headless_browser = headless_browser
        self.chrome: Chrome = None

        self.login = LoginPage(params=self.params)
        self.select_options = SelectOptionsPage(params=self.params)
        self.fill_info = FillInfoPage(params=self.params)
        self.set_payment = PaymentPage(params=self.params)
        self.upload_files = UploadFilesPage(params=self.params)
        self.signing = SigningPage(params=self.params)

        self.tab: Tab = None

    async def process_case(self) -> None:
        """
        Main process of the application.
        """
        pass

    async def process_login(self, *, with_creds: bool = False) -> None:
        """
        First step of the process.
        """
        if not with_creds:
            await self.login.nca_login(self.tab)
            return

        await self.login.creds_login(self.tab)

    async def process_select_options(self) -> None:
        """
        Second step of the process.
        """
        await self.select_options.goto_page(self.tab)
        await self.select_options.select_options(self.tab)

    async def process_fill_info(
        self, debtor_iin: str, debtor_phone_number: str = ""
    ) -> None:
        """
        Third step of the process.
        """
        pass

    async def process_set_payment(
        self,
        debt_sum: str,
        state_duty_sum: str,
        payment: str = None,
        is_online: bool = False,
    ) -> None:
        """
        The fourth step of the process.
        """
        await self.set_payment.set_payment(
            self.tab, debt_sum, state_duty_sum, payment, is_online=is_online
        )
        await self.set_payment.goto_next_page(self.tab)

    async def process_upload_files(self, files: list[str]) -> None:
        """
        The fifth step of the process.
        """
        pass

    async def process_signing(self) -> None:
        """
        The final step of the process.
        """
        pass
