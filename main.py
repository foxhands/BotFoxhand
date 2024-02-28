import os

import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  # Handle link messages in a separate function
  await handle_links(message)


async def handle_links(message):
  if message.content.startswith((
      'https://www.youtube.com/watch?v=',
      'https://youtu.be/',
      'https://www.youtube.com/shorts/',
      'https://www.youtube.com/playlist?list=',
      'https://vm.tiktok.com/',
      'https://www.tiktok.com/',
      'https://www.tiktok.com/@',
      'https://www.tiktok.com/t/',
      'https://www.tiktok.com/video/',
  )):
    # Search for the thread (case-sensitive)
    thread = discord.utils.get(message.guild.threads, name='Видосики')

    if thread is None:
      # Inform user if the thread is not found
      await message.channel.send(f"The {thread} thread was not found.")

    else:
      # Send a message to the thread
      await thread.send(f"@everyone {message.author}: {message.content}")

    await message.delete()

  # Search for the thread (case-sensitive)
  #thread = discord.utils.get(message.guild.threads, name='Картинки')


try:
  token = os.getenv("TOKEN") or ""
  if token == "":
    raise Exception("Please add your token to the Secrets pane.")
  client.run(token)
except discord.HTTPException as e:
  if e.status == 429:
    print(
        "The Discord servers denied the connection for making too many requests"
    )
    print(
        "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
    )
  else:
    raise e
