import threading
import time
import subprocess

def schedule_hours(hours, clean_func):
    def loop():
        while True:
            clean_func()
            time.sleep(hours * 3600)

    threading.Thread(target=loop, daemon=True).start()

# ---------------- STARTUP ----------------

def enable_startup(exe_path):
    subprocess.run(
        f'schtasks /create /tn "CleanerLite" /tr "{exe_path}" /sc onlogon /rl highest /f',
        shell=True
    )

# ---------------- RESUME FROM SLEEP ----------------

def enable_resume(exe_path):
    subprocess.run(
        f'schtasks /create /tn "CleanerResume" /tr "{exe_path}" /sc onevent '
        f'/ec System /mo "*[System[Provider[@Name=\'Power-Troubleshooter\'] and EventID=1]]" /rl highest /f',
        shell=True
    )