# Phone Info

A Termux tool that prints detailed info about your Android phone, with ASCII art and a GitHub banner.

It only reads this device. Nothing is uploaded or saved.

## What it shows

- Brand, model, manufacturer, board, hardware
- Android version, SDK, security patch, build fingerprint
- Kernel, uptime, CPU cores and frequencies
- RAM and swap
- Storage for `/`, home, and `/sdcard`
- Battery status
- Network and local IP
- Display size and density
- Extra build flags
- Option 2 also dumps every `getprop` line

## Requirements

- Android phone
- [Termux](https://termux.dev) (install from F-Droid or the official GitHub release, not the old Play Store copy)
- Python 3 inside Termux

`requirements.txt` has no pip packages. The script uses only Python built-ins.

Optional: better battery details

```bash
pkg install termux-api
```

Also install the **Termux:API** Android app if you use that package.

## How to run in Termux

### 1. Install Termux

Install Termux from F-Droid or the official Termux GitHub releases.

### 2. Open Termux and update packages

```bash
pkg update
pkg upgrade
```

Type `y` if it asks.

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

### 5. Install requirements

```bash
pip install -r requirements.txt
```

This step is safe even though there are no pip packages yet.

### 6. Run the tool

```bash
python phone_info.py
```

### 7. Use the menu

- `1` = full device report
- `2` = full report + every `getprop` line
- `0` = exit

## Update later

```bash
cd ~/phone-info
git pull
```

## Notes

- Some lines may say `unknown` if Android blocks them. That is normal without root.
- Colors and the GitHub box need a normal Termux session, not a broken terminal.
