import nextcord
from nextcord.ext import commands
from bot import Controller

def _(name):
    class _:
        id: str = name
        
        def __init__(self, ctrl) -> None:
            self.ctrl: Controller = ctrl
            self.bot: commands.Bot = ctrl.bot
            self.config: dict = self.ctrl.config.get("modules", {}).get(self.id, {})
            self.setup()
            
        def setup(self):
            raise NotImplementedError(f"{self.id}.Module.setup()")
    return _
        