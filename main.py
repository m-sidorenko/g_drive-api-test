import os
from io import BytesIO
from pathlib import Path
import io

from fastapi import HTTPException
from googleapiclient.http import MediaIoBaseDownload
from gdrive.gdrive_service import get_drive_service

project_root = Path(__file__).resolve().parent

CREDENTIALS_FILE = f"{project_root}/credentials.json" # путь до файлика с кредами, который генерится в Google Cloud
masterpaln_file_id = "" # id masterplan


def download_file(file_id):
    """"
        Функция для загрузки файлика .docx (это как пример) по его ID с Google Drive
    """

    drive_service = get_drive_service(cred_file_path=CREDENTIALS_FILE)
    try:
        # Создаем двоичный поток для скачивания
        file_stream = BytesIO()
        request = drive_service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(file_stream, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        # Перематываем на начало потока для чтения и получаем имя файла
        file_stream.seek(0)
        file_info = drive_service.files().get(fileId=file_id, fields="name, mimeType").execute()
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


def download_fileV2(file_id, file_name):
    """
    Скачивание файла с гугл драйв
    :param file_id: ID файла, который необходимо скачать;
    :param file_name: имя файла (С РАСШИРЕНИЕМ), которое будет использовано при сохранении файла в корень проекта
    :return:
    """
    try:
        request = get_drive_service(cred_file_path=CREDENTIALS_FILE).files().export_media(
            fileId=file_id,
            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        fh = io.FileIO(file_name, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
    except Exception as e:
        print(f"An error occurred: {e}")

    print("FILE HAS BEEN DOWNLOADED")

if __name__ == "__main__":
    download_fileV2(masterpaln_file_id, "test_excel.xlsx")
