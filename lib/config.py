import nextcord
from yaml import load, Loader
from nextcord.ext import commands


class Config(dict):
    def load(self, stream):
        self.clear()
        self.update(load(stream, Loader))

    def get_bot_token(self) -> str:
        return self.get("bot_token")

    def get_guild(self, bot: commands.Bot)  -> nextcord.Guild | None:
        return bot.get_guild(self.get("guild_id"))

    def get_channel_availible(self, bot: commands.Bot) -> nextcord.VoiceChannel | None:
        return bot.get_channel(self.get("channels", {}).get("availible"))

    def get_channel_queue(self, bot: commands.Bot) -> nextcord.VoiceChannel | None:
        return bot.get_channel(self.get("channels", {}).get("queue"))

    def get_text_channel(self, bot: commands.Bot) -> nextcord.TextChannel | None:
        return bot.get_channel(self.get("channels", {}).get("text"))
    
    def fetch_guild(self, bot: commands.Bot) -> nextcord.Guild:
        return bot.fetch_guild(self.get("guild_id"))

    def fetch_channel_availible(self, bot: commands.Bot) -> nextcord.VoiceChannel:
        return bot.fetch_channel(self.get("channels", {}).get("availible"))

    def fetch_channel_queue(self, bot: commands.Bot) -> nextcord.VoiceChannel:
        return bot.fetch_channel(self.get("channels", {}).get("queue"))

    def fetch_text_channel(self, bot: commands.Bot) -> nextcord.TextChannel:
        return bot.fetch_channel(self.get("channels", {}).get("text"))


config = Config()
with open("config.yml", "r", encoding="utf-8") as file:
    config.load(file)
