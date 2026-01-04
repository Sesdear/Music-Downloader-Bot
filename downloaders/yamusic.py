from aiogram.types import Message, FSInputFile
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from yandex_music import ClientAsync, Track
import os
import re

import asyncio

from config import *

router = Router()

YANDEX_MUSIC_TOKEN = YAMUSIC_TOKEN


async def download_yandex_music(message: Message, url: str):

    
    try:

        client = await ClientAsync(YANDEX_MUSIC_TOKEN).init()
        
        
        
        track_id = extract_track_id(url)
        if not track_id:
            await message.answer("❌ Неверный формат ссылки. Пример: https://music.yandex.ru/album/1234567/track/7654321")
            return
        
        await download_track_async(client, track_id, message)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)[:200]}")
    finally:
        pass


def extract_track_id(url: str) -> str | None:
    patterns = [
        r'/track/(\d+)',
        r'album/\d+/track/(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


async def download_track_async(client: ClientAsync, track_id: str, message: Message):
    try:
        tracks = await client.tracks([track_id])
        if not tracks:
            await message.answer("❌ Трек не найден")
            return

        track: Track = tracks[0]

        artist_name = track.artists[0].name if track.artists else "Unknown"
        track_title = f"{artist_name} - {track.title}"
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', track_title) + ".mp3"

        await message.answer(f"⬇️ Скачиваю: {track_title}")

        os.makedirs('./audios', exist_ok=True)
        filename = f"./audios/{safe_filename}"

        await track.download_async(filename)

        audio_file = FSInputFile(filename)
        await message.answer_audio(audio_file, title=track.title, performer=artist_name)

        os.remove(filename)

        await message.answer("✅ Готово!")

    except Exception as e:
        await message.answer(f"❌ Ошибка при скачивании: {str(e)[:200]}")
        
        
async def download_album_async(client: ClientAsync, album_id: str, message: Message):
    try:
        album = await client.albums_with_tracks(album_id)
        tracks = album.volumes[0]
        
        await message.answer(f"🎵 Альбом: {album.title}\n📊 Треков: {len(tracks)}")
        
        for i, track_short in enumerate(tracks, 1):
            try:
                track = await track_short.fetch_track_async()
                await message.answer(f"⬇️ [{i}/{len(tracks)}] {track.title}")
                await download_track_async(client, str(track.id), message)
                await asyncio.sleep(1)
            except Exception as e:
                await message.answer(f"⚠️ Пропущен трек {i}: {str(e)[:100]}")
                
    except Exception as e:
        await message.answer(f"❌ Ошибка альбома: {str(e)[:200]}")