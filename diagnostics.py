import platform
import socket
import time
import psutil
import datetime


def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def get_cpu_info():
    freq = psutil.cpu_freq()
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "usage_percent": psutil.cpu_percent(interval=1),
        "frequency_mhz": round(freq.current, 2) if freq else "N/A",
        "frequency_max_mhz": round(freq.max, 2) if freq else "N/A",
    }


def get_ram_info():
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "total_gb": round(ram.total / (1024 ** 3), 2),
        "used_gb": round(ram.used / (1024 ** 3), 2),
        "free_gb": round(ram.available / (1024 ** 3), 2),
        "usage_percent": ram.percent,
        "swap_total_gb": round(swap.total / (1024 ** 3), 2),
        "swap_used_gb": round(swap.used / (1024 ** 3), 2),
        "swap_percent": swap.percent,
    }


def get_disk_info():
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "free_gb": round(usage.free / (1024 ** 3), 2),
                "usage_percent": usage.percent,
            })
        except PermissionError:
            continue
    return disks


def get_network_info():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "Unavailable"

    interfaces = []
    for name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                interfaces.append({"interface": name, "ip": addr.address, "netmask": addr.netmask})

    stats = psutil.net_io_counters()
    return {
        "primary_ip": ip,
        "interfaces": interfaces,
        "bytes_sent_mb": round(stats.bytes_sent / (1024 ** 2), 2),
        "bytes_recv_mb": round(stats.bytes_recv / (1024 ** 2), 2),
    }


def get_battery_info():
    battery = psutil.sensors_battery()
    if battery is None:
        return {"available": False}

    if battery.secsleft == psutil.POWER_TIME_UNLIMITED:
        time_left = "Unlimited (AC)"
    elif battery.secsleft == psutil.POWER_TIME_UNKNOWN or battery.secsleft < 0:
        time_left = "Unknown"
    else:
        time_left = f"{round(battery.secsleft / 60, 1)} min"

    return {
        "available": True,
        "percent": battery.percent,
        "plugged_in": battery.power_plugged,
        "time_left": time_left,
    }


def get_boot_info():
    boot_time = psutil.boot_time()
    boot_dt = datetime.datetime.fromtimestamp(boot_time)
    uptime = datetime.datetime.now() - boot_dt
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes = remainder // 60
    return {
        "boot_time": boot_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": f"{hours}h {minutes}m",
    }


def get_top_processes():
    # First pass: prime cpu_percent (returns 0.0 on first call)
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        pass
    time.sleep(0.5)

    # Second pass: now cpu_percent returns real values
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    processes = [p for p in processes if p['cpu_percent'] is not None]
    processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
    return processes[:10]


def get_temperatures():
    """Return temperature sensor data. Returns empty dict on Windows
    (psutil.sensors_temperatures is not available on Windows)."""
    if not hasattr(psutil, "sensors_temperatures"):
        return {}
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return {}
        result = {}
        for name, entries in temps.items():
            result[name] = [{"label": e.label or "Core", "current": e.current, "high": e.high, "critical": e.critical} for e in entries]
        return result
    except (AttributeError, OSError):
        return {}


def collect_all():
    return {
        "system": get_system_info(),
        "cpu": get_cpu_info(),
        "ram": get_ram_info(),
        "disks": get_disk_info(),
        "network": get_network_info(),
        "battery": get_battery_info(),
        "boot": get_boot_info(),
        "processes": get_top_processes(),
        "temperatures": get_temperatures(),
    }