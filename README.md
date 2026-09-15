# Phone Info v2.0.0

A Termux toolkit for Android: device report, info, network tests, system tools, and Termux:API helpers.

## What changed in v2.0.0

- Faster device reports (`getprop` loaded once, not hundreds of times)
- More stable startup on Termux
- Safer live CPU / RAM / battery screens
- Clearer exit with `0`, `q`, or Ctrl+C (Volume Down + C)
- Process list works better on Android
- Shows version in the menu

## Update on Termux

```bash
cd ~/phone-info
git pull
python phone_info.py
```

## First install

```bash
pkg update
pkg install python git termux-api
cd ~
git clone https://github.com/erdi-exe/phone-info.git
cd phone-info
pip install -r requirements.txt
python phone_info.py
```

Also install the **Termux:API** Android app for camera, torch, Wi-Fi signal, clipboard, and notifications.

## Menu

1. Full device report
2. Full report + every getprop
3. Info
4. Network
5. Tools
6. System
7. Phone / Termux:API
0. Exit
