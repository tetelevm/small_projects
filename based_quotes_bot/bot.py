from telegram import Bot
from telegram.ext import Application, MessageHandler

from env import env
from service import get_quote


async def command_im_silly(update, context):
    return await update.effective_chat.send_message(
        "Sorry, I'm a silly machine and I don't understand anything.",
    )


async def app_init(token: str):
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(None, command_im_silly, False))

    await app.initialize()
    await app.updater.start_polling()
    await app.start()


async def send_quote(bot: Bot):
    quote = get_quote()
    return await bot.send_message(
        chat_id=env("CHAT_LINK"),
        text=quote,
    )


async def bot_init(token: str):
    bot = Bot(token)
    await bot.initialize()
    return bot
