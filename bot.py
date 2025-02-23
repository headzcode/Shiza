import discord
from discord.ext import commands
import os

# Configurações iniciais
intents = discord.Intents.default()
intents.members = True  # Permite acesso aos membros do servidor
intents.message_content = True  # Permite acesso ao conteúdo das mensagens

# Carregar o token do arquivo token.txt
with open("token.txt", "r") as file:
    TOKEN = file.read().strip()

# Prefixo do bot
bot = commands.Bot(command_prefix=".", intents=intents)

# Evento de inicialização
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Moderação | !help"))
    print("Carregando extensões...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Extensão carregada: {filename[:-3]}")

# Executar o bot
if __name__ == "__main__":
    bot.run(TOKEN)