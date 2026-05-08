import os
import discord
import wikipedia
from discord.ext import commands

# Configure Wikipedia to use English
wikipedia.set_lang("en")

# Bot setup with required intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {mirray77_} (ID: {bot1500447087291273349.id})")
    print("Cat Bot Wiki is ready.")


@bot.command(name="cat")
async def cat_info(ctx, *, topic: str = "cat"):
    """
    Fetch cat-related information from Wikipedia.
    Usage: !cat              — summary about cats
           !cat <topic>      — e.g. !cat Persian cat
    """
    # Ensure the query is cat-related
    query = topic if "cat" in topic.lower() else f"{topic} cat"

    async with ctx.typing():
        try:
            summary = wikipedia.summary(query, sentences=4, auto_suggest=True)
            page = wikipedia.page(query, auto_suggest=True)

            embed = discord.Embed(
                title=page.title,
                url=page.url,
                description=summary,
                color=discord.Color.orange(),
            )
            embed.set_footer(text="Source: Wikipedia • Cat Bot Wiki #7727")
            await ctx.send(embed=embed)

        except wikipedia.exceptions.DisambiguationError as e:
            # Multiple results — pick the first cat-related option
            options = [opt for opt in e.options if "cat" in opt.lower()] or e.options[:5]
            embed = discord.Embed(
                title="Multiple results found",
                description="Did you mean one of these?\n" + "\n".join(f"• {opt}" for opt in options[:5]),
                color=discord.Color.gold(),
            )
            embed.set_footer(text="Try: !cat <specific topic>")
            await ctx.send(embed=embed)

        except wikipedia.exceptions.PageError:
            await ctx.send(
                f"❌ No Wikipedia page found for **{topic}**. "
                "Try a different search term, e.g. `!cat Persian cat`."
            )

        except Exception as e:
            print(f"Unexpected error in !cat command: {e}")
            await ctx.send("⚠️ Something went wrong while fetching cat info. Please try again later.")


@bot.command(name="catfact")
async def cat_fact(ctx):
    """
    Fetch a random fact from the main Wikipedia 'Cat' article.
    Usage: !catfact
    """
    async with ctx.typing():
        try:
            summary = wikipedia.summary("Cat", sentences=2, auto_suggest=False)
            embed = discord.Embed(
                title="🐱 Cat Fact",
                description=summary,
                color=discord.Color.orange(),
            )
            embed.set_footer(text="Source: Wikipedia • Cat Bot Wiki #7727")
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Unexpected error in !catfact command: {e}")
            await ctx.send("⚠️ Something went wrong while fetching a cat fact. Please try again later.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Unknown command. Try `!cat` or `!catfact`.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ Missing argument. Usage: `!cat <topic>`")
    else:
        print(f"Unhandled error: {error}")


# Read token from environment and start the bot
token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise RuntimeError("DISCORD_TOKEN environment variable is not set.")

bot.run(token)
