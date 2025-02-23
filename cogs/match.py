import discord
from discord.ext import commands
import random
import json
import os

# ID do canal onde as mensagens de match serão enviadas (substitua pelo ID real do seu canal)
MATCH_CHANNEL_ID = 1342055742072557609

class Match(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.matches_file = "matches.json"
        self.match_messages = {}  # Armazena IDs das mensagens de match {user_id: message_id}
        self.load_matches()

    def load_matches(self):
        """Carrega os dados de matches do arquivo JSON."""
        if os.path.exists(self.matches_file):
            with open(self.matches_file, "r") as file:
                data = json.load(file)
                self.matches_data = data.get("matches", {})
                self.match_messages = data.get("match_messages", {})
        else:
            self.matches_data = {}
            self.match_messages = {}

    def save_matches(self):
        """Salva os dados de matches no arquivo JSON."""
        with open(self.matches_file, "w") as file:
            json.dump({"matches": self.matches_data, "match_messages": self.match_messages}, file, indent=4)

    @commands.command(name="match", aliases=["m"])
    async def match_me(self, ctx):
        """Registra o membro como disponível para match."""
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        if guild_id not in self.matches_data:
            self.matches_data[guild_id] = []

        if user_id in self.matches_data[guild_id]:
            await ctx.send("Você já está registrado para encontrar um match!", delete_after=5)
            return

        self.matches_data[guild_id].append(user_id)
        self.save_matches()

        # Envia a mensagem no canal de match
        match_channel = self.bot.get_channel(MATCH_CHANNEL_ID)
        if not match_channel:
            await ctx.send("O canal de match não foi configurado corretamente.", delete_after=5)
            return

        embed = discord.Embed(
            title=f"{ctx.author.name} está disponível para match!",
            description="Reaja com ❤️ se estiver interessado ou 💔 caso contrário.",
            color=discord.Color.purple()
        )
        embed.set_image(url=ctx.author.avatar.url)  # Define a imagem principal como a foto de perfil
        embed.set_footer(text=f"ID do usuário: {ctx.author.id}")

        message = await match_channel.send(embed=embed)
        await message.add_reaction("❤️")
        await message.add_reaction("💔")

        # Salva o ID da mensagem para referência futura
        self.match_messages[user_id] = message.id
        self.save_matches()

        await ctx.send("Você foi registrado para encontrar um match! Sua mensagem foi enviada ao canal de match.", delete_after=5)

    @commands.command(name="unmatch", aliases=["um"])
    async def unmatch_me(self, ctx):
        """Remove o membro da lista de disponíveis para match."""
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        if guild_id not in self.matches_data or user_id not in self.matches_data[guild_id]:
            await ctx.send("Você não está registrado para encontrar um match.", delete_after=5)
            return

        # Remove o usuário da lista de matches
        self.matches_data[guild_id].remove(user_id)

        # Remove a mensagem do canal de match, se existir
        match_channel = self.bot.get_channel(MATCH_CHANNEL_ID)
        if user_id in self.match_messages:
            message_id = self.match_messages.pop(user_id)
            try:
                message = await match_channel.fetch_message(message_id)
                await message.delete()
            except discord.NotFound:
                pass  # A mensagem já foi excluída manualmente

        self.save_matches()
        await ctx.send("Você foi removido da lista de matches e sua mensagem foi apagada.", delete_after=5)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Lida com reações nas mensagens de match."""
        if payload.channel_id != MATCH_CHANNEL_ID:
            return

        # Verifica se a reação é válida
        if str(payload.emoji) not in ["❤️", "💔"]:
            return

        # Obtém a mensagem e o autor original
        match_channel = self.bot.get_channel(payload.channel_id)
        try:
            message = await match_channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        # Verifica se a mensagem pertence ao sistema de match
        for user_id, message_id in self.match_messages.items():
            if message_id == payload.message_id:
                member = self.bot.get_user(int(user_id))
                reactor = self.bot.get_user(payload.user_id)

                if not member or not reactor:
                    return

                # Notifica o autor da reação
                if str(payload.emoji) == "❤️":
                    await reactor.send(f"Você reagiu com ❤️ à mensagem de match de {member.name}. Entre em contato!")
                elif str(payload.emoji) == "💔":
                    await reactor.send(f"Você reagiu com 💔 à mensagem de match de {member.name}. Sem problemas!")

async def setup(bot):
    await bot.add_cog(Match(bot))