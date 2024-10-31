import uuid
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from googleapiclient.errors import HttpError

from gdrive.gdrive_service import get_drive_service

project_root = Path(__file__).resolve().parent

CREDENTIALS_FILE = f"{project_root}/credentials.json" # путь до файлика с кредами, который генерится в Google Cloud
CHANNEL_ID = str(uuid.uuid4())  # Уникальный ID канала, оставляй таким
WEBHOOK_URL = "URL" # ссылка на NGROK или др URL, куда будет стучаться сервак гугла
FILE_ID = "FILE ID ON G-DRIVE" # айди файла на гугл доке

app = FastAPI()


@app.on_event("startup")
async def setup_hook():
    """"
        Настройка веб-хука
    """
    gdrive_service = get_drive_service(cred_file_path=CREDENTIALS_FILE)
    try:
        body = {
            "id":       CHANNEL_ID,
            "type":     "web_hook",
            "address":  WEBHOOK_URL
        }
        file_id = FILE_ID
        gdrive_service.files().watch(fileId=file_id, body=body).execute()

    except HttpError as error:
        print(f"Ошибка подписки на изменения файла: {error.content}")
        raise HTTPException(status_code=500, detail="Ошибка подписки на изменения файла")


@app.post("/webhook")
async def hook_processing(request: Request):
    """"
        Хендлер веб-хука, в котором приходит уведомление об обновлении файла
    """
    headers = request.headers
    state = headers.get("X-Goog-Resource-State")
    if state == "sync":
        print("got sync message!")
        return {"status": "Sync message"}

    else:
        print(f"got state:{state}!")


@app.post("/")
async def root():
    """"
        Корневой эндпоинт для отладки, а еще на него иногда стучится google cloud api сервак
    """
    print("root")
    return {"status": "Ignored"}