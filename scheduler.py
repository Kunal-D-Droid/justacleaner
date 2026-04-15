import threading
import time
import subprocess

def clear_all_tasks():
    for tn in ['CleanerInterval', 'CleanerLite', 'CleanerResume']:
        subprocess.run(['schtasks', '/delete', '/tn', tn, '/f'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

def schedule_hours(hours, exe_path):
    clear_all_tasks()
    cmd = ['schtasks', '/create', '/tn', 'CleanerInterval', '/tr', f'"{exe_path}" --silent-clean', '/sc', 'HOURLY', '/mo', str(hours), '/rl', 'highest', '/f']
    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

def enable_startup(exe_path):
    clear_all_tasks()
    cmd = ['schtasks', '/create', '/tn', 'CleanerLite', '/tr', f'"{exe_path}" --silent-clean', '/sc', 'onlogon', '/rl', 'highest', '/f']
    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

def enable_resume(exe_path):
    clear_all_tasks()
    mo_query = '*[System[Provider[@Name=\'Microsoft-Windows-Power-Troubleshooter\'] and (EventID=1)]]'
    cmd = ['schtasks', '/create', '/tn', 'CleanerResume', '/tr', f'"{exe_path}" --silent-clean', '/sc', 'onevent', '/ec', 'System', '/mo', mo_query, '/rl', 'highest', '/f']
    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)