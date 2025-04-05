import logging
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Считываем токен бота из переменных окружения
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL')  # Автоматически создается Railway

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Настройки webhook
WEBHOOK_HOST = RAILWAY_STATIC_URL  # Автоматический URL от Railway
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT', default=8000))

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! 🤖 Я — ваш тестовый бот.")

@dp.message()
async def echo(message: Message):
    await message.answer(message.text)

# Функция, вызываемая при запуске бота
async def on_startup():
    logging.info("Загрузка webhook...")
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

# Функция, вызываемая при выключении бота
async def on_shutdown():
    logging.info("Удаление webhook...")
    await bot.delete_webhook()

# Создание aiohttp приложения
app = web.Application()

# Настройка вебхука
async def on_startup_app(app):
    await on_startup()

async def on_shutdown_app(app):
    await on_shutdown()

# Добавление обработчика запросов
app.router.add_post(WEBHOOK_PATH, lambda request: dp.feed_webhook_update(bot, request))

# Запуск сервера
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.on_startup.append(on_startup_app)
    app.on_shutdown.append(on_shutdown_app)

    # Запуск aiohttp сервера
    web.run_app(
        app,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
