import os
import shutil
import tempfile

from loguru import logger


def delete_temp_dirs() -> None:
    temp_path = tempfile.gettempdir()

    for _file in os.listdir(temp_path):
        if os.path.isdir(os.path.join(temp_path, _file)) and _file[:3] == "tmp":
            try:
                shutil.rmtree(os.path.join(temp_path, _file))
            except OSError:
                continue


def move_result_when_done(folder_name: str, result_dir_path: str) -> None:
    try:
        shutil.move(folder_name, result_dir_path)
    except shutil.Error:
        logger.warning(
            "Дело {folder_name} уже существует. Удаляем папку".format(
                folder_name=os.path.basename(folder_name)
            )
        )
        shutil.rmtree(folder_name)


def get_notification_code(case_path: str) -> str:
    files = os.listdir(case_path)
    for file in files:
        file_name = os.path.basename(file).replace(".pdf", "")
        if file_name.isdigit():
            return file.replace(".pdf", "")


def check_if_notification_exists(case_path: str) -> bool:
    files = os.listdir(case_path)
    for file in files:
        if "уведомление_об_отправке" in file or file.replace(".pdf", "").isdigit():
            return True

    return False
