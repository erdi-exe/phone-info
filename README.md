# Phone Info
#Not Finished Fully, Still In Development
#Fixed some issues just not fully finished, still need to do some more work on it

A Termux toolkit for Android: device report, info, network tests, system tools, and Termux:API phone helpers.

## Menu

1. Full device report
2. Full device report + every `getprop` line
3. Info
4. Network
5. Tools
6. System
7. Phone / Termux:API
0. Exit

### System
- Process list
- Kill process
- Termux cache / downloads cleaner
- Screen brightness
- Keep awake

### Network
- Ping (S to F), public IP, speed estimate, Wi-Fi signal
- Port check, DNS lookup, traceroute, download file

### Phone / Termux:API
- Photo, live battery bar, notification, share text
- Vibrate, torch, one-shot location

## How to update and run in Termux

```bash
cd ~/phone-info
git pull
pip install -r requirements.txt
python phone_info.py
```

First-time install:

```bash
pkg update
pkg upgrade
pkg install python git termux-api traceroute qrencode
cd ~
git clone https://github.com/erdi-exe/phone-info.git
cd phone-info
pip install -r requirements.txt
python phone_info.py
```

Also install the **Termux:API** Android app for camera, torch, location, brightness, share, and notifications.

Exit with `0` at the main menu, or `Ctrl+C` (Volume Down + C on many phones).
