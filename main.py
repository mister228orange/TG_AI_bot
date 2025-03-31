import asyncio
from AIManager import AIManager
from telethon import TelegramClient, events
from config import cfg


CHUNK_SIZE = 3800
MSG_TAIL = "\n Donate me to \nSber: 89527339056\n or TON: UQA2fRjn7N901f8bX5h0Z-vDsaxeMsQoFu8C06PfuH7r8DfI \n"


async def handle_msgs(event):
    sender = event.chat_id
    if event.message.message == '/start':
        await tg_client.send_message(
            sender,
            message=f'Привет, я LLM {ai_controller.model_name} от {ai_controller.model_developers},'
                    f' готова ответить на любые ваши текстовые вопросы.'
        )
    else:
        try:
            AI_response = await ai_controller.get_AI_response(sender, event.message.message)
            for start_slice in range(0, len(AI_response), CHUNK_SIZE):
                await tg_client.send_message(
                    sender,
                    message=AI_response[start_slice:start_slice + CHUNK_SIZE] + MSG_TAIL
                )
        except Exception as e:
            print(f"Error handling message: {e}")


async def main():
    # Initialize components
    global ai_controller, tg_client
    ai_controller = AIManager("gemma3:12b", "google")

    # Create client
    tg_client = TelegramClient('bot', cfg.API_ID, cfg.API_HASH)

    tg_client.add_event_handler(events.NewMessage)
    tg_client.add_event_handler(handle_msgs, events.NewMessage())


    try:
        print("Starting bot...")
        await tg_client.start(bot_token=cfg.BOT_TOKEN)
        print("Bot started successfully!")
        await tg_client.run_until_disconnected()
    except Exception as e:
        print(f"Failed to start bot: {e}")
    finally:
        await tg_client.disconnect()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
