import logging
import jsonGet
import jsonGet2
import jsonGet3

from aiogram import types, Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from pyowm import OWM
from pyowm.utils.config import get_default_config
from yaml import safe_load

from config import api_key_weather, bot_token

bot = Bot(bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands="start")
async def cmdStart(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Погода 🌥", "Поломки ⚠", "Оборудование 📠", "Инфо ℹ"]
    keyboard.add(*buttons)
    await message.answer("Что хотите посмотреть?", reply_markup=keyboard)


@dp.message_handler(text_contains="Инфо ℹ")
async def help(message: types.Message):
    with open('intro.png', 'rb') as png:
        await message.answer_photo(png)
    await message.answer("""
    Привет, новый юзер! 👋
    Краткая информация по этому боту.
    Наш бот был создан для мониторинга работы орошающих установок и просмотра погоды по всему миру.
     
    Навигация по боту осуществляется с помощью кнопок.
     
    На этом пока все, список будет дополнятся.
    Контакт создателя: @endfixed
    """)


class CityChoose(StatesGroup):
    writeCity = State()


@dp.message_handler(text_contains="Погода 🌥")
async def user_cityChoose(message: types.Message):
    await message.answer("Введите название города(села):")
    await CityChoose.writeCity.set()


@dp.message_handler(state=CityChoose.writeCity)
async def checkWeather(message: types.Message, state: FSMContext):
    await state.update_data(chosenCity=message.text)
    city = await state.get_data()

    config_dict = get_default_config()
    config_dict['language'] = 'ru'
    config_dict['connection']['use_ssl'] = False
    config_dict['connection']["verify_ssl_certs"] = False
    owm = OWM(api_key_weather, config_dict)
    language = 'ru'
    mgr = owm.weather_manager()
    try:
        observation = mgr.weather_at_place(str(city['chosenCity']))
    except Exception as err:
        print(err)
        await state.finish()
        await message.answer(
            "Не удалось найти такой город(село).\nЕсли хотите попробовать еще раз, нажмите кнопку 'Погода 🌥'")
        return

    w = observation.weather
    temperature = w.temperature('celsius')['temp']
    status = w.detailed_status
    wind = w.wind()

    def WhatIsWind():
        if 0 <= w.wind()['deg'] < 45:
            return 'Северный'

        if 45 <= w.wind()['deg'] < 90:
            return 'Северо-Восточный'

        if 90 <= w.wind()['deg'] < 135:
            return 'Восточный'

        if 135 <= w.wind()['deg'] < 180:
            return 'Юго-Восточный'

        if 180 <= w.wind()['deg'] < 225:
            return 'Южный'

        if 225 <= w.wind()['deg'] < 270:
            return 'Юго-Западный'

        if 270 <= w.wind()['deg'] < 325:
            return 'Западный'

        if 325 <= w.wind()['deg'] <= 360:
            return 'Северо-Западный'

    await message.answer(f"""Город: {city['chosenCity']}. \n
🌡️ Температура: {temperature} °С.
⛅ Погода: {status}.
‍💨 Ветер: """ + WhatIsWind() + f""" {wind['speed']}м/с \
""")

    await state.finish()


@dp.message_handler(text_contains="Поломки ⚠")
async def notification(message: types.Message):
    with open("var.txt") as file:
        listvar = safe_load(file)

    await message.answer("Установка №1")
    if listvar['isWatering'] == False:
        await message.answer("Внимание! \n Поливание не работает!")
    elif listvar['isWorking'] == False:
        await message.answer("Внимание! \n Орошаюшая установка не работает!")
    else:
        await message.answer("Все корректно работает!")

    with open("var2.txt") as file:
        listvar = safe_load(file)

    await message.answer("Установка №2")
    if listvar['isWatering'] == False:
        await message.answer("Внимание! \n Поливание не работает!")
    elif listvar['isWorking'] == False:
        await message.answer("Внимание! \n Орошаюшая установка не работает!")
    else:
        await message.answer("Все корректно работает!")

    with open("var3.txt") as file:
        listvar = safe_load(file)

    await message.answer("Установка №3")
    if listvar['isWatering'] == False:
        await message.answer("Внимание! \n Поливание не работает!")
    elif listvar['isWorking'] == False:
        await message.answer("Внимание! \n Орошаюшая установка не работает!")
    else:
        await message.answer("Все корректно работает!")


# ----------------------------------------------------

@dp.message_handler(text_contains="Оборудование 📠")
async def serviceChoose(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["№1", "№2", "№3", "Назад ⬅"]
    keyboard.add(*buttons)
    await message.answer("Выберите орошающую установку:", reply_markup=keyboard)


@dp.message_handler(text_contains="№1")
async def serviceGet1(message: types.Message):

    with open("var.txt") as file:
        listvar = safe_load(file)

    if listvar['thingId'] == 'device1':
        await message.answer("Установка №1")
        await message.answer(f"""
                Оборудование:
            Поливает : {listvar['isWatering']}
            Работает : {listvar['isWorking']}""")
        await message.answer(f"""
    Координаты центральной точки:
Координаты (долгота) : {listvar['current']['geo0']['lon']}
Координаты (широта) : {listvar['current']['geo0']['lat']}

Координаты дальней точки:
Координаты (долгота) : {listvar['current']['geo1']['lon']}
Координаты (широта) : {listvar['current']['geo1']['lat']}
            """)

        url = f"https://2gis.ru/geo/70030076118166550/{listvar['current']['geo0']['lon']}%2C{listvar['current']['geo0']['lat']}?m=56.424083%2C54.694473%2F5.99"
        await message.answer(f"""Где сейчас? \n {url}""")
    else:
        file.readline()
        return


@dp.message_handler(text_contains="№2")
async def serviceGet2(message: types.Message):

    with open("var2.txt") as file:
        listvar2 = safe_load(file)

        await message.answer("Установка №2")
        await message.answer(f"""
                Оборудование:
            Поливает : {listvar2['isWatering']}
            Работает : {listvar2['isWorking']}""")
        await message.answer(f"""
    Координаты центральной точки:
Координаты (долгота) : {listvar2['current']['geo0']['lon']}
Координаты (широта) : {listvar2['current']['geo0']['lat']}
 
Координаты дальней точки:
Координаты (долгота) : {listvar2['current']['geo1']['lon']}
Координаты (широта) : {listvar2['current']['geo1']['lat']}
            """)

        url = f"https://2gis.ru/geo/70030076118166550/{listvar2['current']['geo0']['lon']}%2C{listvar2['current']['geo0']['lat']}?m=56.424083%2C54.694473%2F5.99"
        await message.answer(f"""Где сейчас? \n {url}""")


@dp.message_handler(text_contains="№3")
async def serviceGet3(message: types.Message):

    with open("var3.txt") as file:
        listvar3 = safe_load(file)

        await message.answer("Установка №3")
        await message.answer(f"""
                Оборудование:
            Поливает : {listvar3['isWatering']}
            Работает : {listvar3['isWorking']}""")
        await message.answer(f"""
    Координаты центральной точки:
Координаты (долгота) : {listvar3['current']['geo0']['lon']}
Координаты (широта) : {listvar3['current']['geo0']['lat']}

Координаты дальней точки:
Координаты (долгота) : {listvar3['current']['geo1']['lon']}
Координаты (широта) : {listvar3['current']['geo1']['lat']}
            """)

        url = f"https://2gis.ru/geo/70030076118166550/{listvar3['current']['geo0']['lon']}%2C{listvar3['current']['geo0']['lat']}?m=56.424083%2C54.694473%2F5.99"
        await message.answer(f"""Где сейчас? \n {url}""")


@dp.message_handler(text_contains="Назад ⬅")
async def btns2(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Погода 🌥", "Поломки ⚠", "Оборудование 📠", "Инфо ℹ"]
    keyboard.add(*buttons)
    await message.answer("Что хотите посмотреть?", reply_markup=keyboard)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
