import asyncio

from loguru import logger
from pydoll.browser.tab import Tab
from pydoll.constants import By
from pydoll.exceptions import ElementNotVisible

from core.browser.constants.selectors import FillInfoPageSelectors
from core.browser.pages.base import OfficeSudBase
from core.models import SetupParams
from core.types import ParticipantSide, Dialog


class FillInfoPage(OfficeSudBase):
    selectors = FillInfoPageSelectors

    def __init__(self, params: SetupParams) -> None:
        super().__init__()
        self.PAGE_URL = self.BASE_URL + "form/requestType2/createRequest.xhtml"
        self.params = params

    async def fill_statement_info(self, tab: Tab) -> None:
        logger.info("Страница заполнения данных")
        await self.wait_page(tab, self.PAGE_URL)

        if self.params.type == "statement":
            await self._select_option(tab, self.selectors.CATEGORY_GROUP_SELECT,
                                      self.params.fill_info_page_params.cat_group)

        # Категория дела
        await self._select_option(tab, self.selectors.CATEGORY_SELECT, self.params.fill_info_page_params.cat)
        # Характер заявления
        await self._select_option(tab, self.selectors.CHARACTER_SELECT,
                                  self.params.fill_info_page_params.statement_character)

        # Область
        await self._select_option(tab, self.selectors.CITY_SELECT, self.params.fill_info_page_params.district)
        # Судебный орган
        await self._select_option(tab, self.selectors.COURT_SELECT, self.params.fill_info_page_params.court)

    async def add_participant(self, tab: Tab, _type: int, side: int) -> None:
        """
        :param tab:
        :param _type: int 1 or 2 (1 - физ лицо, 2 - юр лицо)
        :param side: int (1 - взыскатель, 2 - должник, 7 - третья сторона, 4 - заявитель, 5 - представитель)
        :return:
        """
        if side not in ParticipantSide.sides:
            raise AttributeError("Attribute side must be in (1, 2, 7, 4, 5)")
        try:
            add_participant_button = await tab.find_or_wait_element(
                By.CSS_SELECTOR, self.selectors.ADD_PARTICIPANT_BUTTON, timeout=10
            )
            await add_participant_button.click()
            await asyncio.sleep(3)

            if _type == 1:
                await self._select_option(tab, self.selectors.PARTICIPANT_TYPE_SELECT, "false")
            else:
                await self._select_option(tab, self.selectors.PARTICIPANT_TYPE_SELECT, "true")

            await self._select_option(tab, self.selectors.PARTICIPANT_SIDE_SELECT, str(side))
            goto_button = await tab.find_or_wait_element(
                By.XPATH, self.selectors.PARTICIPANT_GOTO_BUTTON
            )
            await goto_button.click()
        except (ElementNotVisible, TimeoutError):
            await self.add_participant(tab, _type, side)
        else:
            return

    async def fill_jur_data(self, tab: Tab) -> None:
        await asyncio.sleep(1)
        await self._set_text(tab, self.selectors.ORG_BIN, self.params.fill_info_page_params.org_bin)

        org_search_button = await tab.find_or_wait_element(
            By.XPATH, self.selectors.ORG_SEARCH_BUTTON
        )
        await org_search_button.click()
        await asyncio.sleep(1)

        await self._set_text(tab, self.selectors.ORG_FACT_ADDRESS, self.params.fill_info_page_params.org_address)
        if self.params.fill_info_page_params.org_requisites:
            await self._set_text(tab, self.selectors.ORG_BANK_DETAILS, self.params.fill_info_page_params.org_requisites)

        save_button = await tab.find_or_wait_element(
            By.XPATH, self.selectors.JUR_SAVE_BUTTON
        )
        await save_button.click()
        await asyncio.sleep(3)

    async def fill_fiz_data(self, tab: Tab, *, iin: str, phone_number: str) -> None:
        await self._set_text(tab, self.selectors.PERSON_IIN, str(iin))

        person_search_button = await tab.find_or_wait_element(
            By.XPATH, self.selectors.PERSON_SEARCH_BUTTON, timeout=2
        )
        await person_search_button.click()
        await asyncio.sleep(1)

        if "+7" in phone_number:
            phone_number = phone_number.replace("+7", "")
        await self._set_text(tab, self.selectors.PERSON_PHONE, phone_number)

        save_button = await tab.find_or_wait_element(
            By.XPATH, self.selectors.FIZ_SAVE_BUTTON
        )
        async with asyncio.timeout(10):
            while True:
                if await save_button.is_visible():
                    await save_button.click()
                else:
                    break

        await self._goto_next_page(tab, self.selectors.GONEXT_BUTTON)

    async def select_dialog_values(self, tab: Tab, dialogs: list[Dialog]) -> None:
        for dialog in dialogs:
            await self.select_dialog_value(tab, dialog_text=dialog.text, dialog_value=dialog.value, sleep_time=2)

    async def select_dialog_value(self, tab: Tab, dialog_text: str, dialog_value: bool, sleep_time: float = None) -> None:
        dialog_value = 'true' if dialog_value else 'false'
        dialog_elements = await tab.find_or_wait_element(
            By.XPATH, self.selectors.MODAL_DIALOG_PANEL, find_all=True
        )
        if not dialog_elements:
            pass
        for dialog_element in dialog_elements:
            if await dialog_element.is_visible():
                dialog_element_text = await (
                    await dialog_element.find_or_wait_element(By.TAG_NAME, "p")
                ).text
                if dialog_text.lower() in dialog_element_text.lower():
                    quest_block = await dialog_element.find_or_wait_element(
                        By.CLASS_NAME, self.selectors.QUEST_BLOCK_CONTAINER_CLASS
                    )
                    needed_input = await quest_block.find_or_wait_element(
                        By.XPATH, self.selectors.DIALOG_VALUE.format(dialog_value=dialog_value)
                    )
                    await needed_input.click()
                    break

        await asyncio.sleep(1)

        submit_buttons = await tab.find_or_wait_element(
            By.XPATH,
            self.selectors.NEXT_QUEST_BUTTONS,
            timeout=10,
            find_all=True
        )
        for submit_button in submit_buttons:
            if await submit_button.is_visible():
                await submit_button.click()

            break

        if sleep_time:
            await asyncio.sleep(sleep_time)

    async def goto_next_page(self, tab: Tab, /, timeout: float = 60) -> None:
        await self._goto_next_page(tab, timeout=timeout, button=self.selectors.GONEXT_BUTTON)

    async def trigger_constructor(self, tab: Tab) -> None:
        gonext_button = await tab.find_or_wait_element(
            By.XPATH, self.selectors.TRIGGER_CONSTRUCTOR_BUTTON, timeout=5
        )
        await gonext_button.click()
        await asyncio.sleep(3)

    # TODO: универсальный метод для указания данных в зависимости от типа участника (юр./физ. лицо)
    async def fill_participant_data(self, tab: Tab, *, _type: int) -> None:
        pass
