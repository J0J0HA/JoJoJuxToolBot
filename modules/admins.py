from typing import Callable
import nextcord
from helpers import voice
from ._ import _
from asyncinit import asyncinit


def CustomButton(callback):
    class CustomButton(nextcord.ui.Button):
        async def callback(self, interaction: nextcord.Interaction):
            await callback(interaction)

    return CustomButton


class Module(_(__name__)):
    admin_actions = []
    admin_channels = {}

    async def on_join(
        self,
        member: nextcord.Member,
        before: None | nextcord.VoiceState,
        after: None | nextcord.VoiceState,
    ):
        if not member.name in self.admins:
            self.admins[member.name] = await Admin(self, member)

        print(f"{member.name} joined the availible channel")

    async def on_ready(self):
        self.channel = await self.bot.fetch_channel(self.channel_id)

    def register_admin_action(self, name: str, id: str, callback: Callable):
        self.admin_actions.append((name, id, callback))
        print(name, id, callback)

        @self.admin_command.subcommand(id, description=name)
        async def command(interaction: nextcord.Interaction):
            if (
                interaction.user.name not in self.admins
                or interaction.user.voice.channel.id != self.channel_id
            ):
                await interaction.send("You have not yet joined the availible channel.", ephemeral=True)
                return
            await callback(self.admins[interaction.user.name], interaction)
            await interaction.send("Done", ephemeral=True)

    def setup(self):
        self.admin_actions = []
        self.admins = {}
        self.channel_id = self.config["channel_id"]
        self.bot.add_listener(voice.on_moveto_x(self.channel_id, self.on_join))
        self.bot.add_listener(self.on_ready, "on_ready")

        @self.bot.slash_command(
            description="Admin Commands", guild_ids=[self.ctrl.config["guild_id"]]
        )
        async def admin(interaction: nextcord.Interaction):
            commands = "\n- `/admin ".join(
                f"{action[1]}` - _{action[0]}_" for action in self.admin_actions
            )
            await interaction.send(f"**Commands**:\n- `/admin {commands}", ephemeral=True)

        self.admin_command = admin

        @admin.subcommand("help", description="List all admin commands")
        async def command(interaction: nextcord.Interaction):
            commands = "\n- `/admin ".join(
                f"{action[1]}` - _{action[0]}_" for action in self.admin_actions
            )
            await interaction.send(f"**Commands**:\n- `/admin {commands}", ephemeral=True)

        # self.bot.add_listener(voice.on_moveaway_x(channel_id, self.on_leave_move))
        # self.bot.add_listener(voice.on_leave(channel_id, self.on_leave_leave))
        ### WORKS:
        # self.bot.slash_command(NAME, guild_ids=[self.ctrl.config["guild_id"]])(
        #     CALLBACK
        # )


@asyncinit
class Admin:
    message = None
    
    async def __init__(self, module: Module, member: nextcord.Member) -> None:
        self.module: Module = module
        self.member: nextcord.Member = member
        self.admin_channels = {self.module.channel_id}
        await self.create_channel()
        self.module.bot.add_listener(
            voice.on_move(voice.is_member(self.member, self.on_move))
        )

    async def on_move(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ):
        if after.channel is None:
            if self.channel is None:
                return
            print("left")
            await self.channel.delete()
            self.channel = None
        if before.channel is None:
            print("joined")
            await self.create_channel()
        if before.channel is not None and after.channel is not None:
            print("moved")
            if after.channel.id not in self.admin_channels:
                if self.channel is None:
                    return
                print("Untrusted channel")
                await self.channel.delete()
                self.channel = None
            if (
                after.channel.id in self.admin_channels
                and before.channel.id not in self.admin_channels
            ):
                print("Trusted channel")
                await self.create_channel()

    async def create_channel(self):
        self.channel: nextcord.TextChannel = await self.module.ctrl.modules[
            "modules.dynamic_channels"
        ].create_dynamic_text(f"admin-{self.member.name}", members=[self.member])
        await self.set_message("Channel created.")

    async def set_message(
        self,
        message: str,
        view: nextcord.ui.View = None,
    ):
        if view is None:
            view = nextcord.ui.View()

            async def _button_leave(interaction: nextcord.Interaction):
                await self.member.move_to(None)

            def callback_wrapper(func):
                async def _button_callback(interaction: nextcord.Interaction):
                    await func(self, interaction)

                return _button_callback

            for action in self.module.admin_actions:
                view.add_item(
                    CustomButton(callback_wrapper(action[2]))(
                        style=nextcord.ButtonStyle.green, label=action[0]
                    )
                )

            view.add_item(
                CustomButton(_button_leave)(
                    style=nextcord.ButtonStyle.red, label="No longer availible"
                )
            )

        if self.message is None:
            self.message = await self.channel.send(
                f"# Admin Panel\n## for {self.member.mention}\n> {message}\n", view=view
            )
        else:
            await self.message.edit(
                content=f"# Admin Panel\n## for {self.member.mention}\n> {message}\n", view=view
            )
