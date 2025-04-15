import os
from telegram import Bot

bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

owner_ids = [int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x]
manager_ids = [int(x) for x in os.getenv("MANAGER_IDS", "").split(",") if x]
viewer_ids = [int(x) for x in os.getenv("VIEWER_IDS", "").split(",") if x]

def is_owner(user_id: int) -> bool:
    return user_id in owner_ids

def is_manager(user_id: int) -> bool:
    return user_id in manager_ids

def is_viewer(user_id: int) -> bool:
    return user_id in viewer_ids

async def notify_group(user_ids: list[int], text: str):
    for uid in user_ids:
        try:
            await bot.send_message(chat_id=uid, text=text)
        except Exception as e:
            print(f"❌ Не удалось отправить сообщение пользователю {uid}: {e}")

async def notify_admins(text: str):
    await notify_group(owner_ids, text)

async def notify_managers(text: str):
    await notify_group(manager_ids, text)

async def notify_viewers(text: str):
    await notify_group(viewer_ids, text)
