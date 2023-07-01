import nextcord
from nextcord.ext import commands
from asyncinit import asyncinit
from uuid import uuid4
from .utils import CustomButton
from collections import deque
from .config import config


@asyncinit
class Admin:
    async def __init__(
        self,
        bot: commands.Bot,
        member: nextcord.Member,
        guild: nextcord.Guild,
        queue: deque,
    ):
        self.bot = bot
        self.member = member
        self.guild = guild
        self.queue = queue
        self.channel_name = "admin-" + str(uuid4())
        self.channel: nextcord.TextChannel = None

    async def open(self):
        self.channel = await self.guild.create_text_channel(
            self.channel_name,
            overwrites={
                self.bot.user: nextcord.PermissionOverwrite(
                    view_channel=True
                ),
                self.member: nextcord.PermissionOverwrite(
                    view_channel=True
                ),
                self.guild.default_role: nextcord.PermissionOverwrite(
                    view_channel=False
                )
            },
        )

        await self.channel.send(
            view=self.get_base_view(),
            content=f"# {self.channel_name}\nfor: {self.member.mention}\n> Admin channel opened successfully.",
        )

    def get_base_view(self):
        view = nextcord.ui.View()

        async def _button_next(interaction: nextcord.Interaction):
            await self.next(interaction)

        async def _button_leave(interaction: nextcord.Interaction):
            await self.member.move_to(None)

        view.add_item(
            CustomButton(_button_next)(
                style=nextcord.ButtonStyle.green, label="Next verification"
            )
        )

        view.add_item(
            CustomButton(_button_leave)(
                style=nextcord.ButtonStyle.red, label="No longer availible"
            )
        )
        return view

    @property
    async def invite_link(self):
        invite = await self.channel.create_invite(max_uses=1)
        return invite.url

    @property
    async def jumpto(self):
        return self.channel.jump_url

    async def create_verify_channel(self, member: nextcord.Member):
        verification_id = "verify-" + str(uuid4())
        channel = await self.guild.create_voice_channel(
            verification_id,
            user_limit=2,
            overwrites={
                self.bot.user: nextcord.PermissionOverwrite(
                    view_channel=True
                ),
                self.member: nextcord.PermissionOverwrite(
                    view_channel=True
                ),
                member: nextcord.PermissionOverwrite(
                    view_channel=True
                ),
                self.guild.default_role: nextcord.PermissionOverwrite(
                    view_channel=False
                )
            },
        )
        return channel

    async def next(self, interaction: nextcord.Interaction):
        if not self.queue:
            await interaction.edit(
                content=f"# {self.channel_name}\nfor: {self.member.mention}\n> No users in queue."
            )
            return
        next_member: nextcord.Member = self.queue.pop()
        verify_channel = await self.create_verify_channel(next_member)
        await self.member.move_to(verify_channel)
        await next_member.move_to(verify_channel)
        view = nextcord.ui.View()

        async def _button_verify(interaction: nextcord.Interaction):
            role = nextcord.utils.get(self.guild.roles, name="Verified")
            await next_member.add_roles(role)
            await verify_channel.set_permissions(next_member, view_channel=False)
            await self.member.move_to(config.get_channel_availible(self.bot))
            await verify_channel.delete()
            await interaction.edit(
                view=self.get_base_view(),
                content=f"# {self.channel_name}\nfor: {self.member.mention}\n> Verification Channel closed.",
            )
            await self.bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name=f"{next_member.name}'s verification"))

        async def _button_requeue(interaction: nextcord.Interaction):
            await verify_channel.set_permissions(next_member, view_channel=False)
            await next_member.move_to(config.get_channel_queue(self.bot))
            await self.member.move_to(config.get_channel_availible(self.bot))
            await verify_channel.delete()
            await interaction.edit(
                view=self.get_base_view(),
                content=f"# {self.channel_name}\nfor: {self.member.mention}\n> Verification Channel closed.",
            )

        async def _button_end(interaction: nextcord.Interaction):
            await verify_channel.set_permissions(next_member, view_channel=False)
            await self.member.move_to(config.get_channel_availible(self.bot))
            await verify_channel.delete()
            await interaction.edit(
                view=self.get_base_view(),
                content=f"# {self.channel_name}\nfor: {self.member.mention}\n> Verification Channel closed.",
            )

        async def _button_kick(interaction: nextcord.Interaction):
            await next_member.kick()
            await self.member.move_to(config.get_channel_availible(self.bot))
            await verify_channel.delete()
            await interaction.edit(
                view=self.get_base_view(),
                content=f"# {self.channel_name}\nfor: {self.member.mention}\n> Verification Channel closed.",
            )

        async def _button_ban(interaction: nextcord.Interaction):
            await next_member.ban()
            await self.member.move_to(config.get_channel_availible(self.bot))
            await verify_channel.delete()
            await interaction.edit(
                view=self.get_base_view(),
                content=f"# {self.channel_name}\nfor: {self.member.mention}\n> Verification Channel closed.",
            )

        view.add_item(
            CustomButton(_button_verify)(
                style=nextcord.ButtonStyle.green, label="Verify"
            )
        )
        view.add_item(
            CustomButton(_button_requeue)(
                style=nextcord.ButtonStyle.blurple, label="Sent back to queue"
            )
        )
        view.add_item(
            CustomButton(_button_end)(
                style=nextcord.ButtonStyle.blurple, label="End Session"
            )
        )
        view.add_item(
            CustomButton(_button_kick)(style=nextcord.ButtonStyle.red, label="Kick")
        )
        view.add_item(
            CustomButton(_button_ban)(style=nextcord.ButtonStyle.red, label="Ban")
        )

        await interaction.edit(
            content=f"# {self.channel_name}\nfor: {self.member.mention}\n> You started verification with {next_member.mention} in {verify_channel.jump_url}",
            view=view,
        )

    async def close(self):
        await self.channel.delete()
