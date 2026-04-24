import os
from pathlib import Path

DEBUG = True

PATH = Path(__file__).resolve().parent
CONFIGS = PATH / "configs"

TG_BOT_TOKEN = "7471120443:AAG-JD6F77s_ENR0TztsBpuDhYsPqNInDMU"

LOG_FILE_PATH = PATH / "app.log"

IMAGES_DIR = PATH / "core/desktop/images"

APPDATA = os.getenv("APPDATA")

nca_layer_path = os.path.join(APPDATA, r"NCALayer\NCALayer.exe")
open_jdk_path = os.path.join(APPDATA, r"NCALayer\jre\bin\javaw.exe")

PROJECT_NAME = "office-sud-automate"
