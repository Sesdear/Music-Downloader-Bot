from yt_dlp import YoutubeDL
from aiogram.types import Message, FSInputFile
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import os

from config import *
from messages_config import *

async def download_soundcloud_mp3(message: Message, url: str):
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': './audios/%(title)s.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': FFMPEG_PATH if os.name == 'nt' else None,
    }
    
    await message.answer(SC_DOWNLOAD_PROCESS)
    
    try:
        with YoutubeDL(ydl_opts) as ydl: #type: ignore
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)
            ydl.download([url])
            
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
            
            if os.path.exists(mp3_filename):
                audio_file = FSInputFile(mp3_filename)
                await message.answer_audio(audio_file)
                os.remove(mp3_filename)
            else:
                await message.answer(SC_MP3_NOT_CREATED_ERROR_MESSAGE)
    except Exception as e:
        await message.answer(f"{GENERAL_ERROR_MESSAGE} {str(e)[:200]}")