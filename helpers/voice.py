import nextcord
from typing import Callable


def on_join(func: Callable):
    async def on_voice_state_update(
        member: nextcord.Member,
        before: None | nextcord.VoiceState,
        after: None | nextcord.VoiceState,
    ):
        if before.channel is None and after.channel is not None:
            await func(member, before, after)

    return on_voice_state_update


def on_leave(func: Callable):
    async def on_voice_state_update(
        member: nextcord.Member,
        before: None | nextcord.VoiceState,
        after: None | nextcord.VoiceState,
    ):
        if before.channel is not None and after.channel is None:
            await func(member, before, after)

    return on_voice_state_update


def on_moveto_x(channel_id: int, func: Callable):
    async def on_voice_state_update(
        member: nextcord.Member,
        before: None | nextcord.VoiceState,
        after: None | nextcord.VoiceState,
    ):
        if (
            after.channel is not None
            and after.channel.id == channel_id
            and (before.channel is None or before.channel.id != channel_id)
        ):
            await func(member, before, after)

    return on_voice_state_update


def is_member(check_member: nextcord.Member, func: Callable):
    async def on_voice_state_update(
        member: nextcord.Member,
        before: None | nextcord.VoiceState,
        after: None | nextcord.VoiceState,
    ):
        if member.id == check_member.id:
            await func(member, before, after)

    return on_voice_state_update


def on_move(func: Callable):
    async def on_voice_state_update(
        member: nextcord.Member,
        before: None | nextcord.VoiceState,
        after: None | nextcord.VoiceState,
    ):
        if (
            before.channel is None
            or after.channel is None
            or before.channel.id != after.channel.id
        ):
            await func(member, before, after)

    return on_voice_state_update


def on_moveaway_x(channel_id: int, func: Callable):
    async def on_voice_state_update(
        member: nextcord.Member,
        before: None | nextcord.VoiceState,
        after: None | nextcord.VoiceState,
    ):
        if (
            before.channel is not None
            and before.channel.id == channel_id
            and (after.channel is None or after.channel.id != channel_id)
        ):
            await func(member, before, after)

    return on_voice_state_update


def on_mute(func: Callable):
    async def on_voice_state_update(
        member: nextcord.Member,
        before: None | nextcord.VoiceState,
        after: None | nextcord.VoiceState,
    ):
        if before.mute is False and after.mute is True:
            await func(member, before, after)

    return on_voice_state_update


def on_unmute(func: Callable):
    async def on_voice_state_update(
        member: nextcord.Member,
        before: None | nextcord.VoiceState,
        after: None | nextcord.VoiceState,
    ):
        if before.mute is True and after.mute is False:
            await func(member, before, after)

    return on_voice_state_update


on_join_x = lambda channel_id, func: on_join(on_moveto_x(channel_id, func))
on_leave_x = lambda channel_id, func: on_leave(on_moveaway_x(channel_id, func))
on_move_x_to_y = lambda x_channel_id, y_channel_id, func: on_moveaway_x(
    x_channel_id, on_moveto_x(y_channel_id, func)
)
