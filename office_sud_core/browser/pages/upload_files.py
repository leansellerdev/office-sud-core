import asyncio

from loguru import logger
from pydoll.browser.tab import Tab
from pydoll.constants import By
from pydoll.elements.web_element import WebElement

from office_sud_core.browser.constants.selectors import (
    CommonSelectors,
    UploadFilesPageSelectors,
)
from office_sud_core.browser.pages.base import OfficeSudBase
from office_sud_core.exceptions import StatementError
from office_sud_core.models import SetupParams


class UploadFilesPage(OfficeSudBase):
    selectors = UploadFilesPageSelectors

    def __init__(self, params: SetupParams) -> None:
        super().__init__()
        self.PAGE_URL = self.BASE_URL + "form/requestType2/blankData"
        self.params = params

        self.text_paste_interval = 0.005

    async def goto_next_page(self, tab: Tab, timeout: float = 60) -> None:
        """
        Proceed to the next step from the file upload page.
        """
        await self._goto_next_page(
            tab, button=self.selectors.GONEXT_BUTTON, timeout=timeout
        )

    async def set_files(self, tab: Tab, files: list) -> None:
        """
        Upload statement file and supporting documents to their respective inputs.
        Raises StatementError if the portal rejects a file type.
        :param tab: active browser tab
        :param files: list of absolute file paths to upload
        """
        logger.info("Страница загрузки файлов")

        await self.wait_page(tab, self.PAGE_URL)
        logger.info("Files to upload: {files}".format(files=files))

        await self._upload_files(
            tab,
            self.selectors.STATEMENT_UPLOAD_INPUT,
            [file for file in files if "Исковое_Заявление" in file],
        )
        await self._upload_files(
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

    async def fill_base_requirements(self, tab: Tab) -> None:
        """
        Fill the base and additional requirements text fields from the config.
        """
        await self._set_text(
            tab,
            self.selectors.BASE_REQ_FIELD,
            self.params.upload_files_page_params.base_req,
            interval=self.text_paste_interval,
        )
        await self._set_text(
            tab,
            self.selectors.ADDITIONAL_REQ_FIELD,
            self.params.upload_files_page_params.additional_req,
            interval=self.text_paste_interval,
        )

    async def fill_agreement_info(
        self,
        tab: Tab,
        agreement_date: str,
        term_date: str,
        loan_sum: str,
        termination_info: str,
        violation_info: str,
        pretrial_results: str,
        statement_requirements: list[str],
    ) -> None:
        """
        Fill loan agreement details and add individual statement requirements.
        :param tab: active browser tab
        :param agreement_date: contract conclusion date (DD.MM.YYYY)
        :param term_date: repayment deadline date (DD.MM.YYYY)
        :param loan_sum: loan principal amount as a string
        :param termination_info: description of termination grounds
        :param violation_info: description of the obligation violation
        :param pretrial_results: summary of pretrial settlement attempts
        :param statement_requirements: list of claim requirement strings to add one by one
        """
        contract_date_input: WebElement = await tab.find_or_wait_element(
            By.XPATH, self.selectors.CONTRACT_DATE_INPUT, timeout=10
        )
        await contract_date_input.type_text(agreement_date)
        term_date_input: WebElement = await tab.find_or_wait_element(
            By.XPATH, self.selectors.TERM_DATE_INPUT, timeout=10
        )
        await term_date_input.type_text(term_date)

        await self._set_text(tab, self.selectors.LOAN_SUM_INPUT, loan_sum)
        await self._set_text(
            tab,
            self.selectors.TERMINATION_INFO_INPUT,
            termination_info,
            interval=self.text_paste_interval,
        )
        await self._set_text(
            tab,
            self.selectors.VIOLATION_INFO_INPUT,
            violation_info,
            interval=self.text_paste_interval,
        )
        await self._set_text(
            tab,
            self.selectors.PRETRIAL_RESULTS_INPUT,
            pretrial_results,
            interval=self.text_paste_interval,
        )

        for statement_requirement in statement_requirements:
            await self._add_statement_requirement(tab, statement_requirement)
            await asyncio.sleep(1)

    async def _add_statement_requirement(
        self, tab: Tab, statement_requirement: str
    ) -> None:
        statement_req_button: WebElement = await tab.find_or_wait_element(
            By.XPATH, self.selectors.STATEMENT_REQ_BUTTON, timeout=10
        )
        await statement_req_button.click()
        await asyncio.sleep(1)

        await self._set_text(
            tab,
            self.selectors.STATEMENT_REQ_TEXTFIELD,
            statement_requirement,
        )
