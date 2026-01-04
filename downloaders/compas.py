from aiogram.types import Message
from urllib.parse import urlparse
from downloaders import *

supported_domains: list = [
    "soundcloud.com", "www.soundcloud.com",
    "youtube.com", "www.youtube.com", "youtu.be",
    "music.yandex.ru"
]

async def split_link(link: str) -> str:
    parsed = urlparse(link)
    return parsed.netloc

async def check_link(url: str) -> bool:
    if url in supported_domains:
        return True
    else:
        return False

async def compas(message: Message):
    url: str = str(message.text)
    domain: str = await split_link(url)
    await message.answer("🔍 Обрабатываю ссылку...")
    if domain not in supported_domains:
        await message.answer("LINK INCORRECT")
        return
    match domain:
        case "soundcloud.com" | "www.soundcloud.com":
            await download_soundcloud_mp3(message, url)
        case "youtube.com" | "www.youtube.com" | "youtu.be":
            await yt_download_send_mp3(message, url)
        case "music.yandex.ru":
            await download_yandex_music(message, url)
        case _:
            await message.answer("Unsupported domain despite check")
