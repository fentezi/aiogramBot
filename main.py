import datetime
import logging
import os
import platform
import socket
import subprocess
import tempfile
import time
import uuid
import webbrowser
from ctypes import cast, POINTER

import cv2
import psutil
import pyautogui
import pygetwindow as gw
import requests
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.exceptions import NetworkError
from comtypes import CLSCTX_ALL
from pycaw.api.endpointvolume import IAudioEndpointVolume
from pycaw.utils import AudioUtilities
from screeninfo import get_monitors

from keyboards import keyboard, keyboard_volume, keyboard_media

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1.5

logging.basicConfig(level=logging.INFO)

token = '5601004463:AAHmEsiVDMxE7fCSCD2-sOE0lMjXZHvqaWg'
bot = Bot(token=token)
dp = Dispatcher(bot=bot, storage=MemoryStorage())


class YourStateEnum(StatesGroup):
    volume = State()


def system_inf():
    time_pc = psutil.boot_time()
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(time_pc)
    uptime_work = str(datetime.timedelta(seconds=round(uptime.total_seconds())))
    info = {
        'Время работы ПК': uptime_work,
        'Операционная система': platform.system(),
        'Оперативная память': psutil.virtual_memory()[0],
        'Процессор': platform.processor(),
        'Машина': platform.machine()
    }
    result = ''
    for key, values in info.items():
        result += f'{key}: {values}\n'
    return result


def ip_PC():
    """Получает информацию о PC(hostname, IP, MAC)"""
    # Имя компьютера
    hostname = socket.gethostname()
    # Получаем IP-адрес
    ip_address = socket.gethostbyname(hostname)
    # Получаем MAC-адрес
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1])
    return "Имя компьютера: " + hostname + \
           "\nIP-адрес: " + ip_address + \
           "\nMAC-адрес: " + mac_address


def join_classroom():
    """Подключается к Google Classroom."""
    if 'КМП 22-1/11 I курс II сем.2022-2023 - Google Chrome' in gw.getAllTitles():
        try:
            google_window = gw.getWindowsWithTitle('КМП 22-1/11 I курс II сем.2022-2023 - Google Chrome')[0]
            google_window.maximize()
            google_window.activate()
            time.sleep(1.5)
            pyautogui.moveTo(x=542, y=526)
            connect = pyautogui.click()
            response = requests.get('https://meet.google.com/kht-cavh-trn?authuser=2')
            if response.status_code == 200:
                time.sleep(1.5)
                off_micro = pyautogui.click(x=684, y=756)
                off_camera = pyautogui.click(x=765, y=759)
                time.sleep(1)
                # con = pyautogui.click(x=1262, y=584)
                return 'Вы подключены'
            else:
                return "Сайт не загружен"
        except ConnectionError:
            return 'Отсутствует подключение к интернету!'
    else:
        try:
            webbrowser.register('google-chrome', None,
                                webbrowser.BackgroundBrowser('C:\Program Files\Google\Chrome\Application\chrome.exe'))
            webbrowser.get(using='google-chrome').open('https://classroom.google.com/u/2/c/NTgyMDE2NTQ1Nzky?hl=ru')
            time.sleep(1.5)
            pyautogui.moveTo(x=542, y=526)
            connect = pyautogui.click()
            response = requests.get('https://meet.google.com/kht-cavh-trn?authuser=2')
            if response.status_code == 200:
                time.sleep(1.5)
                off_micro = pyautogui.click(x=684, y=756)
                off_camera = pyautogui.click(x=765, y=759)
                time.sleep(1)
                # con = pyautogui.click(x=1262, y=584)
                return 'Вы подключены'
            else:
                return "Сайт не загружен"
        except ConnectionError:
            return 'Отсутствует подключение к интернету!'


def disconnect_class():
    '''Выходит с урока в Classroom'''
    pyautogui.moveTo(x=1115, y=1038, duration=0.5)
    pyautogui.click()


def power_off():
    subprocess.call(['shutdown', '/s', '/t', '1'])


def reboot():
    subprocess.call(['shutdown', '/r', '/t', '1'])


def adjust_volume(volume_percent: int):
    """Устанавливает громкость на указанный процент."""
    if volume_percent != 0:
        direction = 'volumeup' if volume_percent > 0 else 'volumedown'
        pyautogui.press(direction, presses=abs(volume_percent) // 2)
    else:
        pyautogui.press('volumemute')


@dp.message_handler(commands=['start'])
async def welcome_message(message: types.Message):
    try:
        await message.answer(
            'Привет. Этот бот разработан для управлением ПК с помощью Telegram.\n /help для просмотра доступных команд')
    except ConnectionError:
        await message.answer('Ошибка подключения к интернету!')


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer('/systeminfo - получает информация о ПК к которому вы подключены\n'
                         '/ip_pc - получает информацию о ПК(hostname, IP, MAC)\n', reply_markup=keyboard)


@dp.message_handler(commands=['system'])
async def system_command(message: types.Message):
    await message.answer(system_inf())


@dp.message_handler(commands=['ip'])
async def ip_command(message: types.Message):
    await message.answer(ip_PC())


@dp.message_handler(commands=['join'])
async def join_command(message: types.Message):
    await message.answer(join_classroom())


@dp.message_handler(commands=['disconnect'])
async def disconnect_command(message: types.Message):
    disconnect_class()


@dp.message_handler(commands=['reboot'])
async def reboot_command(message: types.Message):
    await message.answer('Перезагружаем ПК...')
    reboot()


@dp.message_handler(commands=['off'])
async def off_command(message: types.Message):
    await message.answer('Выключение...')
    power_off()


@dp.message_handler(commands=['volume'])
async def volume_command(message: types.Message):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    await message.answer(f'Текущая громкость: {round(volume.GetMasterVolumeLevelScalar() * 100)}%',
                         reply_markup=keyboard_volume)


@dp.message_handler(commands=['media'])
async def media_command(message: types.Message):
    await message.answer('Media', reply_markup=keyboard_media)


@dp.message_handler(commands=['screens'])
async def screens_command(message: types.Message):
    monitors = get_monitors()
    if len(monitors) > 0:
        response = ""
        i = 0
        keyboard_screen = InlineKeyboardMarkup()
        for monitor in monitors:
            button = InlineKeyboardButton(text=f'Скриншот экрана №{i} ({monitor.width}x{monitor.height})',
                                          callback_data=f'{i}')
            keyboard_screen.add(button)
            response += f"№{i}: {monitor.width}x{monitor.height}. Активный монитор: {monitor.is_primary}\n"
            i += 1
        await message.answer(f'Список экранов ({len(monitors)}):\n'
                             f'{response}', reply_markup=keyboard_screen)
    else:
        await message.answer("Монитор не найден")


@dp.message_handler(commands=['cameras'])
async def cameras_command(message: types.Message):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        await message.answer('Не удалось открыть камеру')
        exit()
    ret, frame = cap.read()
    with tempfile.NamedTemporaryFile(suffix='.jpg', dir=tempfile.gettempdir(), delete=False) as temp_file:
        cv2.imwrite(temp_file.name, frame)
        cap.release()
        temp_file.seek(0)
        if os.path.exists(temp_file.name):
            await bot.send_photo(message.chat.id, open(temp_file.name, 'rb'))
            temp_file.close()
            os.unlink(temp_file.name)


@dp.message_handler(content_types=['text'])
async def media_controller(message: types.Message):
    if message.text == 'Следуюющий трек':
        pyautogui.press('nexttrack')
    elif message.text == 'Предыдущий трек':
        pyautogui.press('prevtrack', presses=2)
    elif message.text == 'Стоп/Старт':
        pyautogui.press('playpause')


@dp.callback_query_handler(lambda callback_query: callback_query.data and callback_query.data.isdigit())
async def handle_monitor_screen(callback_query: types.CallbackQuery):
    screen_number = int(callback_query.data)
    screen = pyautogui.screenshot()
    with tempfile.NamedTemporaryFile(suffix='.jpeg', dir=tempfile.gettempdir(), delete=False) as temp_file:
        screen.save(temp_file.name)
        temp_file.seek(0)
        if os.path.exists(temp_file.name):
            await bot.send_photo(callback_query.message.chat.id, open(temp_file.name, 'rb'))
            temp_file.close()
            os.unlink(temp_file.name)
        else:
            await callback_query.answer('Ошибка: файл не найден')


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'btn_volume')
async def volume_handler(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.bot.edit_message_text(text='На сколько увеличить(+)/уменьшить(-) звук?',
                                               chat_id=callback_query.from_user.id,
                                               message_id=callback_query.message.message_id)
    await YourStateEnum.volume.set()


@dp.message_handler(state=YourStateEnum.volume, content_types=types.ContentTypes.TEXT)
async def handle_volume(message: types.Message, state: FSMContext):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current_value = round(volume.GetMasterVolumeLevelScalar() * 100)
    value = int(message.text)
    adjust_volume(value)
    if value > 0:
        await message.answer(f"Громкость увеличена до {current_value + value}%")
    else:
        await message.answer(f'Громкость понижена до {current_value + value}%')
    await state.reset_state()


@dp.callback_query_handler(lambda callback_query: CallbackQuery)
async def mute_volume(callback_query: CallbackQuery):
    adjust_volume(0)


if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except NetworkError:
            time.sleep(3)
            print('Error')
