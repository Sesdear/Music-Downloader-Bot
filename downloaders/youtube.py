from yt_dlp import YoutubeDL
from aiogram.types import Message, FSInputFile

from messages_config import *
from config import *

import os

async def yt_download_send_mp3(message: Message, url: str):

    
    ydl_opts = {

        'format': 'bestaudio/best',
        'outtmpl': './audios/%(title)s.%(ext)s',
        'noplaylist': True,
        'cookiefile': COOKIES_FILE,
        'quiet': True,
        'writethumbnail': True,
        
        'postprocessors': [

            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },

            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
            }
        ],
        
        'ffmpeg_location': FFMPEG_PATH if os.name == 'nt' else None,
    }
    
    await message.answer(DOWNLOAD_MESSAGE)
    
    try:
        with YoutubeDL(ydl_opts) as ydl: #type: ignore

            info = ydl.extract_info(url, download=False)
            
            temp_filename = ydl.prepare_filename(info)

            mp3_filename = os.path.splitext(temp_filename)[0] + '.mp3'
            
            ydl.download([url])
            
            if not os.path.exists(mp3_filename):
                possible_files = [f for f in os.listdir('./audios') 
                                if os.path.splitext(f)[0] == os.path.splitext(os.path.basename(mp3_filename))[0]]
                if possible_files:
                    mp3_filename = f'./audios/{possible_files[0]}'
                else:
                    raise FileNotFoundError(YT_MP3_NOT_CREATED_ERROR_MESSAGE)
                    return()
            
            audio_file = FSInputFile(mp3_filename)
            await message.answer_audio(audio_file)
            
            os.remove(mp3_filename)
            return()
            
    except Exception as e:
        error_msg = str(e)[:300]
        await message.answer(f"{GENERAL_ERROR_MESSAGE} {error_msg}")
        
        try:
            await message.answer(YT_TRY_LIGHT_METHOD_MESSAGE)
            
            ydl_opts_simple = {
                'format': 'bestaudio/best',
                'outtmpl': './audios/%(title)s.mp3',
                'noplaylist': True,
                'cookiefile': './cookies.txt',
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
            }
            
            with YoutubeDL(ydl_opts_simple) as ydl: #type: ignore
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                ydl.download([url])
                
                if os.path.exists(filename):
                    audio_file = FSInputFile(filename)
                    await message.answer_audio(audio_file)
                    os.remove(filename)
                else:
                    await message.answer(YT_ERROR_DOWNLOAD_2_MESSAGE)
                    return()
                    
        except Exception as e2:
            await message.answer(f"{YT_ERROR_DOWNLOAD_1_MESSAGE} {str(e2)[:200]}")
            return()