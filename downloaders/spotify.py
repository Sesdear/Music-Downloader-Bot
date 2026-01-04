from aiogram.types import Message, FSInputFile
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from yt_dlp import YoutubeDL
import os
import re

from messages_config import *
from config import *

router = Router()


class SpotifyUrl(StatesGroup):
    url_or_query = State()

def extract_spotify_id(url: str) -> str | None:
    patterns = [
        r'spotify:track:([a-zA-Z0-9]+)',
        r'open\.spotify\.com/track/([a-zA-Z0-9]+)',
        r'spotify:album:([a-zA-Z0-9]+)',
        r'open\.spotify\.com/album/([a-zA-Z0-9]+)',
        r'spotify:playlist:([a-zA-Z0-9]+)',
        r'open\.spotify\.com/playlist/([a-zA-Z0-9]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@router.message(Command("spotify"))
async def spotify_start(message: Message, state: FSMContext):
    await message.answer(SPOTIFY_ENTER_URL_MESSAGE)
    await state.set_state(SpotifyUrl.url_or_query)

@router.message(SpotifyUrl.url_or_query)
async def download_spotify(message: Message, state: FSMContext):
    query = message.text.strip()

    try:
        await message.answer(PROCESSING_MESSAGE)

        search_query = query
        if extract_spotify_id(query):

            search_query = f"ytsearch1:{query}"

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': './audios/%(title)s - %(uploader)s.%(ext)s',
            'ffmpeg_location': FFMPEG_PATH,
            'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
            'noplaylist': True,
            'default_search': 'ytsearch1:',
            'ignoreerrors': True,
        }

        os.makedirs('./audios', exist_ok=True)

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)

            if 'entries' in info and info['entries']:
                info = info['entries'][0]

            title = info.get('title', 'Unknown Title')
            artist = info.get('uploader', info.get('artist', 'Unknown Artist'))
            full_title = f"{artist} - {title}"
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', full_title) + ".mp3"

            filename = ydl.prepare_filename(info)
            mp3_filename = os.path.splitext(filename)[0] + ".mp3"

            if not os.path.exists(mp3_filename):
                await message.answer("❌ Не удалось найти или скачать трек")
                await state.clear()
                return

            await message.answer(DOWNLOADING_TRACK_MESSAGE.format(title=full_title))

            audio_file = FSInputFile(mp3_filename)
            await message.answer_audio(audio_file, title=title, performer=artist)

            os.remove(mp3_filename)

        await message.answer(SUCCESS_MESSAGE)

    except Exception as e:
        await message.answer(SPOTIFY_ERROR_MESSAGE + str(e)[:200])
    finally:
        await state.clear()