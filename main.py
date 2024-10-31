import os
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException
from googleapiclient.http import MediaIoBaseDownload
from gdrive.gdrive_service import get_drive_service

project_root = Path(__file__).resolve().parent

CREDENTIALS_FILE = f"{project_root}/credentials.json" # путь до файлика с кредами, который генерится в Google Cloud
FILE_ID = "FILE ID ON G-DRIVE" # айди файла на гугл доке


def download_file():
    """"
        Функция для загрузки файлика .docx (это как пример) по его ID с Google Drive
    """

    drive_service = get_drive_service(cred_file_path=CREDENTIALS_FILE)
    try:
        # Создаем двоичный поток для скачивания
        file_stream = BytesIO()
        request = drive_service.files().get_media(fileId=FILE_ID)
        downloader = MediaIoBaseDownload(file_stream, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Перематываем на начало потока для чтения и получаем имя файла
        file_stream.seek(0)
        file_info = drive_service.files().get(fileId=FILE_ID, fields="name, mimeType").execute()
        file_name = file_info.get("name", "downloaded_file")

        # Проверяем, что файл ИМЕННО типа .docx
        if file_info.get("mimeType") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            if not file_name.endswith(".docx"):
                file_name += ".docx"
        else:
            return {"status": "Unsupported file type", "mime_type": file_info.get("mimeType")}

        # Сохраняем файл в корень проекта
        save_path = os.path.join(os.getcwd(), file_name)
        with open(save_path, "wb") as f:
            f.write(file_stream.read())

        return {"status": "File saved", "file_path": save_path}

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Ошибка при скачивании файла, {error}")


if __name__ == "__main__":
    print(download_file())
