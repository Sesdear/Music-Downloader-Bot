from aiogram.types import Message, FSInputFile
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from vkpymusic import Service
import os
import re
import aiohttp

router = Router()

class VKMUrl(StatesGroup):
    url_or_query = State()

@router.message(Command("vkmusic"))
async def vk_start(message: Message, state: FSMContext):
    await message.answer("Отправьте ссылку на трек/альбом/плейлист VK или название для поиска")
    await state.set_state(VKMUrl.url_or_query)

@router.message(VKMUrl.url_or_query)
async def download_vk_music(message: Message, state: FSMContext):
    query = message.text.strip()

    try:
        service = Service()

        await message.answer("🔍 Обрабатываю...")

        if "vk.com" in query.lower() or "audio" in query:
            tracks = service.search_songs_by_text(query, count=5)
        else:
            tracks = service.search_songs_by_text(query, count=1)

        if not tracks:
            await message.answer("❌ Ничего не найдено")
            await state.clear()
            return

        track = tracks[0]

        artist = track.artist or "Unknown"
        title = track.title
        full_title = f"{artist} - {title}"
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', full_title) + ".mp3"

        await message.answer(f"⬇️ Скачиваю: {full_title}")

        os.makedirs("./audios", exist_ok=True)
        filename = f"./audios/{safe_filename}"

        if not track.url:
            await message.answer("❌ Нет прямой ссылки для скачивания")
            await state.clear()
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(track.url) as resp:
                if resp.status != 200:
                    await message.answer(f"❌ Ошибка загрузки: {resp.status}")
                    await state.clear()
                    return
                with open(filename, "wb") as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        f.write(chunk)

        audio_file = FSInputFile(filename)
        await message.answer_audio(audio_file, title=title, performer=artist)

        os.remove(filename)

        await message.answer("✅ Готово!")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)[:200]}")
    finally:
        await state.clear()

def extract_vk_track_id(url: str) -> str | None:
    match = re.search(r"audio(-?\d+)_(\d+)", url)
    if match:
        return f"{match.group(1)}_{match.group(2)}"
    return None