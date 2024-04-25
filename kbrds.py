from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Message

keyboard_initial = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[
    InlineKeyboardButton(text="Connect", callback_data="connect")]]
)

keyboard = [[
    KeyboardButton(text="Execute Command", callback_data="execute"),
    KeyboardButton(text="Upload File", callback_data="upload"),
    KeyboardButton(text="Download File", callback_data="download"),
    KeyboardButton(text="Submit Job", callback_data="submit_job"),
    KeyboardButton(text="Show Queue", callback_data="show_queue"),
    KeyboardButton(text="Cancel Job", callback_data="cancel_job"),
    KeyboardButton(text="Disconnect", callback_data="disconnect")
]]

keyboard_connected = ReplyKeyboardMarkup(
    keyboard=keyboard,
    resize_keyboard=True,
    one_time_keyboard=True
)

keyboard_connecting = [
  [
    InlineKeyboardButton(text="Подключиться с паролем", callback_data="auth_password"),
    InlineKeyboardButton(text="Подключиться с .pem ключом", callback_data="auth_pem")
  ]]