import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

from config import *
from music_utils import *
from image_generator import *

TOKEN = token_tg

bot = Bot(token=TOKEN)
dp = Dispatcher()


# /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! 👋\n"
        "Отправь мне любую цитаты из песни — я сделаю из неё красивую картинку\n\n"
        "формат запроса:\n\n"
        "(1 строка) цитата\n"
        "(2 строка) название трека\n"
        "(3 строка) исполнитель\n\n"
        "пример:\n"
        "Зачем вообще тогда рождаться людьми?\n"
        "Девочка с окраины\n"
        "HARU\n"
        "\n\n"
        "all handlers:\n"
        "/start\n"
        "/help\n"
        "any text\n"
    )


# /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "/start — начать работу\n"
        "/help — это меню\n"
        "Любое другое сообщение — обработка текста + картинка"
    )


# Любое другое сообщение
@dp.message(F.text)
async def echo_with_image(message: Message):
    user_id = message.from_user.id
    user_text = message.text
    print(f"{user_id}:\n{user_text}\n")

    user_text_list = user_text.split('\n')

    if len(user_text_list) >= 3:
        # quote = '\n '.join(user_text_list[:-2])  # здесь через join сделаем
        quote = user_text_list[:-2]
        for i in range(len(quote)):
            quote[i] = quote[i] + '\n'
        print(quote)
        title = user_text_list[-2]
        artist = user_text_list[-1]

        query = title + ' - ' + artist
    else:
        response = 'неверный формат'
        await message.answer(
            text=response
        )
        print(f"bot:\n{response}\n")
        return
    #
    cover_path, title, t_artist, link = download_cover(query, user_id)

    if cover_path:
        result_file = create_img(quote, title, artist, cover_path, user_id)
# \n<href="{link}">{title}</a>
        response = f'<blockquote>{''.join(quote)}</blockquote>\n<a href="{link}">{title}</a>\n{artist}'

        image = FSInputFile(result_file)
        await message.answer_photo(
            photo=image,
            caption=response,
            parse_mode = "HTML"
        )
    else:
        response = f"Трек не найден"
        await message.answer(
            text=response
        )

    print(f"bot:\n{response}\n")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())