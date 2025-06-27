import os
import time  # 追加
import discord
from discord.ext import commands
from keep_alive import keep_alive  # Flaskのサーバー起動用

# ⬇️ 追記：送信ログ用のキャッシュ
last_message_time = {}

PAIR_CONFIG = {
    451520103453032450: {
        "partner_id": 1072436461070192730,
        "common_vc_ids": [
            1387604262132912288,
            1387603562460217446,
            1387835939128348702,
            1387603026671304755,
        ],
        "private_vc_id": 1387836330154922004,
        "text_channel_id": 1387831889976492194,
        "messages": {
            "common": {
                1387604262132912288: "<@{partner}> ごはんつくる",
                1387603562460217446: "<@{partner}> りびんぐまったり",
                1387835939128348702: "<@{partner}> 作業するよ",
                1387603026671304755: "<@{partner}> ねる",
            },
            "private": "<@{partner}> いらすとさぎょうするよ"
        }
    },
    1072436461070192730: {
        "partner_id": 451520103453032450,
        "common_vc_ids": [
            1387604262132912288,
            1387603562460217446,
            1387835939128348702,
            1387603026671304755,
        ],
        "private_vc_id": 1387836714021683360,
        "text_channel_id": 1387831889976492194,
        "messages": {
            "common": {
                1387604262132912288: "<@{partner}> ごはん作る",
                1387603562460217446: "<@{partner}> りびんぐ！かまって！！",
                1387835939128348702: "<@{partner}> 作業する～！",
                1387603026671304755: "<@{partner}> ねたい",
            },
            "private": "<@{partner}> はなちゃんへ、らてあーとします"
        }
    }
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        config = PAIR_CONFIG.get(member.id)
        if not config:
            return
        text_channel = bot.get_channel(config["text_channel_id"])
        if not text_channel:
            return

        voice_channel = after.channel
        partner_id = config["partner_id"]

        # 相手がすでにVCにいる場合は送信しない
        if any(user.id == partner_id for user in voice_channel.members):
            print(f"[INFO] 相手({partner_id})が既にVCにいるため送信スキップ")
            return

        now = time.time()
        last_time = last_message_time.get(member.id, 0)
        if now - last_time < 10:
            print(f"[INFO] 連投防止: {member.name} からのメッセージ送信をスキップ")
            return  # 10秒以内の再送を防止

        # VCごとのメッセージ
        if after.channel.id in config["common_vc_ids"]:
            msg_template = config["messages"]["common"].get(after.channel.id)
            if msg_template:
                msg = msg_template.format(partner=partner_id, user=member.display_name)
                await text_channel.send(msg)
                print(f"[SENT] {msg}")
                last_message_time[member.id] = now

        elif config["private_vc_id"] and after.channel.id == config["private_vc_id"]:
            msg = config["messages"]["private"].format(partner=partner_id, user=member.display_name)
            await text_channel.send(msg)
            print(f"[SENT] {msg}")
            last_message_time[member.id] = now

# Flaskサーバー起動（Replitのスリープ防止）
keep_alive()

# 環境変数からトークンを取得してBot起動
bot.run(os.environ['DISCORD_TOKEN'])
