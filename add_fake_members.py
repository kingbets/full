from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
import json, os, time

# خواندن api_id و api_hash از config.json
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

# خواندن تمام session ها
sessions_path = "sessions"
sessions = [f for f in os.listdir(sessions_path) if f.endswith(".session")]

if not sessions:
    print("❌ هیچ sessionی یافت نشد!")
    exit()

# ساخت پوشه لاگ‌ها در صورت نبود
os.makedirs("logs", exist_ok=True)

for session in sessions:
    print(f"🟢 یوزربات {session} در حال ورود به گروه است...")
    client = TelegramClient(f"{sessions_path}/{session}", api_id, api_hash)
    client.start()
    try:
        # اتصال به گروه و اضافه کردن
        client(JoinChannelRequest(target_group))
        print(f"✅ {session} با موفقیت وارد گروه شد.")
        with open("logs/fake_added.txt", "a") as f:
            f.write(session + "\n")
    except Exception as e:
        print(f"❌ خطا برای {session}: {e}")
        with open("logs/fake_failed.txt", "a") as f:
            f.write(session + " | " + str(e) + "\n")
    finally:
        # اتصال به کانال و سپس قطع ارتباط
        client.disconnect()
    time.sleep(delay)
