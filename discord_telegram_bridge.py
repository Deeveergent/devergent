import asyncio
import logging
from telethon import TelegramClient, events
import discord
from discord.ext import commands

# ====== Настройки (замените на свои значения) ======
API_ID = 25599182  # Ваш API ID с https://my.telegram.org
API_HASH = '947c526d0cfbf055dcce3fd39ab62290'
TELEGRAM_CHANNEL = '@gibsonllc'  # Юзернейм или ID канала (например, '@mychannel')
DISCORD_BOT_TOKEN = 'MTI1MzcyNDE1NzcyODc4ODU4MQ.G9q_6Q.jJq-TKTUm7dc3D8TwLTShGfTMaINyNSJq_7F1U'
DISCORD_CHANNEL_ID = 1375783503677096006  # ID канала Discord для публикации
# ================================================

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация клиентов
tg_client = TelegramClient('tg_session', API_ID, API_HASH)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Телеграм-обработчик новых сообщений
@tg_client.on(events.NewMessage(chats=TELEGRAM_CHANNEL))
async def telegram_handler(event):
    message = event.message
    content = message.text or ''
    discord_channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if discord_channel is None:
        logger.warning(f'Канал Discord с ID {DISCORD_CHANNEL_ID} не найден')
        return

    # Отправка медиа, если есть
    if message.photo or message.video or message.document:
        file_path = await message.download_media()
        await discord_channel.send(content, file=discord.File(file_path))
    else:
        await discord_channel.send(content)

    logger.info('Сообщение отправлено в Discord')

# Событие готовности Discord-бота
@bot.event
async def on_ready():
    logger.info(f'Discord бот запущен как {bot.user}')

# Функция запуска Telegram-клиента
async def start_telegram():
    await tg_client.start()
    logger.info('Telegram клиент запущен')
    await tg_client.run_until_disconnected()

# Главная функция для параллельного запуска
async def main():
    telegram_task = asyncio.create_task(start_telegram())
    discord_task = asyncio.create_task(bot.start(DISCORD_BOT_TOKEN))
    await asyncio.gather(telegram_task, discord_task)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Остановка бота...')
        bot.loop.stop()
        tg_client.disconnect()
