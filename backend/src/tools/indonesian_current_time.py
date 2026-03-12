from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Literal
from strands import tool


INDONESIA_TIMEZONES = {
    "WIB": ZoneInfo("Asia/Jakarta"),
    "WITA": ZoneInfo("Asia/Makassar"),
    "WIT": ZoneInfo("Asia/Jayapura"),
}

@tool
def indonesian_current_time(zone: Literal["WIB", "WITA", "WIT"] = "WIB") -> str:
    """
    Get current time in Indonesian timezone.
    Args:
        zone: Indonesian timezone
            - WIB (Western Indonesia Time): UTC+7
            - WITA (Central Indonesia Time): UTC+8  
            - WIT (Eastern Indonesia Time): UTC+9
    """
    tz = INDONESIA_TIMEZONES[zone]
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S") + f" {zone}"