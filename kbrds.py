from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Message

keyboard_initial = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[
    InlineKeyboardButton(text="Connect", callback_data="connect")]]
)

keyboard_connecting = [
  [
    InlineKeyboardButton(text="пароль", callback_data="auth_password"),
    InlineKeyboardButton(text=".pem ключ", callback_data="auth_pem")
  ]]