import asyncio
import logging
import sys
from config import token
from config import key 
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart,Command
from aiogram.types import Message
from openai import OpenAI
import requests

TOKEN = token
dp = Dispatcher()

client = OpenAI(api_key=key)

def ask(text):
    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages = [
            {'role':'system','content':f"text"}
        ]
    )
    answer = responce.choice[0].message.content
    print(answer)
    return answer


@dp.message()
async def telegram(message:Message):

    answer = ask(message.text)
    try:
        await message.answer(answer)
    except TypeError:
        await message.answer('Something wrong')


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
