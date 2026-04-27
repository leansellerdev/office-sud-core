import asyncio

from loguru import logger
from pydoll.browser.tab import Tab
from pydoll.constants import By
from pydoll.exceptions import ElementNotFound

from office_sud_core.browser.constants.selectors import LoginPageSelectors
from office_sud_core.browser.pages.base import OfficeSudBase
from office_sud_core.models import SetupParams


class LoginPage(OfficeSudBase):
    selectors = LoginPageSelectors

    def __init__(self, params: SetupParams) -> None:
        super().__init__()
        self.params = params
        self._MAIN_PAGE_URL = self.BASE_URL + "form/proceedings/services.xhtml"

    @staticmethod
    async def change_language(tab: Tab) -> None:
        language_changed = False
        button = await tab.find_or_wait_element(
            By.CSS_SELECTOR, LoginPageSelectors.LANGUAGE
        )

        while not language_changed:
            try:
                await button.click()
            except ElementNotFound:
                pass
            else:
                language_changed = True

        logger.info("Язык изменен")

    async def creds_login(self, tab: Tab) -> None:
        iin_field = await tab.find_or_wait_element(
            By.XPATH, self.selectors.IIN_FIELD_LOGIN
        )
        password_field = await tab.find_or_wait_element(
            By.XPATH, self.selectors.PASSWORD_FIELD_LOGIN
        )
        login_button = await tab.find_or_wait_element(
            By.XPATH, self.selectors.LOGIN_BUTTON
        )

        await iin_field.click()
        await iin_field.insert_text(self.params.auth_params.bin)

        await password_field.click()
        await password_field.insert_text(self.params.auth_params.password)

        await asyncio.sleep(2)
        await login_button.click()

    async def nca_login(self, tab: Tab) -> None:
        logger.info("Страница логина")
        self.nca_layer.start()

        await tab.go_to(self._SUD_URL, timeout=60)
        if await tab.current_url == self._MAIN_PAGE_URL:
            return

        await self.change_language(tab)
        await asyncio.sleep(3)

        # await self.creds_login(tab)
        await self.select_eds(
            tab,
            nca_path=str(self.params.auth_params.nca_path),
            password=self.params.auth_params.nca_password,
        )
