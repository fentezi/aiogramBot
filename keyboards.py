from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создание кнопок
button1 = KeyboardButton('💻System')
button2 = KeyboardButton('/ip')
button3 = KeyboardButton('/join')
button4 = KeyboardButton('/disconnect')
button5 = KeyboardButton('/volume')
button6 = KeyboardButton('/media')
button7 = KeyboardButton('/reboot')
button8 = KeyboardButton('/off')
button9 = KeyboardButton('/cameras')
button10 = KeyboardButton('/screens')
button11 = KeyboardButton('/file explorer')


# Создание клавиатуры
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.row(button1, button2, button3)
keyboard.row(button4, button5, button6)
keyboard.row(button7, button8)
keyboard.row(button9, button10, button11)

vol_button = InlineKeyboardButton("+-vol", callback_data="btn_volume")
mute_button = InlineKeyboardButton("mute", callback_data="mute")

keyboard_volume = InlineKeyboardMarkup().row(vol_button).add(mute_button)

#media keyboards
btn_next = InlineKeyboardButton('⏩', callback_data='btn_next')
btn_stop = InlineKeyboardButton('⏯', callback_data='btn_stop')
btn_back = InlineKeyboardButton('⏪', callback_data='btn_back')

keyboard_media = InlineKeyboardMarkup(resize_keyboard=True).row(btn_back, btn_stop, btn_next)
