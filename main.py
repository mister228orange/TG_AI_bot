import asyncio
from AIManager import AIManager
from telethon import TelegramClient, events
from config import cfg

CHUNK_SIZE = 3800
MSG_TAIL = "\n Donate me to \nSber: 89527339056\n or TON: UQA2fRjn7N901f8bX5h0Z-vDsaxeMsQoFu8C06PfuH7r8DfI \n"


async def main():
    # Initialize components
    ai = AIManager("gemma3:12b", "google")

    # Create client
    bot = TelegramClient('bot', cfg.API_ID, cfg.API_HASH)

    @bot.on(events.NewMessage())
    async def handle_msgs(event):
        """Handle incoming messages"""
        print("Received message:", event.message)
        sender = event.chat_id
        if event.message.message == '/start':
            await bot.send_message(
                sender,
                message=f'Привет, я LLM {ai.model_name} от {ai.model_developers},'
                        f' готова ответить на любые ваши текстовые вопросы.'
            )
        else:
            try:
                AI_response = await ai.get_AI_response(sender, event.message.message)
                for start_slice in range(0, len(AI_response), CHUNK_SIZE):
                    await bot.send_message(
                        sender,
                        message=AI_response[start_slice:start_slice + CHUNK_SIZE] + MSG_TAIL
                    )
            except Exception as e:
                print(f"Error handling message: {e}")

    try:
        print("Starting bot...")
        await bot.start(bot_token=cfg.BOT_TOKEN)
        print("Bot started successfully!")
        await bot.run_until_disconnected()
    except Exception as e:
        print(f"Failed to start bot: {e}")
    finally:
        await bot.disconnect()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
