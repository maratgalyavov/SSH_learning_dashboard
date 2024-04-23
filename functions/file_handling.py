import logging
import os

async def upload_file(ssh_client, local_path, remote_path):
    try:
        if os.path.exists(local_path):
            logging.info(f"Confirmed that {local_path} exists. Proceeding with upload.")
        else:
            return f"Error: File {local_path} was not found locally."

        sftp = ssh_client.open_sftp()
        logging.info(f"Uploading {local_path} to {remote_path}")
        sftp.put(local_path, remote_path)
        sftp.close()
        return "Файл успешно загружен."
    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError: {e}")
        return f"Ошибка при загрузке файла: Локальный файл не найден - {e}"
    except Exception as e:
        logging.error(f"Exception in upload_file: {e}")
        return f"Ошибка при загрузке файла: {e}"




async def download_file(ssh_client, remote_path, local_path):
    try:
        sftp = ssh_client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        return "Файл успешно скачан."
    except Exception as e:
        return f"Ошибка при скачивании файла: {e}"