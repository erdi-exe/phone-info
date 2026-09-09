# Phone Info

A Termux toolkit for Android: full device report, live info, network tests, and small tools.

It only reads this device. Nothing is uploaded unless you use Public IP or Speed estimate, which contact public test servers.

## Menu

1. Full device report
2. Full device report + every `getprop` line
3. Info
   - Live CPU / RAM
   - Temperatures
   - Installed apps
   - Uptime / last boot
4. Network
   - Ping test with S to F class
   - Public IP
   - Speed estimate
   - Wi-Fi signal
5. Tools
   - Password generator
   - QR code
   - Clipboard
   - Notes
   - File / folder size
0. Exit

## Requirements

- Android phone
- [Termux](https://termux.dev) from F-Droid or the official GitHub release
- Python 3 inside Termux

`requirements.txt` has no pip packages.

Optional:

```bash
pkg install termux-api qrencode
```

Also install the **Termux:API** Android app if you want Wi-Fi signal, clipboard, and better battery JSON.

## How to run in Termux

### 1. Install Termux

Install Termux from F-Droid or the official Termux GitHub releases.

### 2. Update packages

```bash
pkg update
pkg upgrade
```

### 3. Install Python and Git

```bash
pkg install python git
```

### 4. Download this project

```bash
cd ~
git clone https://github.com/erdi-exe/phone-info.git
cd phone-info
```

If you already cloned it:

```bash
cd ~/phone-info
git pull
```

### 5. Install requirements

```bash
pip install -r requirements.txt
```

### 6. Run

```bash
python phone_info.py
```

### 7. Pick a menu number

Use `1` to `5`, or `0` to exit.

## Notes

- Some values say `unknown` if Android blocks them. That is normal without root.
- Live CPU / RAM stops with `Ctrl+C`.
- Notes are saved to `notes.txt` in this folder.
