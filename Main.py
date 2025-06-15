from telethon import TelegramClient, errors, functions, types
import asyncio
import os
import random

api_id = 22325330
api_hash = '2cd1e042d95dfe4cf34b4d58309820cc'
session_name = 'main_account'
message_text = 'Привет! Это тестовое сообщение.'

target_links = [
    'https://t.me/Lolizesies',
    'https://t.me/Testedies',
]
media_folder = 'media'

async def send_media_message(client, entity, message, media_folder):
    try:
        images = [os.path.join(media_folder, f) for f in os.listdir(media_folder)
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        if not images:
            print('⚠️ Нет изображений в папке media/')
            return

        photo_path = random.choice(images)
        await client.send_file(entity, photo_path, caption=message)
        print(f'📸 Отправлено сообщение с фото: {photo_path}')
    except Exception as e:
        print(f'❌ Ошибка при отправке фото: {e}')

# 🧠 Основная логика
async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()

    for link in target_links:
        try:
            print(f'\n➡️ Работаем с {link}')
            entity = await client.get_entity(link)

            # Пробуем вступить
            try:
                await client(functions.channels.JoinChannelRequest(channel=entity))
                print(f'✅ Вступили в {link}')
            except errors.UserAlreadyParticipantError:
                print(f'🔹 Уже участник {link}')
            except Exception as e:
                print(f'❌ Не удалось вступить в {link}: {e}')
                continue

            # Если это канал
            if isinstance(entity, types.Channel) and entity.broadcast:
                posts = await client.get_messages(entity, limit=10)
                discussion_found = False
                for post in posts:
                    if post.replies and post.replies.comments and post.replies.channel_id:
                        try:
                            discussion_chat = await client.get_entity(post.replies.channel_id)
                            await send_media_message(client, discussion_chat, message_text, media_folder)
                            print(f'📩 Комментарий отправлен в обсуждение к посту {post.id}')
                            discussion_found = True
                            break
                        except Exception as e:
                            print(f'❌ Ошибка при получении обсуждения: {e}')
                if not discussion_found:
                    print(f'⚠️ Нет обсуждаемых постов в канале {link}')

            # Если это супергруппа или чат
            elif isinstance(entity, (types.Chat, types.Channel)):
                await send_media_message(client, entity, message_text, media_folder)

            # ⏳ Задержка 7–12 сек
            delay = random.uniform(7, 12)
            print(f'⏳ Ждём {round(delay, 2)} секунд...')
            await asyncio.sleep(delay)

            # Покидаем чат/канал
            try:
                await client(functions.channels.LeaveChannelRequest(channel=entity))
                print(f'🚪 Вышли из {link}')
            except Exception as e:
                print(f'⚠️ Не удалось выйти из {link}: {e}')

        except Exception as e:
            print(f'❌ Ошибка при обработке {link}: {e}')

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())