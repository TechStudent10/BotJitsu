import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
from gtts import gTTS
import os
import asyncio

from constants import *

from match import Match

load_dotenv("../.env")

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

matches = {}

async def start_match(ctx: commands.Context, player_one: discord.Member, player_two: discord.Member):
    match = Match(player_one, player_two)
    matches[match.id] = match
    await play_audio(ctx, f"Starting match, {player_one.display_name} vs. {player_two.display_name}, in 3... 2... 1... GO!")
    await asyncio.sleep(9)

    print(str(match.player_one_hand))
    print(str(match.player_two_hand))

    round_num = 0
    while not match.ended:
        round_num += 1
        msg = "Play a card, your hand consists of\n\n```{hand}```\n\n The message format should look like so:\n\n```element power```.\n\n**You may need to send the message twice**"
        p1_element, p1_power, p2_element, p2_power = None, None, None, None
        restart_p1 = True
        restart_p2 = True

        while restart_p1 and restart_p2:
            p1_msg = await player_one.send(msg.format(hand="\n".join(str(match.player_one_hand).split(", "))))
            p2_msg = await player_two.send(msg.format(hand="\n".join(str(match.player_two_hand).split(", "))))

            def check_p1(m: discord.Message):
                if m.channel.id == player_one.dm_channel.id:
                    return True
                return False

            def check_p2(m: discord.Message):
                if m.channel.id == player_two.dm_channel.id:
                    return True
                return False

            p1_res: discord.Message = await bot.wait_for("message", check=check_p1)
            p2_res: discord.Message = await bot.wait_for("message", check=check_p2)

            forfeit_text = "{player_one} forfeit against {player_two}. {player_two} wins!"

            if p1_res.content.lower() == "forfeit":
                text = forfeit_text.format(player_one=player_one.display_name, player_two=player_two.display_name)
                await play_audio(ctx, text)
                await player_one.send(text)
                await player_two.send(text)
                match.end()
                continue

            if p2_res.content.lower() == "forfeit":
                text = forfeit_text.format(player_one=player_two.display_name, player_two=player_one.display_name)
                await play_audio(ctx, text)
                await player_one.send(text)
                await player_two.send(text)
                match.end()
                continue
 
            p1_element, p1_power = p1_res.content.split(" ")
            p2_element, p2_power = p2_res.content.split(" ")

            p1_element = p1_element.lower()
            p2_element = p2_element.lower()

            try:
                int(p1_power)
                restart_p1 = False
            except ValueError:
                await player_one.send("Power must be a number")
                restart_p1 = True
                continue

            try:
                int(p2_power)
                restart_p2 = False
            except ValueError:
                await player_two.send("Power must be a number")
                restart_p2 = True
                continue

            possible_elements = {"fire": 0, "water": 1, "snow": 2}
            if p1_element not in possible_elements:
                await player_one.send(f"{p1_element} is not a valid element.")
                restart_p1 = True
                continue

            if p2_element not in possible_elements:
                await player_two.send(f"{p2_element} is not a valid element")
                restart_p2 = True
                continue

            p1_card = match.player_one_hand.use_card(possible_elements[p1_element], int(p1_power))
            p2_card = match.player_two_hand.use_card(possible_elements[p2_element], int(p2_power))

            if p1_card is None:
                await player_one.send(f"You do not have a {p1_element} card with power {p1_power}.")
                restart_p1 = True
                continue
            
            if p2_card is None:
                await player_two.send(f"You do not have a {p2_element} card with power {p2_power}.")
                restart_p2 = True
                continue

        match.player_one_hand.add_card(match.deck.deal())
        match.player_two_hand.add_card(match.deck.deal())
        p1_power = int(p1_power)
        p2_power = int(p2_power)

        await player_one.send(f"You chose {p1_element} with power of {p1_power}")
        await player_two.send(f"You chose {p2_element} with power of {p2_power}")

        text = ""
        if p1_element == "fire" and p2_element == "snow" or \
            p1_element == "snow" and p2_element == "water" or \
                p1_element == "water" and p2_element == "fire" or \
                    p1_element == p2_element and p1_power > p2_power:
                text = f"{player_one.display_name} beat {player_two.display_name} in round {round_num}."
        
        elif p2_element == "fire" and p1_element == "snow" or \
            p2_element == "snow" and p1_element == "water" or \
                p2_element == "water" and p1_element == "fire" or \
                    p2_element == p1_element and p2_power > p1_power:
                text = f"{player_two.display_name} beat {player_one.display_name} in round {round_num}."

        if match.player_one_bank.hasWon():
            text = f"{player_one.display_name} has won against {player_two.display_name}. Feel free to play again!"
            match.end()

        if match.player_two_bank.hasWon():
            text = f"{player_two.display_name} has won against {player_one.display_name}. Feel free to play again!"
            match.end()

        await player_one.send(text)
        await player_two.send(text)
        await play_audio(ctx, text)

@bot.event
async def on_ready():
    print("Ready!")

async def play_audio(ctx: commands.Context, text: str, text_name: None or str = None):
    await ctx.respond(text)
    filename = text_name or "voice.mp3"
    tts = gTTS(text=text, lang="en")
    tts.save(filename)

    source = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(
            executable=os.getenv("FFMPEG"),
            source=filename
        )
    )
    ctx.voice_client.play(source)

@bot.slash_command(
    name="challenge",
    description="Challenge a player to a game of CardJitsu!"
)
async def challenge_player(ctx: commands.Context, player: discord.Member):
    vc = ctx.voice_client
    if vc is not None:
        pass
    else:
        vc = ctx.author.voice.channel
        if vc is not None:
            await vc.connect()
        else:
            await ctx.respond(f"Must be in a voice channel")
            return

    if player.bot:
        await play_audio(ctx, "You cannot challenge a bot.")
        return

    if ctx.author.name == player.name:
        await play_audio(ctx, "You cannot challenge yourself (you have a 100% chance of winning, where's the fun in that?)")
        return

    if player.id not in vc.voice_states.keys():
        await play_audio(ctx, "Player not in VC.")
        return

    await play_audio(ctx, f"Challenging {player.display_name}", "challenger.mp3")

    class DoYouAccept(discord.ui.View):
        async def on_timeout(self) -> None:
            for child in self.children:
                child.disabled = True

            await self.message.edit(content="You took too long.")
        
        @discord.ui.button(label="Yes", style=discord.ButtonStyle.primary)
        async def challenge_yes(self, button, interaction):
            await interaction.response.send_message("Challenge accepted")
            await ctx.send(f"{player.display_name} accepted your challenge.")
            future = asyncio.ensure_future(start_match(ctx, ctx.author, player))

        @discord.ui.button(label="No", style=discord.ButtonStyle.red)
        async def challenge_no(self, button, interaction):
            await interaction.response.send_message("Challenge declined")
            await play_audio(ctx, f"{player.display_name} declined your challenge.")

    # TODO: send DM to user who got challenged, ask weather they accept or not
    await player.send(f"{player.mention} DO YOU ACCEPT THIS CHALLENGE?!", view=DoYouAccept())
    # TODO: if they say yes, listen for when they join the VC
    # TODO: when they join, begin match

@bot.slash_command(
    description="Connect to the VC"
)
async def connect(ctx: commands.Context, *, channel: discord.VoiceChannel):
    if ctx.voice_client is not None:
        await ctx.respond("Joined")
        return await ctx.voice_client.move_to(channel)

    await channel.connect()
    await ctx.respond("Joined")

bot.run(os.getenv("TOKEN"))
