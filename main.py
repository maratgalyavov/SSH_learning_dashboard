import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.dispatcher.router import Router
from aiogram.enums import ContentType
from aiogram.filters import Command
import paramiko
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InputFile, FSInputFile

API_TOKEN = '6845365315:AAEjLspSJ7X8wQot7NnE3zO27y20Mxscfqg'

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
router = Router()

# SSH client
ssh_client = None

class CommandState(StatesGroup):
    waiting_for_command = State()

# Helper functions
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


async def submit_job(ssh_client, job_script):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(f'sbatch {job_script}')
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        return output or error or "Задача отправлена на выполнение."
    except Exception as e:
        return f"Ошибка при отправке задачи: {e}"


async def show_queue(ssh_client):
    try:
        stdin, stdout, stderr = ssh_client.exec_command('squeue')
        output = stdout.read().decode('utf-8').strip()
        return output or "Очередь задач пуста."
    except Exception as e:
        return f"Ошибка при просмотре очереди задач: {e}"


async def cancel_job(ssh_client, job_id):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(f'scancel {job_id}')
        output = stdout.read().decode('utf-8').strip()
        return output or "Задача отменена."
    except Exception as e:
        return f"Ошибка при отмене задачи: {e}"


# Commands
@router.message(Command(commands=['start', 'help']))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для SSH подключения.\n\n"
                         "Доступные команды:\n"
                         "/connect - Подключиться к серверу\n"
                         "/disconnect - Отключиться от сервера\n"
                         "/execute - Выполнить команду на сервере\n"
                         "/upload - Загрузить файл на сервер\n"
                         "/download - Скачать файл с сервера\n"
                         "/submit_job - Отправить задачу на выполнение\n"
                         "/show_queue - Просмотр очереди задач\n"
                         "/cancel_job - Отменить задачу")


@router.message(Command(commands=['connect']))
async def connect_ssh(message: types.Message):
    await message.answer("Введите данные для подключения в формате: host username password, port(опционально)")


@router.message(lambda message: message.text and ' ' in message.text and ssh_client is None)
async def process_connect_command(message: types.Message):
    global ssh_client
    try:
        parts = message.text.split(' ', 3)
        host, username, password = parts[:3]
        port = int(parts[3]) if len(parts) > 3 else 22
    except ValueError:
        await message.answer("Неверный формат. Пожалуйста, используйте формат: host username password [port]")
        return

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(hostname=host, username=username, password=password, port=port)
        await message.answer("Успешное подключение к серверу.")
    except Exception as e:
        await message.answer(f"Ошибка подключения: {e}")


@router.message(Command(commands=['disconnect']))
async def disconnect_ssh(message: types.Message):
    global ssh_client
    if ssh_client:
        ssh_client.close()
        ssh_client = None
        await message.answer("Отключение от сервера выполнено.")
    else:
        await message.answer("Соединение не установлено.")


@router.message(Command(commands=['execute']))
async def execute_command(message: types.Message, state: FSMContext):
    global ssh_client
    if not ssh_client:
        await message.answer("Сначала подключитесь к серверу.")
        return
    await state.set_state(CommandState.waiting_for_command)
    await message.answer("Введите команду для выполнения:")


@router.message(CommandState.waiting_for_command)
async def process_execute_command(message: types.Message, state: FSMContext):
    if message.text.startswith('/'):
        await message.answer("Looks like you entered a bot command. If you want to execute an SSH command, please don't start with '/'.")
        return

    command = message.text
    await state.clear()

    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        response = output or error or "Нет вывода"
        await message.answer(response)
    except Exception as e:
        await message.answer(f"Ошибка выполнения команды: {e}")



@router.message(Command(commands=['upload']))
async def upload_file_command(message: types.Message):
    if not ssh_client:
        await message.answer("Сначала подключитесь к серверу.")
        return
    await message.answer("Отправьте файл который хотите загрузить")


import logging


@router.message(F.document)
async def process_upload_file_command(message: Message):
    document = message.document
    file_id = document.file_id
    file_name = document.file_name
    file_path = f'./downloads/{file_name}'

    logging.info(f"Received document with file_id: {file_id}")
    logging.info(f"Local file path: {file_path}")

    try:
        os.makedirs('./downloads', exist_ok=True)
        logging.info(f"Ensured that the downloads directory exists.")

        file = await bot.get_file(file_id)
        file_path_telegram = file.file_path
        logging.info(f"File path on Telegram servers: {file_path_telegram}")

        await bot.download_file(file_path_telegram, destination=file_path)
        logging.info(f"File downloaded locally to {file_path}")

        if os.path.exists(file_path):
            logging.info(f"File {file_name} exists, ready to upload.")
            remote_path = f'{file_name}'  # Modify as needed
            response = await upload_file(ssh_client, file_path, remote_path)
            logging.info(f"File uploaded to remote server at path: {remote_path}")
        else:
            response = f"Error: File {file_name} was not found locally after download."
            logging.error(response)

    except Exception as e:
        response = f"An error occurred: {e}"
        logging.error(response)

    await message.answer(response)


@router.message(Command(commands=['download']))
async def download_file_command(message: types.Message):
    if not ssh_client:
        await message.answer("Сначала подключитесь к серверу.")
        return
    await message.answer("Введите путь к файлу на сервере, который хотите скачать:")


@router.message(lambda message: message.text and not message.text.startswith('/') and ssh_client is not None)
async def process_download_file_command(message: types.Message):
    remote_file_path = message.text
    local_file_path = f'./downloads/{remote_file_path.split("/")[-1]}'

    os.makedirs('./downloads', exist_ok=True)

    response = await download_file(ssh_client, remote_file_path, local_file_path)
    if "успешно" in response:
        document = FSInputFile(local_file_path)
        await bot.send_document(message.from_user.id, document=document)
    else:
        await message.answer(response)


@router.message(Command(commands=['submit_job']))
async def submit_job_command(message: types.Message):
    if not ssh_client:
        await message.answer("Сначала подключитесь к серверу.")
        return
    await message.answer("Введите путь к скрипту задачи на сервере:")


@router.message(lambda message: message.text and not message.text.startswith('/') and ssh_client is not None)
async def process_submit_job_command(message: types.Message):
    job_script_path = message.text
    response = await submit_job(ssh_client, job_script_path)
    await message.answer(response)


@router.message(Command(commands=['show_queue']))
async def show_queue_command(message: types.Message):
    if not ssh_client:
        await message.answer("Сначала подключитесь к серверу.")
        return
    response = await show_queue(ssh_client)
    max_length = 4000
    if len(response) > max_length:
        response = response[:max_length] + "\n... (output truncated)"
    await message.answer(response)


@router.message(Command(commands=['cancel_job']))
async def cancel_job_command(message: types.Message):
    if not ssh_client:
        await message.answer("Сначала подключитесь к серверу.")
        return
    job_id = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None
    if job_id:
        response = await cancel_job(ssh_client, job_id)
        await message.answer(response)
    else:
        await message.answer("Пожалуйста, укажите ID задачи. Формат: /cancel_job [job_id]")


dispatcher = Dispatcher()
dispatcher.include_router(router)

if __name__ == '__main__':
    asyncio.run(dispatcher.start_polling(bot))
