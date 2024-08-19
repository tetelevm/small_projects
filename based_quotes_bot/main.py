import asyncio

from settings import logger, TOKEN
from bot import app_init, bot_init, send_quote
from service import wait_sending_time


async def main():
    await app_init(TOKEN)
    bot = await bot_init(TOKEN)
    logger.info(f"Bot {bot.name} initialized")

    while True:
        await wait_sending_time()
        await send_quote(bot)
        await asyncio.sleep(1)


asyncio.run(main())
