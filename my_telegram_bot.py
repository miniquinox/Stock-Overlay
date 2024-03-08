import asyncio
from telegram import Bot

async def send_telegram(options_data):
    bot_token = '7155310366:AAE0jJEHZOvudvMzrzFNw1LOvnEL1lD6LsU'
    chat_id = '-4144046020'
    bot = Bot(token=bot_token)

    # Using await to call the coroutine send_message
    await bot.send_message(chat_id=chat_id, text=options_data)


# Running the asynchronous function using asyncio.run()
if __name__ == '__main__':
    options_data = "Hello"
    asyncio.run(send_telegram(options_data))