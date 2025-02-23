import discord
from discord.ext import commands
import json
import os
import re

# ID do cargo de staff (substitua pelo ID real do seu cargo)
STAFF_ROLE_ID = 1308146553831034982

class AntiLinks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.authorized_users_file = "authorized_users.json"
        self.load_authorized_users()

    def load_authorized_users(self):
        """Carrega a lista de usuários autorizados do arquivo JSON."""
        if os.path.exists(self.authorized_users_file):
            with open(self.authorized_users_file, "r") as file:
                self.authorized_users = json.load(file)
        else:
            self.authorized_users = {}

    def save_authorized_users(self):
        """Salva a lista de usuários autorizados no arquivo JSON."""
        with open(self.authorized_users_file, "w") as file:
            json.dump(self.authorized_users, file, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Filtra mensagens contendo links de servidores Discord."""
        if message.author.bot:
            return

        # Verifica se o usuário é staff, tem permissão de administrador ou é o dono do servidor
        is_staff = any(role.id == STAFF_ROLE_ID for role in message.author.roles)
        has_admin_perms = message.author.guild_permissions.administrator
        is_owner = message.author.id == message.guild.owner_id

        if is_staff or has_admin_perms or is_owner:
            return

        # Regex para detectar links de convite do Discord
        invite_pattern = r"(discord\.gg\/|discordapp\.com\/invite\/|discord\.com\/invite\/)[a-zA-Z0-9]+"
        if re.search(invite_pattern, message.content):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, links de servidores não são permitidos aqui!", delete_after=5
            )

    @commands.command(name="alink")
    async def authorize_link(self, ctx, member: discord.Member):
        """Autoriza ou desautoriza um usuário para enviar links de servidores."""
        # Verifica se o autor do comando é staff, tem permissão de administrador ou é o dono do servidor
        is_staff = any(role.id == STAFF_ROLE_ID for role in ctx.author.roles)
        has_admin_perms = ctx.author.guild_permissions.administrator
        is_owner = ctx.author.id == ctx.guild.owner_id

        if not (is_staff or has_admin_perms or is_owner):
            await ctx.send("Você não tem permissão para usar este comando.", delete_after=5)
            return

        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in self.authorized_users:
            self.authorized_users[guild_id] = []

        if user_id in self.authorized_users[guild_id]:
            # Desautoriza o usuário
            self.authorized_users[guild_id].remove(user_id)
            self.save_authorized_users()
            await ctx.send(f"{member.mention} foi desautorizado para enviar links de servidores.")
        else:
            # Autoriza o usuário
            self.authorized_users[guild_id].append(user_id)
            self.save_authorized_users()
            await ctx.send(f"{member.mention} foi autorizado para enviar links de servidores.")

    @commands.command(name="listauthorized")
    async def list_authorized(self, ctx):
        """Lista todos os usuários autorizados no servidor."""
        # Verifica se o autor do comando é staff, tem permissão de administrador ou é o dono do servidor
        is_staff = any(role.id == STAFF_ROLE_ID for role in ctx.author.roles)
        has_admin_perms = ctx.author.guild_permissions.administrator
        is_owner = ctx.author.id == ctx.guild.owner_id

        if not (is_staff or has_admin_perms or is_owner):
            await ctx.send("Você não tem permissão para usar este comando.", delete_after=5)
            return

        guild_id = str(ctx.guild.id)
        authorized_users = self.authorized_users.get(guild_id, [])

        if not authorized_users:
            await ctx.send("Nenhum usuário está autorizado para enviar links de servidores.")
            return

        members = [ctx.guild.get_member(int(user_id)) for user_id in authorized_users]
        member_list = "\n".join([member.mention for member in members if member])
        embed = discord.Embed(
            title="Usuários Autorizados",
            description=member_list or "Nenhum usuário encontrado.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AntiLinks(bot))