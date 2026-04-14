import threading
import time
import subprocess

def schedule_hours(hours, exe_path):
    cmd = f'schtasks /create /tn "CleanerInterval" /tr "\\"{exe_path}\\" --silent-clean" /sc HOURLY /mo {hours} /rl highest /f'
    subprocess.run(cmd, shell=True)

# ---------------- STARTUP ----------------

def enable_startup(exe_path):
    subprocess.run(
        f'schtasks /create /tn "CleanerLite" /tr "\\"{exe_path}\\" --silent-clean" /sc onlogon /rl highest /f',
        shell=True
    )

# ---------------- RESUME FROM SLEEP ----------------

def enable_resume(exe_path):
    subprocess.run(
        f'schtasks /create /tn "CleanerResume" /tr "\\"{exe_path}\\" --silent-clean" /sc onevent '
        f'/ec System /mo "*[System[Provider[@Name=\'Microsoft-Windows-Power-Troubleshooter\'] and (EventID=1)]]" /rl highest /f',
        shell=True
    )