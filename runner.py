import subprocess
import threading

# فایل‌هایی که باید اجرا شوند
scripts = [
    "main_bot.py",
    "add_multi.py",
    "watcher.py",
    "add_fake_members.py"
]

def run_script(script_name):
    subprocess.call(["python", script_name])

# اجرای هر فایل در یک Thread جداگانه
threads = []
for script in scripts:
    t = threading.Thread(target=run_script, args=(script,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
