# Phone Info | https://github.com/erdi-exe
# For Termux on Android. Copy this file to your phone, then run:
#   python phone_info.py

import os
import platform
import re
import shutil
import socket
import subprocess
import time


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


def run(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=8,
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


def menu():
    show_art()
    print("1. Full device report")
    print("2. Full device report + every getprop line")
    print("0. Exit")
    print()
    choice = input("Choose: ").strip()
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
    if include_all_props:
        all_props()
    print()
    github_box(flash=False)


def main():
    while True:
        os.system("clear")
        choice = menu()
        if choice == "1":
            full_report(False)
            input("\nPress Enter to go back...")
        elif choice == "2":
            full_report(True)
            input("\nPress Enter to go back...")
        elif choice == "0":
            print("Bye.")
            break
        else:
            print("Pick 1, 2, or 0.")
            time.sleep(1)


if __name__ == "__main__":
    main()
