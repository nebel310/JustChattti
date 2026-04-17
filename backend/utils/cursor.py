import base64
from datetime import datetime
from typing import Tuple




def encode_cursor(created_at: datetime, message_id: int) -> str:
    raw = f"{created_at.isoformat()}|{message_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()

def decode_cursor(cursor: str) -> Tuple[datetime, int]:
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    date_str, id_str = raw.split("|")
    created_at = datetime.fromisoformat(date_str)
    return created_at, int(id_str)