from telethon import TelegramClient, events
import json, os

# خواندن api_id و api_hash از config.json
with open("config.json", "r") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]

# ساخت فایل بکاپ اولیه در صورت نبود
if not os.path.exists("members_db.json"):
    with open("members_db.json", "w") as f:
        json.dump({"group_users": {}, "private_users": {"users": []}}, f)

# خواندن داده‌های موجود از فایل
with open("members_db.json", "r") as f:
    members = json.load(f)

# اطمینان از وجود کلید 'group_users'
if 'group_users' not in members:
    members['group_users'] = {}

# گرفتن لیست sessionها
sessions_folder = "sessions"
sessions = [f for f in os.listdir(sessions_folder) if f.endswith(".session")]

clients = []

for session in sessions:
    client = TelegramClient(f"{sessions_folder}/{session}", api_id, api_hash)
    clients.append(client)

    @client.on(events.NewMessage)
    async def handler(event):
        try:
            chat = await event.get_chat()
            sender = await event.get_sender()
            user_id = str(sender.id)

            if event.is_channel:
                return

            if event.is_group or event.is_supergroup:
                group_id = str(chat.id)
                members["group_users"].setdefault(group_id, [])
                if user_id not in members["group_users"][group_id]:
                    members["group_users"][group_id].append(user_id)

            elif event.is_private:
                if user_id not in members["private_users"]["users"]:
                    members["private_users"]["users"].append(user_id)

            # ذخیره در فایل با async
            with open("members_db.json", "w") as f:
                json.dump(members, f, indent=2)

        except Exception as e:
            print(f"[ERROR] {e}")

# اجرای sessionها
for client in clients:
    client.start()

print("✅ Watcher is running on all sessions...")
for client in clients:
    client.run_until_disconnected()
