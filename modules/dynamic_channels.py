from typing import List
import nextcord
from helpers import voice
from ._ import _


class Module(_(__name__)):
    async def create_dynamic_voice(
        self,
        name: str,
        members: List[nextcord.Member],
        max_users: int = None,
        on_join=None,
        on_leave=None
    ):
        overwrites = {
            self.ctrl.bot_member: nextcord.PermissionOverwrite(
                view_channel=True
            ),
            self.ctrl.guild.default_role: nextcord.PermissionOverwrite(
                view_channel=False
            )
        }
        overwrites.update(
            {
                member: nextcord.PermissionOverwrite(view_channel=True)
                for member in members
            }
        )
        channel = await self.ctrl.guild.create_voice_channel(
            name, user_limit=max_users, overwrites=overwrites
        )

        if on_join is not None:
            self.bot.add_listener(voice.on_moveto_x(channel.id, on_join))

        if on_leave is not None:
            self.bot.add_listener(voice.on_moveaway_x(channel.id, on_leave))

        return channel

    async def create_dynamic_text(self, name: str, members: List[nextcord.Member]):
        overwrites = {
            self.ctrl.bot_member: nextcord.PermissionOverwrite(
                view_channel=True
            ),
            self.ctrl.guild.default_role: nextcord.PermissionOverwrite(
                view_channel=False
            )
        }
        overwrites.update(
            {
                member: nextcord.PermissionOverwrite(view_channel=True)
                for member in members
            }
        )
        channel = await self.ctrl.guild.create_text_channel(name, overwrites=overwrites)
        return channel

    def setup(self):
        print("Dynamic channels was activated.")
