import asyncio

from settings import logger, TOKEN
from bot import app_init, bot_init, send_quote
from service import get_quote, calc_waiting_seconds


async def maintain_channel(bot):
    """
    waits until the post is scheduled amd sends the quote.
    """

    waiting_time = calc_waiting_seconds()
    logger.info(f"Waiting {waiting_time} seconds")
    await asyncio.sleep(waiting_time)

    quote = get_quote()
    logger.info(f"Sending quote < {quote} >")
    await send_quote(bot, quote)
    await asyncio.sleep(1)


async def main():
    await app_init(TOKEN)
    bot = await bot_init(TOKEN)
    logger.info(f"Bot {bot.name} initialized")
    while True:
        await maintain_channel(bot)


asyncio.run(main())
