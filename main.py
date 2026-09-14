import os, glob, asyncio, yt_dlp, requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TAG = "@epic_india"

app = Client("epic_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

def download(query, is_video=False):
    q = query if query.startswith("http") else f"ytsearch1:{query}"
    fmt = 'best' if "instagram.com" in q and is_video else 'bestaudio/best' if "instagram.com" in q else 'best[height<=480][ext=mp4]/best' if is_video else 'bestaudio[ext=m4a]/bestaudio/best'
    opts = {'format': fmt, 'noplaylist': True, 'outtmpl': '%(title).30s.%(ext)s', 'quiet': True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(q, download=True)
        if 'entries' in info: info = info['entries'][0]
        return ydl.prepare_filename(info), info

@app.on_message(filters.command("play"))
async def play(c, m: Message):
    if len(m.command) < 2: return await m.reply(f"Use: /play <song>\n\n{TAG}")
    q = m.text.split(None, 1)[1]
    wait = await m.reply("⚡️")
    try:
        fp, info = download(q, False)
        await call.play(m.chat.id, MediaStream(fp))
        try: await m.delete()
        except: pass
        await wait.delete()
        thumb_path = None
        try:
            url = info.get('thumbnail')
            if url:
                thumb_path = "thumb.jpg"
                open(thumb_path, 'wb').write(requests.get(url, timeout=10).content)
                await c.send_photo(m.chat.id, thumb_path, caption=f"🎧 {info.get('title')}\n\n{TAG}")
            else:
                await c.send_message(m.chat.id, f"🎧 {info.get('title')}\n\n{TAG}")
        except:
            await c.send_message(m.chat.id, f"🎧 {info.get('title')}\n\n{TAG}")
        if thumb_path and os.path.exists(thumb_path): os.remove(thumb_path)
    except Exception as e:
        await m.reply(f"❌ {e}\n\n{TAG}")

@app.on_message(filters.command("vplay"))
async def vplay(c, m: Message):
    if len(m.command) < 2: return await m.reply(f"Use: /vplay <video>\n\n{TAG}")
    q = m.text.split(None, 1)[1]
    wait = await m.reply("⚡️")
    try:
        fp, info = download(q, True)
        await call.play(m.chat.id, MediaStream(fp, video=True))
        try: await m.delete()
        except: pass
        await wait.delete()
        await c.send_video(m.chat.id, fp, caption=f"🎬 {info.get('title')}\n\n{TAG}")
    except Exception as e:
        await m.reply(f"❌ {e}\n\n{TAG}")

@app.on_message(filters.command("stop"))
async def stop(c, m: Message):
    try:
        await call.leave(m.chat.id)
        await m.reply(f"⏹️ Stopped\n\n{TAG}")
    except:
        await m.reply(f"Nothing playing\n\n{TAG}")
    try: await m.delete()
    except: pass

@app.on_message(filters.command("refresh"))
async def refresh(c, m: Message):
    for f in glob.glob("*.mp3")+glob.glob("*.mp4")+glob.glob("*.m4a")+glob.glob("*.webm")+glob.glob("*.jpg"):
        try: os.remove(f)
        except: pass
    await m.reply(f"♻️ Cleaned\n\n{TAG}")

async def main():
    await app.start()
    await call.start()
    print(f"Bot Started {TAG}")
    await asyncio.Event().wait()

asyncio.run(main())
