import os
import shutil
import subprocess
import time

def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

# ---------------- SYSTEM CLEAN ----------------

def clean_temp():
    run_cmd('powershell -Command "Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue"')

def clean_windows_temp():
    path = "C:\\Windows\\Temp"
    if os.path.exists(path):
        run_cmd(f'powershell -Command "Remove-Item -Path \'{path}\\*\' -Recurse -Force -ErrorAction SilentlyContinue"')

def clean_recycle_bin():
    run_cmd("powershell Clear-RecycleBin -Force")

def clean_prefetch():
    path = "C:\\Windows\\Prefetch"
    if os.path.exists(path):
        run_cmd(f'powershell -Command "Remove-Item -Path \'{path}\\*\' -Recurse -Force -ErrorAction SilentlyContinue"')

def clean_recent():
    recent = os.environ.get("APPDATA") + "\\Microsoft\\Windows\\Recent"
    if os.path.exists(recent):
        run_cmd(f'powershell -Command "Remove-Item -Path \'{recent}\\*\' -Recurse -Force -ErrorAction SilentlyContinue"')

def clean_downloads():
    downloads = os.path.join(os.environ.get("USERPROFILE"), "Downloads")
    if os.path.exists(downloads):
        run_cmd(f'powershell -Command "Remove-Item -Path \'{downloads}\\*\' -Recurse -Force -ErrorAction SilentlyContinue"')



# ---------------- DOWNLOAD CLEAN (SAFE) ----------------



def remove_vpns():
    vpns = ["tailscale", "nordvpn", "protonvpn"]

    for vpn in vpns:
        run_cmd(f"winget uninstall {vpn} -h")

    # Clean app data left behind by VPNs
    local_appdata = os.environ.get("LOCALAPPDATA")
    program_data = os.environ.get("PROGRAMDATA")
    if local_appdata and program_data:
        paths_to_clear = [
            os.path.join(local_appdata, "Tailscale"),
            os.path.join(program_data, "Tailscale")
        ]
        for path in paths_to_clear:
            if os.path.exists(path):
                run_cmd(f'powershell -Command "Remove-Item -Path \'{path}\' -Recurse -Force -ErrorAction SilentlyContinue"')

# ---------------- OUTLOOK CLEAN ----------------

def clean_outlook():
    run_cmd("cmdkey /list | findstr MicrosoftOffice > creds.txt")
    run_cmd("cmdkey /delete:MicrosoftOffice")

# ---------------- DEEP PRIVACY CLEAN ----------------

def run_deep_privacy_clean():
    run_cmd("ipconfig /flushdns")
    run_cmd('powershell -Command "Set-Clipboard -Value $null"')
    run_cmd('powershell -Command "wevtutil el | Foreach-Object {wevtutil cl $_} 2>$null"')
    run_cmd('powershell -Command "Remove-VpnConnection -Name * -Force -ErrorAction SilentlyContinue"')
    run_cmd('powershell -Command "Clear-ItemProperty -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU\' -Name * -ErrorAction SilentlyContinue"')
    run_cmd('powershell -Command "Clear-ItemProperty -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths\' -Name * -ErrorAction SilentlyContinue"')

# ---------------- MAIN CLEAN ----------------

def run_clean(do_system=True, do_downloads=True, do_vpn=True, do_outlook=True, do_deep=True):
    if do_system:
        clean_temp()
        clean_windows_temp()
        clean_prefetch()
        clean_recycle_bin()
        clean_recent()

    if do_downloads:
        clean_downloads()

    if do_vpn:
        remove_vpns()
        
    if do_outlook:
        clean_outlook()
        
    if do_deep:
        run_deep_privacy_clean()