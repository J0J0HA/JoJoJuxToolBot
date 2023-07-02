import nextcord
from helpers import voice
from ._ import _


class Module(_(__name__)):
    async def next_queue_member(self, admin, interaction: nextcord.Interaction):
        member: nextcord.Member = self.get_next()
        members = [member, admin.member]
        channel: nextcord.VoiceChannel = await self.ctrl.modules[
            "modules.dynamic_channels"
        ].create_dynamic_voice(f"support-{member.name}", members=members)
        
        deleted = False        
        async def delete_channel(check: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
            nonlocal deleted
            if deleted:
                return
            deleted = True
            if check.id == admin.member.id:
                await member.move_to(await self.bot.fetch_channel(self.config.get("queue_channel_id")))
            else:
                await admin.member.move_to(admin.module.channel)
            await channel.delete()
            admin.admin_channels.remove(channel.id)
            
        
        self.bot.add_listener(voice.on_moveaway_x(channel.id, delete_channel))
        
        admin.admin_channels.add(channel.id)
        
        for memberx in members:
            await memberx.move_to(channel)
        
        await admin.set_message(f"You were connected with {member.mention} in {channel.jump_url}.")

    def setup(self):
        self.ctrl.modules["modules.admins"].register_admin_action(
            "Next in Support Queue", "voicesup-next", self.next_queue_member
        )
        self.get_next, self._queue = self.ctrl.modules["modules.voice_queue"].get_queue(
            self.config["queue_channel_id"]
        )
        
        # @self.bot.slash_command(description="Voice-Support Commands", guild_ids=[self.ctrl.config["guild_id"]])
        # async def voicesupport(interaction: nextcord.Interaction):
        #     await interaction.send("**Commands**:\nSupport next user: /voicesupport next\nNo longer availible: /voicesupport end", ephemeral=True)
            
        # @voicesupport.subcommand(description="Request Support")
        # async def request(interaction: nextcord.Interaction):
        #     await interaction.send(f"Join the queue to request voice support: {(await self.bot.fetch_channel(self.config['queue_channel_id'])).jump_url}", ephemeral=True)

        # @voicesupport.subcommand(description="Open support voice with next user")
        # async def next(interaction: nextcord.Interaction):
        #     await interaction.send("Not yet implemented", ephemeral=True)

        # @voicesupport.subcommand(description="Mark yourself as no longer availible")
        # async def end(interaction: nextcord.Interaction):
        #     await interaction.send("Not yet implemented", ephemeral=True)
