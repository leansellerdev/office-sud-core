import asyncio

from loguru import logger
from pydoll.browser.tab import Tab

from core.browser.constants.selectors import CommonSelectors, UploadFilesPageSelectors
from core.browser.pages.base import OfficeSudBase
from core.exceptions import StatementError
from core.models import SetupParams


# TODO: Сделать загрузку файлов через кнопку
class UploadFilesPage(OfficeSudBase):
    selectors = UploadFilesPageSelectors

    def __init__(self, params: SetupParams) -> None:
        super().__init__()
        self.PAGE_URL = self.BASE_URL + "form/requestType2/blankData/other.xhtml"
        self.params = params

    async def set_files(self, tab: Tab, files: list) -> None:
        logger.info("Страница загрузки файлов")

        await self.wait_page(tab, self.PAGE_URL)

        await self.fill_fields(tab)

        await self.upload_files(
            tab,
            self.selectors.STATEMENT_UPLOAD_INPUT,
            [file for file in files if "Исковое_Заявление" in file],
        )
        await self.upload_files(
            tab,
            self.selectors.FILE_UPLOAD_INPUT,
            [file for file in files if "Исковое_Заявление" not in file],
        )
        await asyncio.sleep(3)

        if await self._element_visible(
            tab,
            xpath=self.selectors.FILE_TYPE_REJECT,
        ):
            raise StatementError("Некорректный тип загружаемого файла")

        while True:
            if await self._element_visible(tab, xpath=CommonSelectors.LOADER):
                await asyncio.sleep(1)
                continue
            else:
                break

        await self.scroll_down(tab)

    async def fill_fields(self, tab: Tab) -> None:
        await self._set_text(tab, self.selectors.BASE_REQ_FIELD, self.params.upload_files_page_params.base_req,
                             interval=0.005)
        await self._set_text(tab, self.selectors.ADDITIONAL_REQ_FIELD,
                             self.params.upload_files_page_params.additional_req, interval=0.005)
