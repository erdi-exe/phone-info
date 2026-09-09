# Phone Info | https://github.com/erdi-exe
# For Termux on Android. Copy this file to your phone, then run:
#   python phone_info.py

import json
import os
import platform
import secrets
import shutil
import socket
import string
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path


GITHUB = "https://github.com/erdi-exe"

ART = r"""
 ____  _                      ___        __       
|  _ \| |__   ___  _ __   ___|_ _|_ __  / _| ___  
| |_) | '_ \ / _ \| '_ \ / _ \| || '_ \| |_ / _ \ 
|  __/| | | | (_) | | | |  __/| || | | |  _| (_) |
|_|   |_| |_|\___/|_| |_|\___|___|_| |_|_|  \___/ 
"""


def paint(text, code):
    return f"\033[{code}m{text}\033[0m"


def github_box(flash=False):
    """Fancy framed GitHub link for Termux."""
    label = " github.com/erdi-exe "
    link = " " + GITHUB + " "
    width = max(len(label), len(link))
    label = label.center(width)
    link = link.center(width)
    top = "╔" + "═" * width + "╗"
    mid = "╠" + "═" * width + "╣"
    bot = "╚" + "═" * width + "╝"
    empty = "║" + " " * width + "║"

    try:
        cols = os.get_terminal_size().columns
    except OSError:
        cols = 40
    pad = " " * max(0, (cols - len(top)) // 2)

    lines_on = [
        paint(pad + top, "96"),
        paint(pad + "║", "96") + paint(label, "95;1") + paint("║", "96"),
        paint(pad + mid, "96"),
        paint(pad + "║", "96") + paint(link, "92") + paint("║", "96"),
        paint(pad + bot, "96"),
    ]
    lines_off = [
        paint(pad + top, "90"),
        paint(pad + empty, "90"),
        paint(pad + mid, "90"),
        paint(pad + empty, "90"),
        paint(pad + bot, "90"),
    ]

    if flash:
        for tick in range(8):
            shown = lines_on if tick % 2 == 0 else lines_off
            print("\n".join(shown))
            time.sleep(0.18)
            print(f"\033[{len(shown)}A", end="")
        print("\n".join(lines_on))
    else:
        print("\n".join(lines_on))


def play_intro():
    os.system("clear")
    print(ART)
    print()
    github_box(flash=True)
    time.sleep(0.4)
    os.system("clear")


play_intro()


def run(command, timeout=8):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return (result.stdout or result.stderr or "").strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read().strip()
    except OSError:
        return ""


def getprop(name):
    return run(["getprop", name])


def section(title):
    print()
    print(title)
    print("-" * 44)


def show(label, value):
    if value is None:
        value = "unknown"
    text = str(value).strip()
    if not text:
        text = "unknown"
    print(f"{label}: {text}")


def gb(num_bytes):
    return round(num_bytes / (1024 ** 3), 2)


def show_art():
    print(ART)
    print()
    github_box(flash=False)
    print()


def identity():
    section("Device")
    show("Brand", getprop("ro.product.brand"))
    show("Manufacturer", getprop("ro.product.manufacturer"))
    show("Model", getprop("ro.product.model"))
    show("Device", getprop("ro.product.device"))
    show("Product", getprop("ro.product.name"))
    show("Board", getprop("ro.product.board"))
    show("Hardware", getprop("ro.hardware"))
    show("Platform", getprop("ro.board.platform"))
    show("Serial", getprop("ro.serialno") or getprop("ril.serialnumber"))


def android_build():
    section("Android")
    show("Version", getprop("ro.build.version.release"))
    show("SDK", getprop("ro.build.version.sdk"))
    show("Codename", getprop("ro.build.version.codename"))
    show("Security patch", getprop("ro.build.version.security_patch"))
    show("Build ID", getprop("ro.build.id"))
    show("Build display", getprop("ro.build.display.id"))
    show("Build type", getprop("ro.build.type"))
    show("Build tags", getprop("ro.build.tags"))
    show("Build date", getprop("ro.build.date"))
    show("Fingerprint", getprop("ro.build.fingerprint"))
    show("Incremental", getprop("ro.build.version.incremental"))
    show("Baseband", getprop("gsm.version.baseband"))
    show("Bootloader", getprop("ro.bootloader"))
    show("ABI", getprop("ro.product.cpu.abi"))
    show("ABI list", getprop("ro.product.cpu.abilist"))
    show("Locale", getprop("persist.sys.locale") or getprop("ro.product.locale"))
    show("Timezone", getprop("persist.sys.timezone"))
    show("Treble", getprop("ro.treble.enabled"))
    show("A/B update", getprop("ro.build.ab_update"))
    show("SELinux", run(["getenforce"]) or getprop("ro.build.selinux"))


def kernel_info():
    section("Kernel")
    show("System", platform.system())
    show("Node", platform.node())
    show("Release", platform.release())
    show("Version", platform.version())
    show("Machine", platform.machine())
    show("Processor", platform.processor() or "unknown")
    show("Uname", run(["uname", "-a"]))
    show("Uptime", run(["uptime"]))


def cpu_info():
    section("CPU")
    text = read_file("/proc/cpuinfo")
    cores = text.count("processor")
    show("Logical cores", cores or os.cpu_count())

    names = []
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key in ("model name", "hardware", "processor") and value and value not in names:
            if key == "processor" and value.isdigit():
                continue
            names.append(value)
        if key == "bogo mips" and value:
            show("BogoMIPS", value)

    if names:
        show("CPU name", names[0])
        if len(names) > 1:
            show("Also listed", ", ".join(names[1:4]))

    freqs = []
    for index in range(cores or 8):
        path = f"/sys/devices/system/cpu/cpu{index}/cpufreq/scaling_cur_freq"
        raw = read_file(path)
        if raw.isdigit():
            freqs.append(int(raw) / 1000)
    if freqs:
        show("Current MHz", ", ".join(str(int(f)) for f in freqs))

    max_freq = read_file("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")
    min_freq = read_file("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq")
    if max_freq.isdigit():
        show("Max MHz", int(max_freq) / 1000)
    if min_freq.isdigit():
        show("Min MHz", int(min_freq) / 1000)

    gov = read_file("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    show("Governor", gov or "unknown")


def memory_info():
    section("Memory")
    text = read_file("/proc/meminfo")
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        number = value.strip().split()[0]
        if number.isdigit():
            values[key] = int(number) * 1024

    show("RAM total (GB)", gb(values.get("MemTotal", 0)) if "MemTotal" in values else "unknown")
    show("RAM free (GB)", gb(values.get("MemFree", 0)) if "MemFree" in values else "unknown")
    show("RAM available (GB)", gb(values.get("MemAvailable", 0)) if "MemAvailable" in values else "unknown")
    show("Buffers (GB)", gb(values.get("Buffers", 0)) if "Buffers" in values else "unknown")
    show("Cached (GB)", gb(values.get("Cached", 0)) if "Cached" in values else "unknown")
    show("Swap total (GB)", gb(values.get("SwapTotal", 0)) if "SwapTotal" in values else "unknown")
    show("Swap free (GB)", gb(values.get("SwapFree", 0)) if "SwapFree" in values else "unknown")


def storage_info():
    section("Storage")
    for path in ("/", os.path.expanduser("~"), "/sdcard", "/storage/emulated/0"):
        if not os.path.exists(path):
            continue
        try:
            usage = shutil.disk_usage(path)
        except OSError:
            continue
        show(
            f"Path {path}",
            f"total {gb(usage.total)} GB, used {gb(usage.used)} GB, free {gb(usage.free)} GB",
        )

    df = run(["df", "-h"])
    if df:
        print()
        print("df -h")
        for line in df.splitlines()[:20]:
            print(" ", line)


def battery_info():
    section("Battery")
    api = run(["termux-battery-status"])
    if api:
        print(api)
        return

    base = "/sys/class/power_supply"
    if not os.path.isdir(base):
        show("Battery", "unknown")
        return

    for name in sorted(os.listdir(base)):
        folder = os.path.join(base, name)
        if not os.path.isdir(folder):
            continue
        kind = read_file(os.path.join(folder, "type")).lower()
        if "battery" not in kind and "battery" not in name.lower():
            continue
        show("Name", name)
        show("Status", read_file(os.path.join(folder, "status")))
        show("Health", read_file(os.path.join(folder, "health")))
        show("Technology", read_file(os.path.join(folder, "technology")))
        capacity = read_file(os.path.join(folder, "capacity"))
        show("Charge (%)", capacity)
        voltage = read_file(os.path.join(folder, "voltage_now"))
        if voltage.isdigit():
            show("Voltage (V)", round(int(voltage) / 1000000, 2))
        temp = read_file(os.path.join(folder, "temp"))
        if temp.isdigit():
            show("Temp (C)", round(int(temp) / 10, 1))
        current = read_file(os.path.join(folder, "current_now"))
        if current.lstrip("-").isdigit():
            show("Current (mA)", round(int(current) / 1000, 1))
        return

    show("Battery", "unknown")


def network_info():
    section("Network")
    show("Hostname", socket.gethostname())
    show("Wi-Fi SSID", getprop("wifi.interface") or "unknown")
    show("Operator", getprop("gsm.operator.alpha") or getprop("gsm.sim.operator.alpha"))
    show("Network type", getprop("gsm.network.type"))
    show("Country", getprop("gsm.operator.iso-country") or getprop("gsm.sim.operator.iso-country"))
    show("Airplane mode", getprop("persist.radio.airplane_mode_on") or getprop("airplane_mode_on"))

    ip = run(["ip", "-4", "addr", "show"])
    if not ip:
        ip = run(["ifconfig"])
    if ip:
        print()
        print("Addresses")
        for line in ip.splitlines():
            line = line.strip()
            if "inet" in line or line.startswith("wlan") or line.startswith("rmnet") or line.startswith("eth"):
                print(" ", line)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("1.1.1.1", 80))
        show("Primary IPv4", sock.getsockname()[0])
        sock.close()
    except OSError:
        show("Primary IPv4", "offline")


def display_info():
    section("Display")
    show("LCD density", getprop("ro.sf.lcd_density"))
    show("OpenGL", getprop("ro.opengles.version"))
    size = run(["wm", "size"])
    density = run(["wm", "density"])
    show("wm size", size.replace("Physical size: ", "") if size else "unknown")
    show("wm density", density.replace("Physical density: ", "") if density else "unknown")


def sensors_and_extra():
    section("Extra")
    show("Camera count", getprop("ro.camera.count") or getprop("persist.camera.count"))
    show("First API level", getprop("ro.product.first_api_level"))
    show("Vendor", getprop("ro.product.vendor.model") or getprop("ro.vendor.product.model"))
    show("System name", getprop("ro.product.system.name"))
    show("ODM", getprop("ro.product.odm.model"))
    show("Boot mode", getprop("ro.bootmode"))
    show("Verified boot", getprop("ro.boot.verifiedbootstate"))
    show("Flash locked", getprop("ro.boot.flash.locked"))
    show("USB config", getprop("sys.usb.config"))
    show("ADB", getprop("sys.usb.state"))
    show("Rooted (su)", "yes" if shutil.which("su") else "no / hidden")
    show("Termux home", os.path.expanduser("~"))
    show("Python", platform.python_version())
    show("PID", os.getpid())
    show("Time", time.strftime("%Y-%m-%d %H:%M:%S"))


def all_props():
    section("All getprop values")
    text = run(["getprop"])
    if not text:
        show("getprop", "not available")
        return
    lines = text.splitlines()
    print(f"Total properties: {len(lines)}")
    print()
    for line in lines:
        print(line)


def bar(percent, width=28):
    percent = max(0, min(100, int(percent)))
    filled = int(width * percent / 100)
    return "[" + "#" * filled + "-" * (width - filled) + f"] {percent}%"


def mem_stats():
    text = read_file("/proc/meminfo")
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        number = value.strip().split()[0]
        if number.isdigit():
            values[key] = int(number)
    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", values.get("MemFree", 0))
    used = max(total - available, 0)
    percent = round(used * 100 / total) if total else 0
    return total, used, available, percent


def cpu_usage():
    def sample():
        line = read_file("/proc/stat").splitlines()[0]
        parts = [int(x) for x in line.split()[1:]]
        idle = parts[3] + (parts[4] if len(parts) > 4 else 0)
        total = sum(parts)
        return idle, total

    idle1, total1 = sample()
    time.sleep(0.25)
    idle2, total2 = sample()
    total_delta = total2 - total1
    idle_delta = idle2 - idle1
    if total_delta <= 0:
        return 0
    return round((1 - idle_delta / total_delta) * 100)


def live_monitor():
    os.system("clear")
    show_art()
    print("Live CPU / RAM")
    print("Press Ctrl+C to stop.")
    print()
    try:
        while True:
            cpu = cpu_usage()
            total, used, available, percent = mem_stats()
            print("\033[2K\r", end="")
            print(f"CPU {bar(cpu)}")
            print(f"RAM {bar(percent)}  {round(used/1024)} / {round(total/1024)} MB")
            print("\033[2A", end="", flush=True)
            time.sleep(0.75)
    except KeyboardInterrupt:
        print("\n\nStopped.")


def temperatures():
    section("Temperatures")
    found = False
    thermal = "/sys/class/thermal"
    if os.path.isdir(thermal):
        for name in sorted(os.listdir(thermal)):
            if not name.startswith("thermal_zone"):
                continue
            folder = os.path.join(thermal, name)
            temp = read_file(os.path.join(folder, "temp"))
            kind = read_file(os.path.join(folder, "type")) or name
            if temp.lstrip("-").isdigit():
                value = int(temp)
                celsius = value / 1000 if value > 200 else value / 10 if value > 80 else value
                show(kind, f"{celsius:.1f} C")
                found = True

    battery_temp = None
    base = "/sys/class/power_supply"
    if os.path.isdir(base):
        for name in os.listdir(base):
            temp = read_file(os.path.join(base, name, "temp"))
            if temp.isdigit():
                battery_temp = round(int(temp) / 10, 1)
                break
    if battery_temp is not None:
        show("Battery", f"{battery_temp} C")
        found = True

    api = run(["termux-battery-status"])
    if api and "temperature" in api:
        show("Termux battery JSON", api)
        found = True

    if not found:
        show("Temps", "unknown on this device")


def apps_info():
    section("Apps")
    user = run(["pm", "list", "packages", "-3"])
    system = run(["pm", "list", "packages", "-s"])
    all_apps = run(["pm", "list", "packages"])
    user_lines = [line for line in user.splitlines() if line.strip()]
    system_lines = [line for line in system.splitlines() if line.strip()]
    all_lines = [line for line in all_apps.splitlines() if line.strip()]
    show("User apps", len(user_lines) if user_lines else "unknown (needs pm)")
    show("System apps", len(system_lines) if system_lines else "unknown")
    show("Total packages", len(all_lines) if all_lines else "unknown")
    if user_lines:
        print()
        print("User packages")
        for line in user_lines[:40]:
            print(" ", line.replace("package:", ""))
        if len(user_lines) > 40:
            print(f"  ... and {len(user_lines) - 40} more")


def uptime_english():
    section("Uptime")
    raw = read_file("/proc/uptime").split()
    if not raw:
        show("Uptime", run(["uptime"]) or "unknown")
        return
    seconds = int(float(raw[0]))
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    show("Uptime", f"{days}d {hours}h {minutes}m {secs}s")
    boot = datetime.now() - timedelta(seconds=seconds)
    show("Last boot", boot.strftime("%Y-%m-%d %H:%M:%S"))


NOTES = {
    "S": "overkill",
    "A": "excellent",
    "B": "great",
    "C": "fine",
    "D": "playable",
    "E": "laggy",
    "F": "unusable",
}


def ping_class(avg_ms, lost, total=10):
    ladder = [
        (10, "S", "95"),
        (20, "A", "92"),
        (35, "B", "32"),
        (50, "C", "93"),
        (80, "D", "33"),
        (120, "E", "91"),
        (10**9, "F", "31"),
    ]
    if avg_ms is None or lost >= total:
        return "F", "31"
    grade, code = "F", "31"
    for limit, name, color in ladder:
        if avg_ms <= limit:
            grade, code = name, color
            break
    if lost > 0:
        order = "SABCDEF"
        colors = {"S": "95", "A": "92", "B": "32", "C": "93", "D": "33", "E": "91", "F": "31"}
        grade = order[min(order.index(grade) + 1, len(order) - 1)]
        code = colors[grade]
    return grade, code


def ping_tool():
    host = input("Host [1.1.1.1]: ").strip() or "1.1.1.1"
    print()
    print(f"Pinging {host} ten times...")
    print()
    times = []
    for attempt in range(1, 11):
        text = run(["ping", "-c", "1", "-W", "2", host])
        reply = "Request timed out."
        ms = None
        for line in text.splitlines():
            lower = line.lower()
            if "time=" in lower:
                reply = line.strip()
                piece = lower.split("time=", 1)[1]
                number = ""
                for char in piece:
                    if char.isdigit() or char == ".":
                        number += char
                    elif number:
                        break
                if number:
                    ms = float(number)
                break
            if "100% packet loss" in lower or "0 received" in lower:
                reply = "Request timed out."
        print(f"  {attempt}/10  {reply}")
        if ms is not None:
            times.append(ms)

    lost = 10 - len(times)
    avg = round(sum(times) / len(times)) if times else None
    grade, code = ping_class(avg, lost)
    print()
    if avg is None:
        print(paint(f"Class: F  {NOTES['F']}", code))
        return
    print(f"Average: {avg} ms    Lost: {lost}/10")
    print(paint(f"Class: {grade}  {NOTES[grade]}", code))


def public_ip():
    section("Public IP")
    urls = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
    ]
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=6) as response:
                ip = response.read().decode("utf-8", errors="replace").strip()
            if ip:
                show("Public IP", ip)
                show("Source", url)
                return
        except (urllib.error.URLError, TimeoutError, OSError):
            continue
    show("Public IP", "offline / blocked")


def speed_estimate():
    section("Speed estimate")
    print("Downloading a small test file...")
    url = "https://speed.cloudflare.com/__down?bytes=2000000"
    try:
        started = time.time()
        with urllib.request.urlopen(url, timeout=20) as response:
            data = response.read()
        elapsed = max(time.time() - started, 0.001)
        mb = len(data) / (1024 * 1024)
        mbps = (len(data) * 8) / elapsed / 1_000_000
        show("Downloaded", f"{mb:.2f} MB")
        show("Time", f"{elapsed:.2f} s")
        show("Estimate", f"{mbps:.1f} Mbps")
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        show("Speed test", f"failed ({error})")


def wifi_signal():
    section("Wi-Fi signal")
    info = run(["termux-wifi-connectioninfo"])
    if info:
        try:
            data = json.loads(info)
            show("SSID", data.get("ssid"))
            show("BSSID", data.get("bssid"))
            show("IP", data.get("ip"))
            show("Link speed", data.get("link_speed_mbps"))
            show("Frequency", data.get("frequency_mhz"))
            show("RSSI", data.get("rssi"))
            show("Network ID", data.get("network_id"))
            return
        except json.JSONDecodeError:
            print(info)
            return
    show("Wi-Fi", "install Termux:API and: pkg install termux-api")


def password_tool():
    section("Password generator")
    raw = input("Length [16]: ").strip() or "16"
    if not raw.isdigit() or int(raw) < 4:
        print("Use a number 4 or higher.")
        return
    length = min(int(raw), 128)
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = "".join(secrets.choice(alphabet) for _ in range(length))
    show("Password", password)


def qr_tool():
    section("QR code")
    text = input("Text or URL: ").strip()
    if not text:
        print("Nothing to encode.")
        return
    if shutil.which("qrencode"):
        print()
        print(run(["qrencode", "-t", "ANSIUTF8", text]))
        return
    print("qrencode is not installed.")
    print("In Termux run: pkg install qrencode")


def clipboard_tool():
    section("Clipboard")
    print("1. Show clipboard")
    print("2. Set clipboard")
    choice = input("Choose: ").strip()
    if choice == "1":
        text = run(["termux-clipboard-get"])
        show("Clipboard", text or "empty / Termux:API missing")
    elif choice == "2":
        text = input("New clipboard text: ")
        result = run(["termux-clipboard-set", text])
        show("Set", "done" if result == "" else result or "done")
    else:
        print("Cancelled.")


def notes_tool():
    section("Notes")
    path = Path(__file__).resolve().parent / "notes.txt"
    print("1. Read notes")
    print("2. Add a note")
    choice = input("Choose: ").strip()
    if choice == "1":
        if not path.exists():
            print("No notes yet.")
            return
        print()
        print(path.read_text(encoding="utf-8", errors="replace"))
    elif choice == "2":
        text = input("Note: ").strip()
        if not text:
            print("Empty note.")
            return
        stamp = time.strftime("%Y-%m-%d %H:%M")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{stamp}] {text}\n")
        show("Saved", str(path))
    else:
        print("Cancelled.")


def file_size_tool():
    section("File / folder size")
    target = input("Path: ").strip() or "."
    path = Path(target).expanduser()
    if not path.exists():
        print("Path not found.")
        return
    if path.is_file():
        size = path.stat().st_size
        show("File", str(path))
        show("Size", f"{size} bytes ({gb(size)} GB)")
        return
    total = 0
    files = 0
    for root, _, names in os.walk(path):
        for name in names:
            try:
                total += (Path(root) / name).stat().st_size
                files += 1
            except OSError:
                continue
    show("Folder", str(path))
    show("Files", files)
    show("Size", f"{total} bytes ({gb(total)} GB)")


def need_termux_api(command_name):
    if shutil.which(command_name):
        return True
    print(f"{command_name} was not found.")
    print("Install: pkg install termux-api")
    print("Also install the Termux:API Android app.")
    return False


def folder_size_bytes(path):
    total = 0
    count = 0
    path = Path(path)
    if not path.exists():
        return 0, 0
    if path.is_file():
        try:
            return path.stat().st_size, 1
        except OSError:
            return 0, 0
    for root, _, names in os.walk(path):
        for name in names:
            try:
                total += (Path(root) / name).stat().st_size
                count += 1
            except OSError:
                continue
    return total, count


def process_list_tool():
    section("Top processes")
    text = run(["ps", "-A", "-o", "PID,PCPU,PMEM,NAME"], timeout=10)
    if not text or "PID" not in text.upper():
        text = run(["ps", "-eo", "pid,pcpu,pmem,comm"], timeout=10)
    if not text:
        text = run(["ps", "-A"], timeout=10)
    if not text:
        print("Could not read process list.")
        return

    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    print("\n".join(lines[:25]))
    if len(lines) > 25:
        print(f"... {len(lines) - 25} more lines")

    print()
    print("Sorted peek (best effort):")
    rows = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 3:
            continue
        pid = parts[0]
        try:
            cpu = float(parts[1].replace("%", ""))
            mem = float(parts[2].replace("%", ""))
        except ValueError:
            continue
        name = " ".join(parts[3:]) if len(parts) > 3 else parts[-1]
        rows.append((cpu, mem, pid, name))
    rows.sort(key=lambda item: (item[0], item[1]), reverse=True)
    for cpu, mem, pid, name in rows[:12]:
        print(f"  PID {pid:>6}  CPU {cpu:5.1f}  MEM {mem:5.1f}  {name}")


def kill_process_tool():
    section("Kill process")
    print("Type a PID number, or part of a process name.")
    target = input("PID or name: ").strip()
    if not target:
        print("Cancelled.")
        return

    pids = []
    if target.isdigit():
        pids = [target]
    else:
        text = run(["ps", "-A"], timeout=10)
        for line in text.splitlines():
            if target.lower() in line.lower():
                parts = line.split()
                if parts and parts[0].isdigit():
                    pids.append(parts[0])
                    print(" ", line.strip())

    pids = list(dict.fromkeys(pids))
    if not pids:
        print("No matching process.")
        return

    print()
    print("Will send SIGTERM to:", ", ".join(pids))
    if input("Type yes to kill: ").strip().lower() != "yes":
        print("Cancelled.")
        return

    for pid in pids:
        ok = run(["kill", pid])
        show(f"kill {pid}", ok or "signal sent")


def termux_cleaner():
    section("Termux storage cleaner")
    home = Path.home()
    prefix = Path(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"))
    targets = [
        home / ".cache",
        home / "downloads",
        home / "Downloads",
        home / "storage" / "downloads",
        prefix / "var" / "cache",
        home / ".pip" / "cache",
        home / ".cache" / "pip",
    ]

    existing = []
    print("Safe folders only (Termux cache / downloads):")
    for path in targets:
        if not path.exists():
            continue
        size, count = folder_size_bytes(path)
        existing.append(path)
        print(f"  {path}  ({count} files, {gb(size)} GB)")

    if not existing:
        print("Nothing found to clean.")
        return

    print()
    if input("Type yes to delete these contents: ").strip().lower() != "yes":
        print("Cancelled.")
        return

    deleted = 0
    skipped = 0
    for folder in existing:
        if folder.is_file():
            try:
                folder.unlink()
                deleted += 1
            except OSError:
                skipped += 1
            continue
        for item in folder.iterdir():
            try:
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                deleted += 1
            except OSError:
                skipped += 1
    show("Deleted entries", deleted)
    show("Skipped", skipped)


def brightness_tool():
    section("Screen brightness")
    if not need_termux_api("termux-brightness"):
        return
    raw = input("Brightness 0-255 (or blank to skip): ").strip()
    if not raw:
        print("Cancelled.")
        return
    if not raw.isdigit() or not 0 <= int(raw) <= 255:
        print("Use a number from 0 to 255.")
        return
    out = run(["termux-brightness", raw])
    show("Brightness", out or raw)


def keep_awake_tool():
    section("Keep awake")
    if not need_termux_api("termux-wake-lock"):
        return
    print("1. Keep awake ON")
    print("2. Keep awake OFF")
    choice = input("Choose: ").strip()
    if choice == "1":
        out = run(["termux-wake-lock"])
        show("Wake lock", out or "on")
    elif choice == "2":
        out = run(["termux-wake-unlock"])
        show("Wake lock", out or "off")
    else:
        print("Cancelled.")


def port_check_tool():
    section("Port check")
    host = input("Host [1.1.1.1]: ").strip() or "1.1.1.1"
    raw = input("Port [443]: ").strip() or "443"
    if not raw.isdigit():
        print("Port must be a number.")
        return
    port = int(raw)
    started = time.time()
    try:
        with socket.create_connection((host, port), timeout=5):
            ms = round((time.time() - started) * 1000)
            show("Result", f"OPEN  {host}:{port}  ({ms} ms)")
    except OSError as error:
        show("Result", f"CLOSED / blocked  {host}:{port}")
        show("Detail", error)


def dns_lookup_tool():
    section("DNS lookup")
    host = input("Hostname [github.com]: ").strip() or "github.com"
    print()
    try:
        infos = socket.getaddrinfo(host, None)
        seen = []
        for info in infos:
            ip = info[4][0]
            if ip not in seen:
                seen.append(ip)
                show("Address", ip)
        if not seen:
            show("DNS", "no results")
    except socket.gaierror as error:
        show("DNS", error)

    dig = run(["dig", "+short", host], timeout=10)
    if dig:
        print()
        print("dig:")
        print(dig)
    host_cmd = run(["host", host], timeout=10)
    if host_cmd:
        print()
        print(host_cmd)


def traceroute_tool():
    section("Traceroute")
    host = input("Host [1.1.1.1]: ").strip() or "1.1.1.1"
    print()
    text = run(["traceroute", "-n", "-w", "2", "-q", "1", "-m", "20", host], timeout=60)
    if not text:
        text = run(["tracepath", "-n", host], timeout=60)
    if not text:
        print("Install traceroute: pkg install traceroute")
        print("Or: pkg install iputils")
        return
    print(text)
    hops = [line for line in text.splitlines() if line.strip() and not line.lower().startswith("traceroute")]
    show("Hop lines", len(hops))


def download_file_tool():
    section("Download file")
    url = input("URL: ").strip()
    if not url:
        print("Cancelled.")
        return
    default_name = url.rstrip("/").split("/")[-1] or "download.bin"
    if "?" in default_name:
        default_name = default_name.split("?", 1)[0] or "download.bin"
    name = input(f"Save as [{default_name}]: ").strip() or default_name
    folder = Path.home() / "downloads"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / name
    print()
    print(f"Saving to {target}")
    try:
        with urllib.request.urlopen(url, timeout=60) as response, target.open("wb") as handle:
            total = 0
            while True:
                chunk = response.read(1024 * 64)
                if not chunk:
                    break
                handle.write(chunk)
                total += len(chunk)
                print(f"\r  {gb(total)} GB downloaded...", end="", flush=True)
        print()
        show("Saved", str(target))
        show("Bytes", total)
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        print()
        show("Download", f"failed ({error})")


def camera_photo_tool():
    section("Camera photo")
    if not need_termux_api("termux-camera-photo"):
        return
    folder = Path.home() / "downloads"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"photo_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
    print("Opening camera...")
    out = run(["termux-camera-photo", str(target)], timeout=120)
    if target.exists():
        show("Saved", str(target))
        show("Size", f"{target.stat().st_size} bytes")
    else:
        show("Photo", out or "failed / permission denied")


def battery_live_bar():
    section("Live battery")
    if not need_termux_api("termux-battery-status"):
        return
    print("Press Ctrl+C to stop.")
    print()
    try:
        while True:
            raw = run(["termux-battery-status"], timeout=5)
            percent = 0
            status = "unknown"
            try:
                data = json.loads(raw)
                percent = int(data.get("percentage", 0))
                status = data.get("status", "unknown")
            except (json.JSONDecodeError, TypeError, ValueError):
                print(raw or "no battery data")
                return
            print("\033[2K\r", end="")
            print(f"Battery {bar(percent)}  {status}")
            print("\033[1A", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")


def notification_tool():
    section("Notification")
    if not need_termux_api("termux-notification"):
        return
    title = input("Title [Phone Info]: ").strip() or "Phone Info"
    content = input("Message: ").strip() or "Hello from Termux"
    out = run(["termux-notification", "--title", title, "--content", content])
    show("Notification", out or "sent")


def share_text_tool():
    section("Share text")
    if not need_termux_api("termux-share"):
        return
    text = input("Text to share: ").strip()
    if not text:
        print("Cancelled.")
        return
    out = run(["termux-share", "-a", "send", text], timeout=30)
    show("Share", out or "opened share sheet")


def vibrate_tool():
    section("Vibrate")
    if not need_termux_api("termux-vibrate"):
        return
    raw = input("Duration ms [300]: ").strip() or "300"
    if not raw.isdigit():
        print("Use a number.")
        return
    out = run(["termux-vibrate", "-d", raw])
    show("Vibrate", out or f"{raw} ms")


def torch_tool():
    section("Torch")
    if not need_termux_api("termux-torch"):
        return
    print("1. Torch ON")
    print("2. Torch OFF")
    choice = input("Choose: ").strip()
    if choice == "1":
        out = run(["termux-torch", "on"])
        show("Torch", out or "on")
    elif choice == "2":
        out = run(["termux-torch", "off"])
        show("Torch", out or "off")
    else:
        print("Cancelled.")


def location_tool():
    section("Location")
    if not need_termux_api("termux-location"):
        return
    print("Requesting one-shot location. Allow permission if Android asks.")
    raw = run(["termux-location", "-p", "network,gps", "-r", "once"], timeout=60)
    if not raw:
        print("No location returned.")
        return
    try:
        data = json.loads(raw)
        show("Latitude", data.get("latitude"))
        show("Longitude", data.get("longitude"))
        show("Altitude", data.get("altitude"))
        show("Accuracy", data.get("accuracy"))
        show("Provider", data.get("provider"))
        show("Speed", data.get("speed"))
        show("Bearing", data.get("bearing"))
    except json.JSONDecodeError:
        print(raw)


def pause():
    input("\nPress Enter to go back...")


def info_menu():
    while True:
        os.system("clear")
        show_art()
        print("Info")
        print("1. Live CPU / RAM")
        print("2. Temperatures")
        print("3. Installed apps")
        print("4. Uptime / last boot")
        print("0. Back")
        print()
        choice = input("Choose: ").strip()
        if choice == "1":
            live_monitor()
            pause()
        elif choice == "2":
            os.system("clear")
            show_art()
            temperatures()
            pause()
        elif choice == "3":
            os.system("clear")
            show_art()
            apps_info()
            pause()
        elif choice == "4":
            os.system("clear")
            show_art()
            uptime_english()
            pause()
        elif choice == "0":
            return


def system_menu():
    while True:
        os.system("clear")
        show_art()
        print("System")
        print("1. Process list")
        print("2. Kill process")
        print("3. Termux cache / downloads cleaner")
        print("4. Screen brightness")
        print("5. Keep awake")
        print("0. Back")
        print()
        choice = input("Choose: ").strip()
        if choice == "1":
            os.system("clear")
            show_art()
            process_list_tool()
            pause()
        elif choice == "2":
            os.system("clear")
            show_art()
            kill_process_tool()
            pause()
        elif choice == "3":
            os.system("clear")
            show_art()
            termux_cleaner()
            pause()
        elif choice == "4":
            os.system("clear")
            show_art()
            brightness_tool()
            pause()
        elif choice == "5":
            os.system("clear")
            show_art()
            keep_awake_tool()
            pause()
        elif choice == "0":
            return


def network_menu():
    while True:
        os.system("clear")
        show_art()
        print("Network")
        print("1. Ping test (S to F)")
        print("2. Public IP")
        print("3. Speed estimate")
        print("4. Wi-Fi signal")
        print("5. Port check")
        print("6. DNS lookup")
        print("7. Traceroute")
        print("8. Download file")
        print("0. Back")
        print()
        choice = input("Choose: ").strip()
        if choice == "1":
            os.system("clear")
            show_art()
            ping_tool()
            pause()
        elif choice == "2":
            os.system("clear")
            show_art()
            public_ip()
            pause()
        elif choice == "3":
            os.system("clear")
            show_art()
            speed_estimate()
            pause()
        elif choice == "4":
            os.system("clear")
            show_art()
            wifi_signal()
            pause()
        elif choice == "5":
            os.system("clear")
            show_art()
            port_check_tool()
            pause()
        elif choice == "6":
            os.system("clear")
            show_art()
            dns_lookup_tool()
            pause()
        elif choice == "7":
            os.system("clear")
            show_art()
            traceroute_tool()
            pause()
        elif choice == "8":
            os.system("clear")
            show_art()
            download_file_tool()
            pause()
        elif choice == "0":
            return


def phone_menu():
    while True:
        os.system("clear")
        show_art()
        print("Phone / Termux:API")
        print("1. Take photo")
        print("2. Live battery bar")
        print("3. Send notification")
        print("4. Share text")
        print("5. Vibrate")
        print("6. Torch on/off")
        print("7. Location once")
        print("0. Back")
        print()
        choice = input("Choose: ").strip()
        if choice == "1":
            os.system("clear")
            show_art()
            camera_photo_tool()
            pause()
        elif choice == "2":
            os.system("clear")
            show_art()
            battery_live_bar()
            pause()
        elif choice == "3":
            os.system("clear")
            show_art()
            notification_tool()
            pause()
        elif choice == "4":
            os.system("clear")
            show_art()
            share_text_tool()
            pause()
        elif choice == "5":
            os.system("clear")
            show_art()
            vibrate_tool()
            pause()
        elif choice == "6":
            os.system("clear")
            show_art()
            torch_tool()
            pause()
        elif choice == "7":
            os.system("clear")
            show_art()
            location_tool()
            pause()
        elif choice == "0":
            return


def tools_menu():
    while True:
        os.system("clear")
        show_art()
        print("Tools")
        print("1. Password generator")
        print("2. QR code")
        print("3. Clipboard")
        print("4. Notes")
        print("5. File / folder size")
        print("0. Back")
        print()
        choice = input("Choose: ").strip()
        if choice == "1":
            os.system("clear")
            show_art()
            password_tool()
            pause()
        elif choice == "2":
            os.system("clear")
            show_art()
            qr_tool()
            pause()
        elif choice == "3":
            os.system("clear")
            show_art()
            clipboard_tool()
            pause()
        elif choice == "4":
            os.system("clear")
            show_art()
            notes_tool()
            pause()
        elif choice == "5":
            os.system("clear")
            show_art()
            file_size_tool()
            pause()
        elif choice == "0":
            return


def menu():
    show_art()
    print("1. Full device report")
    print("2. Full device report + every getprop line")
    print("3. Info")
    print("4. Network")
    print("5. Tools")
    print("6. System")
    print("7. Phone / Termux:API")
    print("0. Exit")
    print()
    choice = input("Choose: ").strip().lower()
    return choice


def full_report(include_all_props=False):
    os.system("clear")
    show_art()
    print("Phone report")
    print("=" * 44)
    identity()
    android_build()
    kernel_info()
    cpu_info()
    memory_info()
    storage_info()
    battery_info()
    network_info()
    display_info()
    sensors_and_extra()
    uptime_english()
    temperatures()
    if include_all_props:
        all_props()
    print()
    github_box(flash=False)


def main():
    while True:
        try:
            os.system("clear")
            choice = menu()
            if choice == "1":
                full_report(False)
                pause()
            elif choice == "2":
                full_report(True)
                pause()
            elif choice == "3":
                info_menu()
            elif choice == "4":
                network_menu()
            elif choice == "5":
                tools_menu()
            elif choice == "6":
                system_menu()
            elif choice == "7":
                phone_menu()
            elif choice in {"0", "q", "quit", "exit"}:
                print("Bye.")
                break
            else:
                print("Pick a number from the menu.")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nBye.")
            break


if __name__ == "__main__":
    main()
