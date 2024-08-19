import asyncio

from env import env
from bot import app_init, bot_init, send_quote
from service import wait_6_am


async def main():
    await app_init(env("TOKEN"))
    bot = await bot_init(env("TOKEN"))
    print(f"bot {bot.name} initialized")

    while True:
        await wait_6_am()
        await send_quote(bot)


asyncio.run(main())
