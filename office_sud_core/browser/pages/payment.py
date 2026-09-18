import asyncio

from loguru import logger
from pydoll.browser.tab import Tab
from pydoll.constants import By
from pydoll.elements.web_element import WebElement

from office_sud_core.browser.constants.selectors import PaymentPageSelectors
from office_sud_core.browser.pages.base import OfficeSudBase
from office_sud_core.models.setup import SetupParams


class PaymentPage(OfficeSudBase):
    KBK_TYPE = "1"
    selectors = PaymentPageSelectors

    def __init__(self, params: SetupParams) -> None:
        super().__init__()
        self.PAGE_URL = self.BASE_URL + "form/requestType2/payment.xhtml"
        self.params = params

    async def set_payment(
        self,
        tab: Tab,
        debt_sum: str,
        state_duty_sum: str,
        payment: str = None,
        *,
        is_online: bool = False,
    ) -> str | None:
        """
        Configure payment: upload the receipt (offline) or initiate online payment, fill amounts, select KBK.
        :param tab: active browser tab
        :param debt_sum: total debt amount as a string
        :param state_duty_sum: state duty amount as a string
        :param payment: path to the offline payment receipt file; ignored when is_online=True
        :param is_online: if True, use online payment flow and return the payment code
        :return: payment code string when is_online=True, None otherwise
        """
        logger.info("Страница с платежом")
        try:
            await self.wait_page(tab, self.PAGE_URL)

            if not is_online:
                await self._upload_files(
                    tab, self.selectors.FILE_UPLOAD_INPUT, [payment]
                )

            await self._fill_payment(tab, debt_sum, state_duty_sum)

            await self._select_option(
                tab,
                self.selectors.KBK_SELECT,
                self.params.payment_page_params.kbk,
            )
            if is_online:
                payment_code = await self.online_payment(tab)
                await self.wait_page(tab, self.PAGE_URL)

                return payment_code

        except TimeoutError:
            logger.warning(
                "Не удалось загрузить файл с помощью инпута. Пробуем через кнопку..."
            )
            await tab.refresh()
            await self.set_payment_with_button(tab, debt_sum, state_duty_sum, payment)

    async def set_payment_with_button(
        self, tab, debt_sum: str, state_duty_sum: str, payment: str
    ) -> None:
        """
        Fallback payment setup using the native file dialog button instead of the file input.
        Used when the file input element is unavailable after a page refresh.
        :param tab: active browser tab
        :param debt_sum: total debt amount as a string
        :param state_duty_sum: state duty amount as a string
        :param payment: path to the offline payment receipt file
        """
        await asyncio.sleep(3)

        await self.upload_file_with_button(
            tab, self.selectors.FILE_UPLOAD_BUTTON, payment
        )

        await self._set_text(tab, self.selectors.DEBT_SUM_FIELD, debt_sum)
        await self._set_text(tab, self.selectors.STATE_DUTY_SUM_FIELD, state_duty_sum)

    async def online_payment(self, tab: Tab) -> str:
        """
        Initiate online payment flow, extract the payment code, then confirm payment.
        :return: payment code string from the payment gateway
        """
        online_checkbox = await self._find_online_checkbox(tab)
        checked = True if online_checkbox.get_attribute("checked") else False
        if checked:
            await online_checkbox.click()
            await asyncio.sleep(1)

        payment_button = await tab.find_or_wait_element(
            By.XPATH, self.selectors.ONLINE_PAY_BUTTON, timeout=10
        )
        await payment_button.click()
        await self.wait_page(tab, "Pages/Sud/Payment.aspx")

        payment_code = await (
            await tab.find_or_wait_element(
                By.ID, self.selectors.PAYMENT_CODE_ID, timeout=10
            )
        ).text
        await self.go_back(tab)

        online_checkbox = await self._find_online_checkbox(tab)
        await online_checkbox.click()
        await asyncio.sleep(2)
        await online_checkbox.click()

        check_payment_button = await tab.find_or_wait_element(
            By.XPATH, self.selectors.CHECK_PAYMENT_BUTTON, timeout=10
        )
        await check_payment_button.click()

        return payment_code

    async def goto_next_page(self, tab: Tab, timeout: float = 60) -> None:
        """
        Proceed to the next step from the payment page.
        """
        await self._goto_next_page(
            tab, button=self.selectors.GONEXT_BUTTON, timeout=timeout
        )

    async def _find_online_checkbox(self, tab) -> WebElement:
        online_checkbox = await tab.find_or_wait_element(
            By.XPATH, self.selectors.IS_ONLINE_PAY_CHECKBOX, timeout=10
        )
        return online_checkbox

    async def _fill_payment(self, tab: Tab, debt_sum: str, state_duty_sum: str) -> None:
        await self._set_text(tab, self.selectors.DEBT_SUM_FIELD, str(debt_sum))
        await self._set_text(
            tab, self.selectors.STATE_DUTY_SUM_FIELD, str(state_duty_sum)
        )
