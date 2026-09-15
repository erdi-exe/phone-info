# Phone Info

**v2.0.0** — a Termux toolkit that reads your Android phone and runs useful local tools.

Made by [erdi-exe](https://github.com/erdi-exe)

---

## What it is

Phone Info is a Python menu for Termux. It shows device details, network checks, system tools, and Termux:API phone helpers.

It only works on the phone you run it on. It does not send your data to a server.

---

## Features

### Reports
- Full device report (brand, model, Android build, CPU, RAM, storage, battery, network, display)
- Optional dump of every `getprop` value

### Info
- Live CPU / RAM bars
- Temperatures
- Installed app counts
- Uptime and last boot

### Network
- Ping test with S–F class
- Public IP
- Speed estimate
- Wi-Fi signal
- Port check
- DNS lookup
- Traceroute
- Download a file

### Tools
- Password generator
- QR code
- Clipboard
- Notes
- File / folder size

### System
- Process list
- Kill process
- Termux cache / downloads cleaner
- Screen brightness
- Keep awake

### Phone / Termux:API
- Take a photo
- Live battery bar
- Notification
- Share text
- Vibrate
- Torch
- One-shot location

---

## Install on Termux

1. Install Termux from F-Droid or the official Termux GitHub release.
2. Open Termux and run:

```bash
pkg update
pkg upgrade
pkg install python git
cd ~
git clone https://github.com/erdi-exe/phone-info.git
cd phone-info
pip install -r requirements.txt
python phone_info.py
```

### Optional packages

```bash
pkg install termux-api qrencode traceroute
```

Also install the **Termux:API** Android app if you want camera, torch, Wi-Fi signal, clipboard, notifications, brightness, and location.

---

## Update

```bash
cd ~/phone-info
git pull
python phone_info.py
```

---

## How to use

```bash
python phone_info.py
```

Menu:

| Key | Section |
| --- | --- |
| 1 | Full device report |
| 2 | Full report + every getprop |
| 3 | Info |
| 4 | Network |
| 5 | Tools |
| 6 | System |
| 7 | Phone / Termux:API |
| 0 | Exit |

Exit with `0`, `q`, or `Ctrl+C` (Volume Down + C on many phones).

---

## Requirements

- Android phone
- Termux
- Python 3

No pip packages are required. `requirements.txt` is included for the install step.

---

## Notes

- Some values may show `unknown` if Android blocks them. That is normal without root.
- Live screens stop with `Ctrl+C`.
- Notes are saved to `notes.txt` in the project folder.
- Downloads go to `~/downloads`.

---

## Links

- Repo: https://github.com/erdi-exe/phone-info
- Latest release: https://github.com/erdi-exe/phone-info/releases/tag/v2.0.0
- Profile: https://github.com/erdi-exe
