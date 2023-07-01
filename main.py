import nextcord
from nextcord.ext import commands
from nextcord.ext import tasks
from lib.config import config
from lib.admin_channel import Admin
from collections import deque

intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot(intents=intents)
admin_channels = {}
user_queue = deque()
STATUS_MESSAGE: nextcord.Message = None


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    guild = config.get_guild(bot)
    role = nextcord.utils.get(guild.roles, name="Verifier")
    for member in guild.members:
        if role in member.roles:
            print(f"{member.name} is Verifier.")
            admin_channels[member.name] = await Admin(
                bot, member, member.guild, user_queue
            )
    text_channel = config.get_text_channel(bot)
    queue_channel = config.get_channel_queue(bot)
    availible_channel = config.get_channel_availible(bot)
    for member in queue_channel.members:
        await member.move_to(None)
    for member in availible_channel.members:
        await member.move_to(None)
    global STATUS_MESSAGE
    STATUS_MESSAGE = await text_channel.send(
        f"# Verification\nJoin the queue to get verified: {queue_channel.jump_url}"
    )
    update_counters.start()


@bot.event
async def on_voice_state_update(
    member: nextcord.Member,
    before: None | nextcord.VoiceState,
    after: None | nextcord.VoiceState,
):
    role = nextcord.utils.get(member.guild.roles, name="Verifier")
    if role in member.roles:
        if after.channel is None and before.channel is not None:
            print(f"{member.name} stopped admin mode.")
            await admin_channels[member.name].close()
        if (
            after.channel is not None
            and before.channel is None
            and after.channel.id == config["channels"]["availible"]
        ):
            print(f"{member.name} started admin mode.")
            await admin_channels[member.name].open()

    if after.channel is not None and after.channel.id == config["channels"]["queue"]:
        print(f"{member.name} joined the queue.")
        user_queue.append(member)

    if (
        before.channel is not None
        and after.channel is None
        and before.channel.id == config["channels"]["queue"]
    ):
        print(f"{member.name} left the queue.")
        user_queue.remove(member)


@tasks.loop(seconds=10)
async def update_counters():
    queue_channel = config.get_channel_queue(bot)
    availible_channel = config.get_channel_availible(bot)
    await STATUS_MESSAGE.edit(
        content=f"# Verification\nJoin the queue to get verified: {queue_channel.jump_url}\n\n**Queue**: {len(queue_channel.members)} currently waiting\n**Admins**: {len(availible_channel.members)} currently free"
    )


bot.run(config.get_bot_token())
