from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
import json, os, time

# 📥 خواندن api_id و api_hash از config.json
with open("config.json", "r") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
channel = config["target_group"]  # استفاده از مقدار target_group در config
delay = config.get("delay", 10)   # مقدار پیش‌فرض 10 ثانیه

# 📁 ساخت پوشه لاگ‌ها اگر وجود نداشت
os.makedirs("logs", exist_ok=True)

# 🧠 بارگیری اعضای ذخیره‌شده
with open("members_db.json", "r") as f:
    members = json.load(f)

# اطمینان از وجود کلید 'group_users'
if 'group_users' not in members:
    members['group_users'] = {}

# استخراج لیست اعضا از group_users
users = list(set(
    user for group in members["group_users"].values() for user in group
))

# 🎯 گرفتن sessionها
sessions = [f for f in os.listdir("sessions") if f.endswith(".session")]
if not sessions:
    print("❌ هیچ فایل سشنی یافت نشد!")
    exit()

per_bot = len(users) // len(sessions) + 1

for index, session in enumerate(sessions):
    print(f"🟢 اجرای {session}...")
    client = TelegramClient(f"sessions/{session}", api_id, api_hash)
    client.start()
    part = users[index * per_bot:(index + 1) * per_bot]
    for user_id in part:
        try:
            client(InviteToChannelRequest(channel, [int(user_id)]))
            print(f"✅ {session} → {user_id} افزوده شد")
            with open("logs/added.txt", "a") as log:
                log.write(user_id + "\n")
        except Exception as e:
            print(f"❌ {session} نتوانست {user_id} را اضافه کند: {e}")
            with open("logs/failed.txt", "a") as log:
                log.write(user_id + "\n")
        time.sleep(delay)
    client.disconnect()
    print(f"⛔️ {session} پایان یافت.")
