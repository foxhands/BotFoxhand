import os
import discord
import ftplib
from io import BytesIO
from datetime import datetime

# Настройки для подключения к FTP
FTP_HOST = os.getenv("FTP_HOST")
DOMAIN = os.getenv("DOMAIN")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_PATH = os.getenv("FTP_PATH")

# Настройки для названий
VIDEOS = os.getenv("VIDEOS")
IMAGES = os.getenv("IMAGES")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Обработка сообщений с ссылками и изображениями
    await handle_links(message)
    await handle_files(message)

    # Проверяем, если сообщение пришло из текстового канала
    if isinstance(message.channel, discord.TextChannel):
        # Получаем объект голосового канала, в котором находится автор сообщения (если есть)
        voice_channel = message.author.voice.channel

        # Проверяем упоминания пользователей
        for mention in message.mentions:
            if mention != message.author:  # Исключаем самого себя
                inviting_user = message.author
                voice_channel_link = voice_channel.mention if voice_channel else "неизвестный канал"

                # Формируем сообщение для упомянутого пользователя
                invite_message = f"Эй, {mention.mention}! Тебя зовет @{inviting_user.name} в канале {voice_channel_link}."

                # Отправляем сообщение в личные сообщения упомянутому пользователю
                await mention.send(invite_message)
                await message.delete()


async def handle_links(message):
    youtube_links = (
        'https://www.youtube.com/watch?v=',
        'https://youtu.be/',
        'https://www.youtube.com/shorts/',
        'https://www.youtube.com/playlist?list=',
    )

    tiktok_links = (
        'https://vm.tiktok.com/',
        'https://www.tiktok.com/',
        'https://www.tiktok.com/@',
        'https://www.tiktok.com/t/',
        'https://www.tiktok.com/video/',
    )

    if message.content.startswith(youtube_links + tiktok_links):
        # Поиск потока для видео
        thread = discord.utils.get(message.guild.threads, name='Видосики')

        if thread is None:
            await message.channel.send("The 'Видосики' thread was not found.")
        else:
            await thread.send(f"@here {message.content} от {message.author.mention}")
            await message.delete()


async def handle_files(message):
    if message.attachments:
        # Поиск потока для изображений и видео
        image_thread = discord.utils.get(message.guild.threads, name=IMAGES)
        video_thread = discord.utils.get(message.guild.threads, name=VIDEOS)

        if image_thread is None:
            await message.channel.send(f"The {IMAGES} thread was not found.")

        if video_thread is None:
            await message.channel.send(f"The {VIDEOS} thread was not found.")

        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif')):
                await handle_image(attachment, image_thread, message)
            elif any(attachment.filename.lower().endswith(ext) for ext in ('.mp4', '.mov', '.avi', '.mkv')):
                await handle_video(attachment, video_thread, message)


async def handle_image(attachment, thread, message):
    try:
        # Чтение данных изображения
        print(f"Reading image data for {attachment.filename}")
        image_data = await attachment.read()
        # Загрузка изображения на FTP
        print(f"Uploading {attachment.filename} to FTP")
        unique_filename = generate_unique_filename(attachment.filename)
        ftp_url = upload_to_ftp(unique_filename, image_data)
        if ftp_url:
            mention_everyone = '@here'
            # Отправка сообщения в поток с упоминанием пользователя и прикреплением изображения
            embed = discord.Embed(
                title=f"Эй! {mention_everyone}",
                description=f"Тут картинка от {message.author.mention}",
                color=discord.Color.random()
            )
            embed.set_image(url=ftp_url)
            await thread.send(embed=embed)
        await message.delete()
    except Exception as e:
        print(f"Error handling image: {e}")


async def handle_video(attachment, thread, message):
    try:
        # Чтение данных видео
        print(f"Reading video data for {attachment.filename}")
        video_data = await attachment.read()
        # Загрузка видео на FTP
        print(f"Uploading {attachment.filename} to FTP")
        unique_filename = generate_unique_filename(attachment.filename)
        ftp_url = upload_to_ftp(unique_filename, video_data)
        if ftp_url:
            await thread.send(f"@here {ftp_url}, {message.author.mention}")
	await message.delete()
    except Exception as e:
        print(f"Error handling video: {e}")


def generate_unique_filename(filename):
    # Получение текущего времени в формате YYYYMMDD_HHMMSS
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Разделение имени файла на имя и расширение
    name, ext = os.path.splitext(filename)
    # Генерация уникального имени файла
    unique_filename = f"{name}_{timestamp}{ext}"
    return unique_filename


def upload_to_ftp(filename, data):
    try:
        # Подключение к FTP-серверу
        print(f"Connecting to FTP: {FTP_HOST} with user {FTP_USER}")
        with ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS) as ftp:
            try:
                # Попытка перейти в каталог на FTP
                ftp.cwd(FTP_PATH)
            except ftplib.error_perm as e:
                if str(e).startswith('550'):
                    print(f"Directory {FTP_PATH} does not exist. Creating directory.")
                    # Создание каталога, если он не существует
                    make_ftp_dir(ftp, FTP_PATH)
                    # Повторная попытка перейти в каталог после его создания
                    ftp.cwd(FTP_PATH)
                else:
                    raise e

            # Загрузка файла на FTP
            bio = BytesIO(data)
            ftp.storbinary(f'STOR {filename}', bio)
            # Формирование правильного URL
            ftp_url = f'https://{DOMAIN}/file/ds/{filename}'
            print(f"Uploaded file URL: {ftp_url}")
            return ftp_url
    except ftplib.error_perm as e:
        print(f"FTP login failed: {e}")
        raise e


def make_ftp_dir(ftp, path):
    dirs = path.split('/')
    path = ''
    for dir in dirs:
        if dir:
            path += f'/{dir}'
            try:
                # Попытка создать каталог
                ftp.mkd(path)
                print(f"Created directory {path}")
            except ftplib.error_perm as e:
                if not str(e).startswith('550'):
                    raise e
                else:
                    # Если каталог уже существует
                    print(f"Directory {path} already exists.")


try:
    # Получение токена из окружения или использование дефолтного
    token = TOKEN
    if not token:
        raise Exception("Please add your token to the Secrets panel.")
    # Запуск клиента Discord
    client.run(token)
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
    else:
        raise e

