import psutil
import platform

def get_ram_info():
    """Get RAM usage information"""
    ram = psutil.virtual_memory()
    used_gb = ram.used / (1024**3)
    total_gb = ram.total / (1024**3)
    percent = ram.percent
    return f"{percent}% used ({used_gb:.1f} GB of {total_gb:.1f} GB)"

def get_battery_info():
    """Get battery percentage and status"""
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        if battery.power_plugged:
            return f"{percent}% (plugged in, charging)"
        else:
            return f"{percent}% (on battery)"
    return "No battery detected (desktop PC)"

def get_cpu_info():
    """Get CPU usage percentage"""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    return f"{cpu_percent}%"

def get_system_summary():
    """Get all system info at once"""
    ram = get_ram_info()
    cpu = get_cpu_info()
    battery = get_battery_info()
    return f"CPU: {cpu}\nRAM: {ram}\nBattery: {battery}"