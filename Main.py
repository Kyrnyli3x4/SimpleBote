import asyncio
import os
import random
from telethon import TelegramClient, errors, functions, types
from openpyxl import load_workbook
from datetime import datetime
from Text import FullText

# 🔐 API Telegram
api_id = 22325330
api_hash = '2cd1e042d95dfe4cf34b4d58309820cc'
session_name = 'main_account'


media_folder = 'media'

excel_file = 'result.xlsx'

log_file = 'log.txt'

def read_links_from_excel(filename):
    wb = load_workbook(filename)
    ws = wb.active
    links = []
    for row in ws.iter_rows(min_row=3, max_col=3):
        cell = row[2].value  # индекс 2 = колонка C
        if cell and isinstance(cell, str) and 't.me' in cell:
            links.append(cell.strip())

    for row in ws.iter_rows(min_row=3, min_col=7, max_col=7):
        cell = row[0].value  # колонка G — это index 6, но min_col=7 даёт index 0
        if cell and isinstance(cell, str) and 't.me' in cell:
            links.append(cell.strip())

    return links


# ✏️ Логгер
def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

# 📦 Отправка фото и текста
async def send_media_message(client, entity, message, media_folder):
    try:
        images = [os.path.join(media_folder, f) for f in os.listdir(media_folder)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not images:
            log(f"⚠️ Нет изображений в папке '{media_folder}'")
            return
        photo_path = random.choice(images)
        await client.send_file(entity, photo_path)
        await client.send_message(entity, message, parse_mode="HTML")
        log(f"✅ Сообщение с фото отправлено в: {entity.title}")
    except Exception as e:
        log(f"❌ Ошибка при отправке фото в {getattr(entity, 'title', 'неизвестно')}: {e}")

# 🚀 Основная логика
async def main():
    #links = read_links_from_excel(excel_file)
    links = [
        'https://t.me/Testedies',
        'https://t.me/Lolizesies',
    ]
    log("🚀 Начало работы скрипта")
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()

    for link in links:
        try:
            log(f"➡️ Работаем с: {link}")
            entity = await client.get_entity(link)

            # Пробуем вступить
            try:
                await client(functions.channels.JoinChannelRequest(channel=entity))
                log(f"✅ Вступили в: {link}")
            except errors.UserAlreadyParticipantError:
                log(f"🔹 Уже участник: {link}")
            except Exception as e:
                log(f"❌ Не удалось вступить в {link}: {e}")
                continue

            # Канал с обсуждением
            if isinstance(entity, types.Channel) and entity.broadcast:
                posts = await client.get_messages(entity, limit=10)
                discussion_found = False
                for post in posts:
                    if post.replies and post.replies.comments and post.replies.channel_id:
                        try:
                            discussion_chat = await client.get_entity(post.replies.channel_id)
                            await send_media_message(client, discussion_chat, FullText, media_folder)
                            discussion_found = True
                            break
                        except Exception as e:
                            log(f"❌ Ошибка при получении обсуждения поста {post.id} в {link}: {e}")
                if not discussion_found:
                    log(f"⚠️ Нет обсуждаемых постов в канале {link}")

            # Обычная группа или чат
            elif isinstance(entity, (types.Chat, types.Channel)):

                await send_media_message(client, entity, FullText, media_folder)



            # Пауза
            delay = random.uniform(7, 12)
            log(f"⏳ Ждём {round(delay, 2)} сек перед следующим")
            await asyncio.sleep(delay)

            # Покидаем
            try:
                await client(functions.channels.LeaveChannelRequest(channel=entity))
                log(f"🚪 Вышли из: {link}")
            except Exception as e:
                log(f"⚠️ Не удалось выйти из {link}: {e}")

        except Exception as e:
            log(f"❌ Ошибка при обработке {link}: {e}")

    await client.disconnect()
    log("✅ Скрипт завершил работу")

if __name__ == '__main__':
    asyncio.run(main())


