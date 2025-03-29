import pytz
from datetime import datetime

ekb_tz = pytz.timezone('Asia/Yekaterinburg')

async def get_current_ekb_time():
    return datetime.now(ekb_tz).replace(tzinfo=None)

async def convert_to_readable_ekb_time(incoming_time: datetime) -> str:
    return datetime.fromisoformat(str(incoming_time)).astimezone(ekb_tz).strftime("%Y-%m-%d %H:%M")
