import asyncio
from typing import Type

from loguru import logger
from pydoll.browser.tab import Tab
from pydoll.constants import By
from pydoll.exceptions import ElementNotFound, ElementNotVisible, WaitElementTimeout
from pywinauto import keyboard

from core.browser.constants import scripts
from core.browser.constants.selectors import (
    BaseSelectors,
    CommonSelectors,
    LoginPageSelectors,
)
from core.desktop.nca_layer import NCALayer


class OfficeSudBase:
    selectors: Type[BaseSelectors] = BaseSelectors

    def __init__(self) -> None:
        self.BASE_URL = "https://office.sud.kz/"
        self._SUD_URL = self.BASE_URL + "new/index.xhtml"
        self.PAGE_URL = ""

        self.nca_layer = NCALayer()

    async def goto_page(self, tab: Tab) -> None:
        pass

    async def wait_page(self, tab: Tab, page_url: str, *, timeout: int = 30) -> None:
        async with asyncio.timeout(timeout):
            while True:
                if page_url not in await tab.current_url:
                    continue

                return

    async def _goto_next_page(
        self, tab: Tab, /, button: str, timeout: float = 60
    ) -> None:
        is_next_page = False
        async with asyncio.timeout(timeout):
            while not is_next_page:
                try:
                    if self.PAGE_URL in await tab.current_url:
                        await self.scroll_down(tab)
                        go_next_button = await tab.find_or_wait_element(
                            By.XPATH, button
                        )
                        await go_next_button.click()
                        await asyncio.sleep(0.5)
                    else:
                        is_next_page = True
                except ElementNotVisible:
                    await asyncio.sleep(0.1)
                    continue
                except ElementNotFound:
                    return

    async def select_eds(self, tab: Tab, *, nca_path: str, password: str) -> None:
        clicked = False
        while not clicked:
            try:
                select_button = await tab.find_or_wait_element(
                    By.CSS_SELECTOR,
                    LoginPageSelectors.SELECT_EDS,
                    timeout=10,
                )
                await select_button.click()
            except (ElementNotVisible, KeyError):
                tab_eds = await tab.find_or_wait_element(By.ID, "tab-eds")
                await tab_eds.click()
            else:
                clicked = True

        await self.nca_layer.choose_key(nca_path, password)

    async def _select_option(
        self, tab: Tab, xpath: str, option: str, timeout: int = 10
    ) -> None:
        logger.debug(f"Trying to select {xpath}")
        selected = False

        async with asyncio.timeout(timeout * 2):
            while not selected:
                try:
                    select = await tab.find_or_wait_element(
                        By.XPATH,
                        xpath,
                        timeout=timeout,
                        find_all=True,
                    )
                    select_id = select[-1].get_attribute("id")
                    if await self._option_selected(tab, select_id, option):
                        return

                    _option = await select[-1].find_or_wait_element(
                        By.CSS_SELECTOR,
                        CommonSelectors.OPTION.format(option),
                        timeout=timeout,
                    )
                    await _option.click()
                    await asyncio.sleep(0.5)
                except WaitElementTimeout:
                    continue
                else:
                    logger.success(f"Selected {await _option.text}")
                    selected = True

    async def _set_text(
        self,
        tab: Tab,
        xpath: str,
        text: str,
        timeout: int = 30,
        interval: float = 0.01,
    ) -> None:
        logger.debug(f"Setting {text} to {xpath}")
        text_set = False

        async with asyncio.timeout(timeout):
            while not text_set:
                try:
                    _field = await tab.find_or_wait_element(
                        By.XPATH, xpath, timeout=timeout // 2
                    )
                    _field_id = _field.get_attribute("id")
                    _field_selector_type = "id"
                    if not _field_id:
                        _field_id = _field.get_attribute("name")
                        _field_selector_type = "name"
                    await _field.click()
                    await _field.type_text(text, interval=interval)
                    await asyncio.sleep(0.3)
                    if not await self._is_text_set(
                        tab,
                        field_selector=_field_id,
                        field_selector_type=_field_selector_type,
                        text=text,
                    ):
                        await _field.execute_script(
                            scripts.CLEAR_TEXT_FIELD.format(
                                input_id=CommonSelectors.INPUT.format(
                                    key=_field_selector_type, value=_field_id
                                )
                            )
                        )
                        continue
                except (WaitElementTimeout, ElementNotVisible):
                    continue
                else:
                    logger.success(f"{text} set to {xpath}")
                    text_set = True

    @staticmethod
    async def go_back(tab: Tab) -> None:
        await tab.execute_script("window.history.back()")

    @staticmethod
    async def scroll_down(tab: Tab) -> None:
        await tab.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(0.1)

    @staticmethod
    async def upload_file_with_button(
        tab: Tab, selector: str, file: str, timeout: int = 30
    ) -> None:
        logger.info(
            f"Загружаем файл с помощью проводника. Имя файла: {file.split('//')[-1]}"
        )
        input_button = await tab.find_or_wait_element(
            By.CSS_SELECTOR, selector, timeout=timeout
        )
        await input_button.click()

        await asyncio.sleep(3)

        keyboard.send_keys(file, pause=0)
        keyboard.send_keys("{ENTER}")

    @staticmethod
    async def _upload_files(
        tab: Tab, selector: str, files: list, timeout: int = 15
    ) -> None:
        logger.info(f"Загружаем файлы. Количество файлов: {len(files)}")
        input_element = await tab.find_or_wait_element(
            By.CSS_SELECTOR, selector, timeout=timeout
        )
        await input_element.set_input_files(files)

        await asyncio.sleep(0.5)

    @staticmethod
    async def _element_visible(
        tab: Tab, *, xpath: str = None, element_id: str = None
    ) -> bool:
        if xpath:
            result = await tab.execute_script(
                scripts.ELEMENT_VISIBLE_BY_XPATH.format(xpath=xpath)
            )
        else:
            result = await tab.execute_script(
                scripts.ELEMENT_VISIBLE_BY_ID.format(element_id=element_id)
            )

        return result["result"]["result"]["value"]

    @staticmethod
    async def _option_selected(tab: Tab, select_id: str, option: str) -> bool:
        result = await tab.execute_script(
            scripts.OPTION_SELECTED.format(
                select_id=CommonSelectors.SELECT.format(select_id),
                option=option,
            )
        )
        return result["result"]["result"]["value"]

    @staticmethod
    async def _is_text_set(
        tab: Tab, text: str, field_selector: str, field_selector_type: str = "id"
    ) -> bool:
        if "person-phone" in field_selector and text != "":
            return True

        result = await tab.execute_script(
            scripts.FIELD_TEXT.format(
                input_id=CommonSelectors.INPUT.format(
                    key=field_selector_type, value=field_selector
                ),
                text=text,
            )
        )

        return result["result"]["result"]["value"]
