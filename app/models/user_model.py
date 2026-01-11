from datetime import datetime
import time

def user_document_from_line(profile: dict):
    now = int(time.time())
    return {
        "line_id": profile["userId"],
        "display_name": profile.get("displayName"),
        "picture_url": profile.get("pictureUrl"),
        "role": "owner",
        "is_registered": False,
        "created_at": now,
        "updated_at": now
    }