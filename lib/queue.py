from typing import *

class QueueChannel:
    def __init__(self, channel_id: int, admin_role_id: int, button: Dict[AnyStr, int | AnyStr], block_conditions: List[]):
        