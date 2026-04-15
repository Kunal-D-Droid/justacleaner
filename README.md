# Just a Cleaner

### The Problem
We live our digital lives through our PC. Over months and years, Windows accumulates an astonishing amount of leftover data. Application installers dump files in the Temp folder and forget them. The system dynamically logs your clipboard history, caches your DNS requests, and intimately tracks your File Explorer paths. If you use a VPN for privacy, uninstalling it is rarely enough—they leave behind deep traces in your hidden AppData directories. 

You try to stay clean, but manually digging through Windows directories, executing PowerShell commands to wipe the DNS cache, or trusting random system optimization software that feels invasive and bloated just isn't the right way to manage your system. Managing system privacy and bloat is tedious, technical, and frankly exhausting.

### The Solution
I wanted a tool that does exactly what it promises—deep, intelligent system cleaning without the bloatware, without the gimmicks, and absolutely transparent about what it deletes. 

**Just a Cleaner** is a modern, lightweight Windows utility built to reclaim your privacy and storage. It eradicates temporary system bloat, aggressively wipes privacy-invasive logs (like your clipboard history and File Explorer registry activity), and securely removes leftover AppData from common VPN software. 

Run it once to reclaim your system, or enable the built-in native scheduler to automate it invisibly in the background.

## Features 

- **Deep System Purge:** Empties Windows Temp folders, Prefetch directories, Recent Items, and the Recycle bin.
- **Absolute Privacy Sweep:** Flushes the DNS cache, permanently wipes the native Windows Clipboard History, destroys File Explorer typed paths, and erases Windows Event Logs.
- **VPN Eradicator:** Uninstalls Tailscale, NordVPN, and ProtonVPN while wiping their hidden program data.
- **Downloads Wipe:** Optional quick-purge for your core Downloads folder.
- **Silent Automation:** Interfaces directly with the Windows Task Scheduler to clean your system automatically—every few hours, on system startup, or upon waking from sleep—all completely invisibly.

## Download & Installation

You can get the official setup wizard for Windows right here:

**[Download JustACleaner_Setup.exe](https://github.com/Kunal-D-Droid/justacleaner/releases/latest/download/JustACleaner_Setup.exe)** 

*(Alternatively, you can browse all versions in the [Releases](https://github.com/Kunal-D-Droid/justacleaner/releases) tab limit)*

The installer handles everything from extracting the core assets to preparing the scheduler configuration file automatically.

## Built With

- **Python**: Core scripting, subprocess execution, and system logic.
- **PyQt6**: A highly customized, beautifully fluid dark-mode user interface.
- **Windows Runtime API (WinRT) / PowerShell**: Direct integrations to control tasks and natively wipe clipboard histories deep in the OS layer.

## Open Source & Contributing

Just a Cleaner is fully open source. There are always new ways to improve system optimization and privacy scrubbing, and I openly welcome any and all contributions!

If you find a bug, have an idea for a new cleaning module, or generally see something in the codebase that can be optimized, your contributions are incredibly welcome. 

1. Fork the repository
2. Create an implementation branch (`git checkout -b feature/NewOptimization`)
3. Make your changes and test them
4. Commit your changes (`git commit -m 'Added advanced registry deep cleaning'`)
5. Open a Pull Request!

I am always happy to review and integrate useful optimizations that make this tool better for everyone. Let's keep our digital environments clean, secure, and fast.

---
*Open Source by [Kunal](https://www.kunaldas.tech)*
