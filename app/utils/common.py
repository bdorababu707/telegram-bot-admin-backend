import uuid
import time

async def generate_uuid() -> str:
    return str(uuid.uuid4())

async def current_time() -> int:
    return int(time.time())