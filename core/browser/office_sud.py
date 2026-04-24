import asyncio

from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions
from pydoll.browser.tab import Tab
from pydoll.exceptions import WaitElementTimeout

from core.browser.pages import (
    FillInfoPage,
    LoginPage,
    PaymentPage,
    SelectOptionsPage,
    UploadFilesPage,
)
from core.browser.pages.signing import SigningPage
from core.models import SetupParams
from core.utils.utils import delete_temp_dirs
from core.utils.config import read_config
from core.types import ParticipantSide, ParticipantType
from settings import CONFIGS


class OfficeSud:
    def __init__(
        self,
        config: SetupParams,
        /,
        chrome_options: ChromiumOptions = None,
        download_dir: str = None,
        headless_browser: bool = False
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

    async def process_case(self) -> None:
        tab = await self._start_browser()

        await self.login.nca_login(tab)

        await self.select_options.goto_page(tab)
        await self.select_options.select_options(tab)

        await self.fill_info.fill_statement_info(tab)

        await self.fill_info.add_participant(
            tab, _type=ParticipantType.legal_entity, side=ParticipantSide.claimant
        )
        await self.fill_info.fill_jur_data(tab)

        try:
            await self.fill_info.add_participant(
                tab, _type=ParticipantType.individual, side=ParticipantSide.debtor
            )
            await self.fill_info.fill_fiz_data(tab, iin="001114501350", phone_number="")
        except WaitElementTimeout:
            await self.fill_info.add_participant(
                tab, _type=ParticipantType.individual, side=ParticipantSide.debtor
            )
            await self.fill_info.fill_fiz_data(tab, iin="001114501350", phone_number="")

        await self.fill_info.trigger_constructor(tab)
        await self.fill_info.select_dialog_value(
            tab, dialog_text="Договор нотариально удостоверен", dialog_value=False, sleep_time=2
        )
        await self.fill_info.select_dialog_value(
            tab, dialog_text="Подлинник письменной формы сделки", dialog_value=True, sleep_time=2
        )
        await self.fill_info.select_dialog_value(
            tab, dialog_text="Обращались ли Вы к нотариусу с данным вопросом", dialog_value=True, sleep_time=2
        )

    async def _start_browser(self) -> Tab:
        delete_temp_dirs()

        self.chrome = Chrome(options=self._chrome_options)
        if self._download_dir:
            await self.chrome.set_download_path(self._download_dir)

        tab = await self.chrome.start(headless=self._headless_browser)

        return tab


if __name__ == "__main__":
    config = read_config(CONFIGS / "lft.json")
    options = ChromiumOptions()
    options.binary_location = r"C:\Users\dd_27\AppData\Local\Google\Chrome\Application\chrome.exe"
    sud = OfficeSud(config, chrome_options=options)

    asyncio.run(sud.process_case())
