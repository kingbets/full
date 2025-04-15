from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
import json, os, time

# خواندن api_id و api_hash و target_group از config.json
with open("config.json", "r") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
target_group = config["target_group"]
delay = config.get("delay", 10)

# بررسی وجود target_group
if not target_group:
    print("❌ target_group در config.json مشخص نشده است!")
    exit()

# ساخت پوشه لاگ‌ها در صورت نبود
os.makedirs("logs", exist_ok=True)

# خواندن لیست اعضا از فایل بکاپ
if not os.path.exists("members_db.json"):
    print("❌ فایل members_db.json یافت نشد!")
    exit()

with open("members_db.json", "r") as f:
    members = json.load(f)

# اطمینان از وجود کلید 'group_users'
if 'group_users' not in members:
    members['group_users'] = {}

# استخراج اعضا از گروه‌ها
user_ids = list(set(
    user_id for group in members["group_users"].values() for user_id in group
))

# اجرای فقط با یک session (برای ادد واقعی، نه multi)
sessions = [f for f in os.listdir("sessions") if f.endswith(".session")]
if not sessions:
    print("❌ هیچ sessionی وجود ندارد.")
    exit()

# استفاده از فقط اولین session
session = sessions[0]
client = TelegramClient(f"sessions/{session}", api_id, api_hash)
client.start()

for user_id in user_ids:
    try:
        client(InviteToChannelRequest(target_group, [int(user_id)]))
        print(f"✅ افزودن موفق: {user_id}")
        with open("logs/real_added.txt", "a")_
