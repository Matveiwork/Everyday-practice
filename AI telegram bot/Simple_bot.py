import asyncio
from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandStart,Command
bot=Bot(token = '')
dp = Dispatcher()

async def main():
    await dp.start_polling(bot)

    
@dp.message(CommandStart())
async def info(message:Message):
    await message.answer('Привет! \
    Рады тебе! Чтобы понять подходящее ли Latoken для тебя место изучи следующие материалы \
    О Латокен:https://coda.io/@latoken/latoken-talent/latoken-161 \
    \
    О Хакатоне:https://deliver.latoken.com/hackathon  \
     \
     Включи VPN для доступа к сайтам,если ты из России,или введи команду /Хакатон ,чтобы узнать подробнее о хакатоне,или комнаду /Латокен ,чтобы узнать подробнее про Латокен.')

    
@dp.message(Command("Хакатон"))
async def info(message:Message):
    await message.answer('Хакатон проходит по пятницам в 18:00. На нем можно получить опыт внежрения AI и приглашение работать в Латокен.На хакатоне ты сможешь сдвинуть периметр возможностей и получить бесценный опыт.Презентация результата задания будет проходить на следующий день в 18:00,задание нужно прислать в 17:15.В 19:00 объявим победителей,пригласим на интервью и затем оффер.Если ты готов пойти на встречу работы мечты,заполни небольшую анкету:https://docs.google.com/forms/d/e/1FAIpQLSdlj5aA3fCgGri9GeFC4csj-ZiNKnmorRTHNGeiIJRIbKyUZw/viewform')   
    
    

@dp.message(Command('Латокен'))
async def info(message:Message):
    await message.answer('Латокен - это Трамплин на глобальный рынок с технологиями и культурой достижений, на удаленке. В Латокен мы помогаем запускать и покупать стартапы будущего.Нам понадобится научиться листить лучшие токены первыми, а также сделать их ликвидными и легко понятными для торговли. Для этого мы используем ИИ, автоматизируя и расширяя продажи, а также обогащая информацию о токенах данными ончейн и социальными данными.А самое главное, мы строим команду, которая на это способна. Мы считаем, что программировать научится ИИ, поэтому характер важнее навыков разработки.') 
    
    
    
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        
    
await main()