import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
import paramiko
import asyncio

API_TOKEN = '6845365315:AAEjLspSJ7X8wQot7NnE3zO27y20Mxscfqg'

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
router = Router()

# SSH client
ssh_client = None

@router.message(Command(commands=['start', 'help']))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для SSH подключения.\n\n"
                         "Доступные команды:\n"
                         "/connect - Подключиться к серверу\n"
                         "/disconnect - Отключиться от сервера\n"
                         "/execute - Выполнить команду на сервере")

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
async def execute_command(message: types.Message):
    global ssh_client
    if not ssh_client:
        await message.answer("Сначала подключитесь к серверу.")
        return

    await message.answer("Введите команду для выполнения:")

@router.message(lambda message: ssh_client is not None and message.text)
async def process_execute_command(message: types.Message):
    command = message.text

    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        response = output or error or "Нет вывода"
        await message.answer(response)
    except Exception as e:
        await message.answer(f"Ошибка выполнения команды: {e}")


dispatcher = Dispatcher()
dispatcher.include_router(router)

if __name__ == '__main__':
    asyncio.run(dispatcher.start_polling(bot))