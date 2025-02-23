import discord
from discord.ext import commands
from discord.ui import Button, View
import random
import asyncio
import datetime

# URLs de GIFs/Imagens
GIF_GIRANDO_TAMBOR = "https://cdn.discordapp.com/attachments/1342263504069197824/1342263972648194109/cdd.gif?ex=67ba51bd&is=67b9003d&hm=4d9fa1e3eebbd6f0c82b2b835f0d35ec50e028382cbda84ffac0e0d4977c096d&"  # Substitua pelo URL real
IMAGE_MIRANDO_CABECA = "https://cdn.discordapp.com/attachments/1342263504069197824/1342263972400988252/Kakegurui_-_042017.07.26_14.27.10.jpg?ex=67ba51bd&is=67b9003d&hm=6d55c218056fd46b9b09d017f90703a7a6a25d7e83473d1e04a13942cc149781&"    # Substitua pelo URL real
IMAGE_ELIMINADO = "https://cdn.discordapp.com/attachments/1342263504069197824/1342263972145004666/F2E2HUEXAAEAnM2.jpg_large.jpg?ex=67ba51bd&is=67b9003d&hm=c1f63b075c60c4f2d7878013ff683f917e3d98875765b24d6eeace84b6ef08c7&"              # Substitua pelo URL real

class Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rooms = {}  # Armazena as salas de roleta russa

    @commands.command(name="roleta")
    async def roulette(self, ctx):
        """Inicia um jogo de roleta russa."""
        if ctx.channel.id in self.rooms:
            await ctx.send("Já existe uma sala de roleta russa ativa neste canal.")
            return

        room = {
            "players": [],
            "started": False,
            "message": None,  # Armazena a mensagem principal da sala
        }
        self.rooms[ctx.channel.id] = room

        view = View(timeout=None)
        start_button = Button(label="Começar", style=discord.ButtonStyle.primary)

        async def start_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("Você não pode iniciar este jogo.", ephemeral=True)
                return

            if len(room["players"]) < 2:
                await interaction.response.send_message("É necessário pelo menos 2 jogadores para começar.", ephemeral=True)
                return

            room["started"] = True
            await interaction.response.send_message("O jogo começou!")
            await self.start_game(interaction.channel, room)

        start_button.callback = start_callback
        view.add_item(start_button)

        join_button = Button(label="Entrar", style=discord.ButtonStyle.secondary)

        async def join_callback(interaction):
            if room["started"]:
                await interaction.response.send_message("O jogo já começou.", ephemeral=True)
                return

            if interaction.user in room["players"]:
                await interaction.response.send_message("Você já está na sala.", ephemeral=True)
                return

            room["players"].append(interaction.user)

            # Atualiza a mensagem principal
            embed = discord.Embed(
                title="Roleta Russa",
                description=self.get_player_list(room["players"]),
                color=discord.Color.red()
            )
            if room["message"]:
                await room["message"].edit(embed=embed)
            else:
                room["message"] = await ctx.send(embed=embed, view=view)

            await interaction.response.send_message(f"{interaction.user.mention} entrou no jogo!", ephemeral=True)

        join_button.callback = join_callback
        view.add_item(join_button)

        # Envia a mensagem inicial
        embed = discord.Embed(
            title="Roleta Russa",
            description=self.get_player_list(room["players"]),
            color=discord.Color.red()
        )
        room["message"] = await ctx.send(embed=embed, view=view)

    def get_player_list(self, players):
        """Retorna a lista de jogadores formatada."""
        if not players:
            return "Nenhum jogador na sala."
        return "\n".join([f"- {player.mention}" for player in players])

    async def start_game(self, channel, room):
        """Inicia o jogo de roleta russa."""
        players = room["players"]
        random.shuffle(players)
        rounds = 3  # Número fixo de rodadas
        eliminated = None

        for round_num in range(1, rounds + 1):
            embed = discord.Embed(
                title=f"=== Rodada {round_num}/{rounds} ===",
                description="Preparando para girar o tambor...",
                color=discord.Color.red()
            )
            embed.set_image(url=GIF_GIRANDO_TAMBOR)
            message = await channel.send(embed=embed)
            await asyncio.sleep(4)  # Pausa para criar suspense

            for member in players:
                embed = discord.Embed(
                    title=f"É a vez de {member.name}",
                    description="Mirando na cabeça...",
                    color=discord.Color.red()
                )
                embed.set_image(url=IMAGE_MIRANDO_CABECA)
                await message.edit(embed=embed)
                await asyncio.sleep(2)  # Pausa para animação

                # Simula o gatilho da arma
                if random.randint(0, 5) == 0:  # 1 em 6 chances de "morrer"
                    embed = discord.Embed(
                        title=f"💥 {member.name} foi eliminado!",
                        description="Fim de jogo.",
                        color=discord.Color.red()
                    )
                    embed.set_image(url=IMAGE_ELIMINADO)
                    await message.edit(embed=embed)
                    eliminated = member
                    break
                else:
                    embed = discord.Embed(
                        title=f"✅ {member.name} escapou desta vez!",
                        description="Próximo jogador...",
                        color=discord.Color.green()
                    )
                    await message.edit(embed=embed)
                    await asyncio.sleep(4)  # Pausa para animação

            if eliminated:
                break

        if eliminated:
            await channel.send(f"💀 {eliminated.mention} foi punido! Fim de jogo.")
            try:
                await eliminated.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=10), reason="Castigo da Roleta Russa")
            except Exception as e:
                await channel.send(f"Não foi possível aplicar o timeout ao jogador {eliminated.mention}. Erro: {e}")
        else:
            await channel.send("🎉 Todos sobreviveram às rodadas! Parabéns aos jogadores!")

        del self.rooms[channel.id]

async def setup(bot):
    await bot.add_cog(Roulette(bot))