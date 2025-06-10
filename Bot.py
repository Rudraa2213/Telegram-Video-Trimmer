from pyrogram import Client, filters
from moviepy import VideoFileClip
import os
import asyncio

BOT_TOKEN = ""
API_ID = 
API_HASH = ""  

app = Client(
    "my_bot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

user_trim_settings = {}

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("👋 Hi! Send `/trim 10 30` to set custom trim range (in seconds), then send a video.")

@app.on_message(filters.command("trim"))
async def set_trim_range(client, message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            return await message.reply("❌ Usage: /trim <start_seconds> <end_seconds>")

        start = int(parts[1])
        end = int(parts[2])

        if start >= end:
            return await message.reply("⚠️ Start time must be less than end time.")

        user_trim_settings[message.from_user.id] = (start, end)
        await message.reply(f"✅ Trim time set from {start}s to {end}s. Now send a video.")
    except ValueError:
        await message.reply("❌ Please enter valid numbers for start and end times.")

@app.on_message(filters.command("reset"))
async def reset_trim(client, message):
    user_trim_settings.pop(message.from_user.id, None)
    await message.reply("🔄 Trim settings have been reset.")


@app.on_message(filters.video)
async def trim_video(client, message):
    user_id = message.from_user.id
    trim_range = user_trim_settings.get(user_id)

    if not trim_range:
        return await message.reply("❗ Please use `/trim start end` before sending the video.")

    start_time, end_time = trim_range
    file_name = f"{message.video.file_unique_id}.mp4"
    download_path = os.path.join(os.path.expanduser("~"), "Downloads", file_name)
    await message.download(file_name=download_path)

    status_msg = await message.reply(f"⏳ Trimming video from {start_time}s to {end_time}s...")

    clip = None
    output_path = "trimmed_output.mp4"

    try:
        clip = VideoFileClip(download_path)
        duration = clip.duration

        if start_time >= duration or end_time > duration:
            return await status_msg.edit("❌ Trim range exceeds video length.")

        # Simulated progress
        for i in range(1, 6):
            await asyncio.sleep(1)
            await status_msg.edit(f"⌛ Processing... {6 - i} seconds remaining...")

        clip.subclipped(start_time, end_time).write_videofile(output_path, codec="libx264", audio_codec="aac")

        await status_msg.edit("✅ Done! Sending trimmed video...")
        await message.reply_video(output_path, caption=f"🎬 Trimmed from {start_time}s to {end_time}s")

        # Optionally clear the settings
        del user_trim_settings[user_id]

    except Exception as e:
        await status_msg.edit(f"❌ Error: {e}")
    finally:
        if clip:
            clip.close()
        for f in [download_path, output_path]:
            if os.path.exists(f):
                os.remove(f)

print("Bot is running...")
app.run()
