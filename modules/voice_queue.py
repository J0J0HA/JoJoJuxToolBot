from collections import deque
from typing import Callable
import nextcord
from helpers import voice
from ._ import _


class Module(_(__name__)):
    def get_queue(self, channel_id: int) -> Callable:
        queue = []
        
        async def add_user_to_queue(member: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
            print(f"{member.name} in now in the queue")
            queue.append(member)
        
        async def remove_user_from_queue(member: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
            print(f"{member.name} left the queue")
            queue.remove(member)
            
        self.bot.add_listener(voice.on_moveto_x(channel_id, add_user_to_queue))
        self.bot.add_listener(voice.on_moveaway_x(channel_id, remove_user_from_queue))
        
        return lambda: queue[0], queue
    
    def setup(self):
        print("Success")