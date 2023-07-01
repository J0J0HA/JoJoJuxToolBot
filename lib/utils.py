import nextcord
from nextcord.ext import commands
from .config import config

def CustomButton(callback):
    class CustomButton(nextcord.ui.Button):
        async def callback(self, interaction: nextcord.Interaction):
            await callback(interaction)
    
    return CustomButton

