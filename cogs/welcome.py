import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Substitua pelo ID real do canal de boas-vindas
        self.welcome_channel_id = 1300574702418264095  # ID do canal

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Envia uma mensagem de boas-vindas quando um novo membro entra no servidor."""
        if not self.welcome_channel_id:
            return  # Sai silenciosamente se o ID não foi definido

        welcome_channel = member.guild.get_channel(self.welcome_channel_id)
        if not welcome_channel:
            return  # Sai silenciosamente se o canal não existir

        embed = discord.Embed(
            title="Bem-vindo!",
            description=f"{member.mention}, seja bem-vindo ao servidor!",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await welcome_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))