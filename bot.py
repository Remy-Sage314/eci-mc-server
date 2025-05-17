import datetime

import nonebot
from nonebot import on_command
from nonebot.params import CommandArg

from nonebot.adapters.discord import Bot, MessageEvent, MessageSegment, Message
from nonebot.adapters.discord.api import *

nonebot.init()
matcher = on_command('send')


@matcher.handle()
async def ready(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    print(msg)
    # 调用discord的api
    self_info = await bot.get_current_user()  # 获取机器人自身信息
    user = await bot.get_user(user_id=event.user_id)  # 获取指定用户信息
    ...
    # 各种消息段
    msg = msg.extract_plain_text()
    if msg == 'mention_me':
        # 发送一个提及你的消息
        await matcher.finish(MessageSegment.mention_user(event.user_id))
    elif msg == 'time':
        # 发送一个时间，使用相对时间（RelativeTime）样式
        await matcher.finish(MessageSegment.timestamp(datetime.datetime.now(),
                                                      style=TimeStampStyle.RelativeTime))
    elif msg == 'mention_everyone':
        # 发送一个提及全体成员的消息
        await matcher.finish(MessageSegment.mention_everyone())
    elif msg == 'mention_channel':
        # 发送一个提及当前频道的消息
        await matcher.finish(MessageSegment.mention_channel(event.channel_id))
    elif msg == 'embed':
        # 发送一个嵌套消息，其中包含a embed标题，nonebot logo描述和来自网络url的logo图片
        await matcher.finish(MessageSegment.embed(
            Embed(title='a embed',
                  type=EmbedTypes.image,
                  description='nonebot logo',
                  image=EmbedImage(
                      url='https://v2.nonebot.dev/logo.png'))))
    elif msg == 'attachment':
        # 发送一个附件，其中包含来自本地的logo.png图片
        with open('logo.png', 'rb') as f:
            await matcher.finish(MessageSegment.attachment(file='logo.png',
                                                           content=f.read()))
    elif msg == 'component':
        # 发送一个复杂消息，其中包含一个当前时间，一个字符串选择菜单，一个用户选择菜单和一个按钮
        time_now = MessageSegment.timestamp(datetime.datetime.now())
        string_select = MessageSegment.component(
            SelectMenu(type=ComponentType.StringSelect,
                       custom_id='string select',
                       placeholder='select a value',
                       options=[
                           SelectOption(label='A', value='a'),
                           SelectOption(label='B', value='b'),
                           SelectOption(label='C', value='c')]))
        select = MessageSegment.component(SelectMenu(
            type=ComponentType.UserInput,
            custom_id='user_input',
            placeholder='please select a user'))
        button = MessageSegment.component(
            Button(label='button',
                   custom_id='button',
                   style=ButtonStyle.Primary))
        await matcher.finish('now time:' + time_now + string_select + select + button)
    else:
        # 发送一个文本消息
        await matcher.finish(MessageSegment.text(msg))

