from datetime import datetime, timedelta

import pyautogui
from loguru import logger
from pywinauto import (
    Application,
    ElementNotFoundError,
    WindowNotFoundError,
    WindowSpecification,
    keyboard,
)
from pywinauto.application import ProcessNotFoundError

from settings import IMAGES_DIR, nca_layer_path, open_jdk_path


class Desktop:
    def __init__(self) -> None:
        self.logger = logger
        self.app = Application()

    def _check_if_started(self, path) -> bool:
        try:
            self.app.connect(path=path)
            return True
        except ProcessNotFoundError:
            return False

    def set_window_focus(self, app_path: str, title: str) -> WindowSpecification | None:
        if not self._check_if_started(app_path):
            self.logger.error(f"Process not started: {app_path.split('/')[-1]}")
            return

        self.app.connect(path=app_path)
        window = self.app.window(title=title)

        window.set_focus()
        return window


class NCALayer(Desktop):
    def __init__(self) -> None:
        super().__init__()

    def start(self) -> None:
        if not self._check_if_started(nca_layer_path) or not self._check_if_started(
            open_jdk_path
        ):
            self.app.start(nca_layer_path)
            self.logger.info("NCALayer запущен.")

            return

        self.logger.warning("NCALayer уже запущен!")

    def close(self) -> None:
        if not self._check_if_started(open_jdk_path):
            return

        self.app.kill()

    async def choose_key(self, nca_path: str, password: str, /, timeout: int = 10):
        key_list_window = await self._wait_window_to_appear(
            "Список ключей", open_jdk_path, timeout=timeout, raise_exc=False
        )
        if key_list_window is not None:
            continue_button = pyautogui.locateOnScreen(
                str(IMAGES_DIR / "continue.png"), minSearchTime=5
            )
            if continue_button:
                center = pyautogui.center(continue_button)  # type: ignore
                pyautogui.click(center)
        else:
            await self._wait_window_to_appear(
                "Открыть файл", open_jdk_path, timeout=timeout
            )
            keyboard.send_keys(nca_path, pause=0)
            keyboard.send_keys("{ENTER}")

        await self._wait_window_to_appear(
            "Формирование ЭЦП в формате XML", open_jdk_path, timeout=timeout
        )
        keyboard.send_keys(password, pause=0)
        keyboard.send_keys("{ENTER 2}", pause=1)

    async def _wait_window_to_appear(
        self,
        window_title: str,
        window_path: str,
        timeout: float,
        raise_exc: bool = True,
    ) -> WindowSpecification | None:
        logger.info(f"Ждем появление окна {window_title}")
        success = False

        start_time = datetime.now()

        while not success:
            if datetime.now() > start_time + timedelta(seconds=timeout):
                if raise_exc:
                    raise WindowNotFoundError()
                else:
                    return None
            try:
                window = self.set_window_focus(app_path=window_path, title=window_title)
                return window
            except ElementNotFoundError:
                continue
