import nextcord
from nextcord.application_command import SlashApplicationCommand
import importlib
from nextcord.ext import commands
from nextcord.ext import tasks
import yaml


class Controller:
    def __init__(self) -> None:
        intents = nextcord.Intents.default()
        intents.members = True
        self.bot: commands.Bot = commands.Bot(intents=intents)
        self.modules = {}
        self.config = {}

    def register_module(self, module):
        self.modules[module.id] = module(self)

    def load_config(self, path: str):
        with open(path, "r") as file:
            self.config = yaml.load(file, yaml.Loader)
        for module_id in self.config.get("modules"):
            print(f"Registering {module_id}...")
            module = importlib.import_module(module_id).Module
            self.register_module(module)  #

    def run(self):
        async def on_ready():
            self.guild = await self.bot.fetch_guild(self.config["guild_id"])
            self.bot_member = await self.guild.fetch_member(self.bot.user.id)
        self.bot.add_listener(on_ready, "on_ready")
        self.bot.run(self.config.get("bot_token"))


if __name__ == "__main__":
    ctrl = Controller()
    ctrl.load_config("config.yml")
    ctrl.run()
