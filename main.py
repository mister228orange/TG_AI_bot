import asyncio
from AIManager import AIManager
from telethon import TelegramClient, events
from config import cfg

AI_URL = 'http://localhost:11434/api/chat'
CHUNK_SIZE = 4000


bot = TelegramClient('bot', cfg.API_ID, cfg.API_HASH, device_model="Windows Desktop",system_version="Ubuntu 20.2")
ai = AIManager()


@bot.on(events.NewMessage())
async def handle_msgs(event):
    """Send a message when the command /start is issued."""
    print(event.message)
    sender = event.chat_id

    try:
        AI_response = await ai.get_AI_response(sender, event.message.message)
        for start_slice in range(0, len(AI_response), CHUNK_SIZE):
            await bot.send_message(sender, message=AI_response[start_slice:start_slice+CHUNK_SIZE])
    except Exception as e:
        print(e)



async def main():
    """Start the bot."""
    await bot.start()

    await bot.connect()
    bot_task = asyncio.create_task(bot.run_until_disconnected())
    await asyncio.gather(bot_task)


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
