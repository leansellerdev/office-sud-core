import asyncio

from loguru import logger
from pydoll.browser.tab import Tab

from office_sud_core.browser.constants.selectors import SelectOptionSelectors
from office_sud_core.browser.pages.base import OfficeSudBase
from office_sud_core.models import SetupParams


class SelectOptionsPage(OfficeSudBase):
    CASE_TYPE = "CIVIL"
    INSTANCE = "FIRSTINSTANCE"
    DOC_TYPE = "12"

    selectors = SelectOptionSelectors

    def __init__(self, params: SetupParams) -> None:
        super().__init__()
        self.PAGE_URL = self.BASE_URL + "form/send/index.xhtml"
        self.params = params

    async def goto_page(self, tab: Tab) -> None:
        """
        Navigate to the case submission options page.
        """
        logger.info("Страница выбора опций")
        await tab.go_to(self.PAGE_URL)
        await self.wait_page(tab, self.PAGE_URL)

    async def select_options(self, tab: Tab) -> None:
        """
        Select case type, court instance, and document type from the config, then proceed.
        """
        # Тип производства
        await self._select_option(
            tab,
            self.selectors.CASE_TYPE_SELECT,
            self.params.select_options_page_params.case_type,
        )
        # Инстанция
        await self._select_option(
            tab,
            self.selectors.INSTANCE_SELECT,
            self.params.select_options_page_params.instance,
        )
        # Тип документа
        await asyncio.sleep(5)
        await self._select_option(
            tab,
            self.selectors.DOC_TYPE_SELECT,
            self.params.select_options_page_params.doc_type,
        )

        await self._goto_next_page(tab, self.selectors.GONEXT_BUTTON)
