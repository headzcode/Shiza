import discord
from discord.ext import commands
import json
import os

# ID do cargo para nível alto (substitua pelo ID real do seu cargo)
HIGH_LEVEL_ROLE_ID = 1334004668828745739
LEVEL_UP_CHANNEL_ID = 1342031811920003083  # Substitua pelo ID do canal de level-up

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "levels.json"
        self.shop_file = "shop.json"
        self.load_data()
        self.load_shop()

    def load_data(self):
        """Carrega os dados de níveis do arquivo JSON."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                self.levels_data = json.load(file)
        else:
            self.levels_data = {}

    def save_data(self):
        """Salva os dados de níveis no arquivo JSON."""
        with open(self.data_file, "w") as file:
            json.dump(self.levels_data, file, indent=4)

    def load_shop(self):
        """Carrega os dados da loja do arquivo JSON."""
        if os.path.exists(self.shop_file):
            with open(self.shop_file, "r") as file:
                self.shop_data = json.load(file)
        else:
            self.shop_data = {}

    def save_shop(self):
        """Salva os dados da loja no arquivo JSON."""
        with open(self.shop_file, "w") as file:
            json.dump(self.shop_data, file, indent=4)

    def get_user_data(self, guild_id, user_id):
        """Obtém ou inicializa os dados de um usuário."""
        if str(guild_id) not in self.levels_data:
            self.levels_data[str(guild_id)] = {}
        if str(user_id) not in self.levels_data[str(guild_id)]:
            self.levels_data[str(guild_id)][str(user_id)] = {"xp": 0, "level": 1}
        return self.levels_data[str(guild_id)][str(user_id)]

    @commands.Cog.listener()
    async def on_message(self, message):
        """Lida com a atribuição de XP quando uma mensagem é enviada."""
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        user_data = self.get_user_data(guild_id, user_id)

        # Atribui XP base por mensagem
        base_xp = 5
        # Bônus por mídia (imagens, vídeos, etc.)
        media_bonus = 10 if any(attachment.content_type.startswith("image") or attachment.content_type.startswith("video") for attachment in message.attachments) else 0
        user_data["xp"] += base_xp + media_bonus

        current_level = user_data["level"]
        xp_needed = current_level * 100  # XP necessário para subir de nível

        # Verifica se o usuário subiu de nível
        if user_data["xp"] >= xp_needed:
            user_data["level"] += 1
            user_data["xp"] -= xp_needed  # Reseta o XP após subir de nível

            # Envia notificação de level-up no canal específico
            level_up_channel = self.bot.get_channel(LEVEL_UP_CHANNEL_ID)
            if level_up_channel:
                await level_up_channel.send(f"🎉 Parabéns {message.author.mention}, você subiu para o nível **{user_data['level']}**!")

            # Verifica se o usuário alcançou o nível alto
            if user_data["level"] >= 10:  # Altere o nível necessário conforme desejar
                role = message.guild.get_role(HIGH_LEVEL_ROLE_ID)
                if role and role not in message.author.roles:
                    await message.author.add_roles(role)
                    await level_up_channel.send(f"🌟 {message.author.mention}, você alcançou o nível alto e recebeu o cargo **{role.name}**!")

        self.save_data()

    @commands.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        """Mostra o nível e XP de um membro."""
        member = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        user_data = self.get_user_data(guild_id, user_id)

        embed = discord.Embed(
            title=f"Nível de {member.name}",
            description=f"Nível: {user_data['level']}\nXP: {user_data['xp']}/{user_data['level'] * 100}",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        """Exibe o ranking de níveis do servidor."""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.levels_data or not self.levels_data[guild_id]:
            await ctx.send("Nenhum dado de nível disponível.")
            return

        leaderboard = sorted(
            self.levels_data[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )[:10]  # Top 10

        embed = discord.Embed(
            title="Leaderboard de Níveis",
            color=discord.Color.gold()
        )
        for index, (user_id, data) in enumerate(leaderboard, start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.name if member else "Usuário desconhecido"
            embed.add_field(
                name=f"{index}. {name}",
                value=f"Nível: {data['level']} | XP: {data['xp']}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="shop")
    async def shop(self, ctx):
        """Mostra os itens disponíveis na loja."""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.shop_data or not self.shop_data[guild_id]:
            await ctx.send("A loja está vazia.")
            return

        embed = discord.Embed(title="Loja de Itens", color=discord.Color.green())
        for item_id, item in self.shop_data[guild_id].items():
            embed.add_field(
                name=item["name"],
                value=f"Custo: {item['cost']} XP | Tipo: {item['type']}",
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command(name="buy")
    async def buy(self, ctx, item_id: str):
        """Compra um item da loja."""
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)
        user_data = self.get_user_data(guild_id, user_id)

        if guild_id not in self.shop_data or item_id not in self.shop_data[guild_id]:
            await ctx.send("Item não encontrado na loja.")
            return

        item = self.shop_data[guild_id][item_id]
        if user_data["xp"] < item["cost"]:
            await ctx.send("Você não tem XP suficiente para comprar este item.")
            return

        # Deduz o custo do XP
        user_data["xp"] -= item["cost"]

        # Aplica o efeito do item
        if item["type"] == "role":
            role = ctx.guild.get_role(item["role_id"])
            if role:
                await ctx.author.add_roles(role)
                await ctx.send(f"Você comprou o cargo {role.name}!")
            else:
                await ctx.send("Cargo não encontrado.")
        elif item["type"] == "item":
            await ctx.send(f"Você comprou o item {item['name']}!")

        self.save_data()

async def setup(bot):
    await bot.add_cog(Levels(bot))