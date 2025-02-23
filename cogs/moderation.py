import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.media_only_channels = set()  # Armazena IDs de canais configurados como "media-only"
        self.staff_role_id = None  # Variável para armazenar o ID do cargo de staff

    def has_permissions(self, ctx):
        """Verifica se o usuário tem permissão para executar comandos."""
        if ctx.author.guild_permissions.administrator:
            return True
        if self.staff_role_id and ctx.guild.get_role(self.staff_role_id) in ctx.author.roles:
            return True
        return False

    @commands.command(name="setstaff")
    @commands.has_permissions(administrator=True)
    async def setstaff(self, ctx, role: discord.Role):
        """Define o cargo de staff que pode executar comandos de moderação."""
        self.staff_role_id = role.id
        await ctx.send(f"✅ O cargo de staff foi definido como {role.mention}.")

    @commands.command(name="varrer")
    async def varrer(self, ctx):
        """Exclui todas as mensagens de um canal que não contenham mídia."""
        if not self.has_permissions(ctx):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        await ctx.send("Iniciando a limpeza de mensagens sem mídia...")
        deleted_count = 0

        async for message in ctx.channel.history(limit=100):  # Limite de 100 mensagens por vez
            if not message.attachments and not message.embeds:  # Verifica se a mensagem não tem mídia
                await message.delete()
                deleted_count += 1

        await ctx.send(f"Foram excluídas {deleted_count} mensagens sem mídia.")

    @commands.command(name="lock")
    async def lock(self, ctx):
        """Bloqueia o canal para que apenas administradores e staff possam enviar mensagens."""
        if not self.has_permissions(ctx):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"🔒 O canal {channel.mention} foi bloqueado.")

    @commands.command(name="unlock")
    async def unlock(self, ctx):
        """Desbloqueia o canal para permitir mensagens novamente."""
        if not self.has_permissions(ctx):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(f"🔓 O canal {channel.mention} foi desbloqueado.")

    @commands.command(name="clean")
    async def clean(self, ctx, amount: int):
        """Remove uma quantidade específica de mensagens de um canal."""
        if not self.has_permissions(ctx):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        if amount <= 0:
            await ctx.send("Por favor, especifique um número positivo de mensagens para limpar.")
            return

        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 para incluir o comando
        await ctx.send(f"🧹 Foram excluídas {len(deleted) - 1} mensagens.", delete_after=5)

    @commands.command(name="mediaonly")
    async def mediaonly(self, ctx):
        """Configura o canal para aceitar apenas mensagens com mídia."""
        if not self.has_permissions(ctx):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        channel_id = ctx.channel.id
        if channel_id in self.media_only_channels:
            await ctx.send("Este canal já está configurado como 'media-only'.")
            return

        self.media_only_channels.add(channel_id)
        await ctx.send(f"📷 O canal {ctx.channel.mention} agora aceita apenas mensagens com mídia.")

    @commands.command(name="nomedia")
    async def nomedia(self, ctx):
        """Desativa o modo 'media-only' de um canal."""
        if not self.has_permissions(ctx):
            await ctx.send("❌ Você não tem permissão para usar este comando.")
            return

        channel_id = ctx.channel.id
        if channel_id not in self.media_only_channels:
            await ctx.send("Este canal não está configurado como 'media-only'.")
            return

        self.media_only_channels.remove(channel_id)
        await ctx.send(f"📝 O canal {ctx.channel.mention} foi restaurado ao comportamento normal.")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Exclui automaticamente mensagens sem mídia em canais 'media-only'."""
        if message.author.bot:
            return

        if message.channel.id in self.media_only_channels:
            if not message.attachments and not message.embeds:
                await message.delete()

# Setup do cog
async def setup(bot):
    await bot.add_cog(Moderation(bot))