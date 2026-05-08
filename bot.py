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

bot.run(MTUwMDQ0NzA4NzI5MTI3MzM0OQ.GyUiXn.AB6PL9Yizkv-5_TJg4pqyxNjaYVdC62HD2ypG4) 
import os
token = os.environ.get("MTUwMDQ0NzA4NzI5MTI3MzM0OQ.GyUiXn.AB6PL9Yizkv-5_TJg4pqyxNjaYVdC62HD2ypG4")
bot.run(MTUwMDQ0NzA4NzI5MTI3MzM0OQ.GyUiXn.AB6PL9Yizkv-5_TJg4pqyxNjaYVdC62HD2ypG4)
import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("🐱 Cat Bot aktif!")

@bot.command()
async def cat(ctx):
    await ctx.send("🐱 miyav!")

@bot.command()
async def miyav(ctx):
    await ctx.send("😺 miyav miyav!")

# Railway'den TOKEN alır
token = os.environ.get("TOKEN")
bot.run(MTUwMDQ0NzA4NzI5MTI3MzM0OQ.GyUiXn.AB6PL9Yizkv-5_TJg4pqyxNjaYVdC62HD2ypG4)
print("🐱 Cat Bot çalışıyor")
import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Wiki ve Eğlence komutlarını yükle
from wiki import setup
setup(bot)

# Veri dosyası
DATA_FILE = "veriler.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_balance(user_id):
    data = load_data()
    return data.get(str(user_id), {"para": 100, "daily": None, "work": None})

def set_balance(user_id, para, daily=None, work=None):
    data = load_data()
    data[str(user_id)] = {"para": para, "daily": daily, "work": work}
    save_data(data)

@bot.event
async def on_ready():
    print(f"🐱 Cat Bot aktif: {bot.user}")
    await bot.change_presence(activity=discord.Game("🐱 !yardım"))

# === TEMEL KOMUTLAR ===

@bot.command()
async def yardım(ctx):
    embed = discord.Embed(
        title="🐱 **KEDİ BOTU KOMUTLARI**",
        color=discord.Color.orange()
    )
    embed.add_field(name="📌 Temel", value="`!cat` `!miyav` `!help` `!yardım` `!mood` `!no` `!uyarı` `!ping`", inline=False)
    embed.add_field(name="📚 Wiki", value="`!wiki <konu>` - Wikipedia'dan bilgi getirir", inline=False)
    embed.add_field(name="💰 Ekonomi", value="`!balance` `!daily` `!work` `!gamble` `!rob` `!leaderboard`", inline=False)
    embed.add_field(name="🎉 Eğlence", value="`!8ball` `!catfact` `!catimg` `!catfight` `!ship` `!trivia` `!randomcat` `!roast` `!flamingo` `!pet`", inline=False)
    embed.set_footer(text="Cat Bot Wiki #7727")
    await ctx.send(embed=embed)

@bot.command()
async def cat(ctx):
    mesajlar = ["🐱 miyav!", "😺 miyav miyav~", "🐈 senin için miyavladım!", "😸 purr purr"]
    await ctx.send(random.choice(mesajlar))

@bot.command()
async def miyav(ctx):
    await ctx.send("😺 miyav miyav!")

@bot.command()
async def help(ctx):
    await ctx.send("📌 Tüm komutları görmek için `!yardım` yaz!")

@bot.command()
async def mood(ctx):
    moods = ["😺 Mutlu", "😸 Şirin", "🙀 Meraklı", "😴 Uykulu", "😼 cool", "😻 Sevgi dolu"]
    await ctx.send(random.choice(moods))

@bot.command()
async def no(ctx):
    await ctx.send("🙅‍♀️ NO!")

@bot.command()
async def uyarı(ctx):
    await ctx.send("⚠️ **RESMİ KEDİ UYARISI:** Bu bot fazla tatlı olabilir. Kedi bağımlılığı riski vardır! 🐱")

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

# === EKONOMİ KOMUTLARI ===

@bot.command()
async def balance(ctx):
    user = get_balance(ctx.author.id)
    await ctx.send(f"💰 **{ctx.author.name}** bakiyesi: **{user['para']}** kedi parası")

@bot.command()
async def daily(ctx):
    user = get_balance(ctx.author.id)
    now = datetime.now()
    
    if user['daily']:
        last_daily = datetime.fromisoformat(user['daily'])
        if now - last_daily < timedelta(hours=24):
            kalan = timedelta(hours=24) - (now - last_daily)
            await ctx.send(f"⏰ Günlük ödülü henüz hazır değil! {kalan} saat sonra gel.")
            return
    
    para = random.randint(50, 200)
    new_balance = user['para'] + para
    set_balance(ctx.author.id, new_balance, now.isoformat(), user['work'])
    await ctx.send(f"🎁 Günlük ödülün: **{para}** kedi parası! Toplam: **{new_balance}**")

@bot.command()
async def work(ctx):
    user = get_balance(ctx.author.id)
    now = datetime.now()
    
    if user['work']:
        last_work = datetime.fromisoformat(user['work'])
        if now - last_work < timedelta(hours=1):
            kalan = timedelta(hours=1) - (now - last_work)
            await ctx.send(f"⏰ Çalışmak için {kalan} bekle!")
            return
    
    para = random.randint(20, 100)
    new_balance = user['para'] + para
    set_balance(ctx.author.id, new_balance, user['daily'], now.isoformat())
    await ctx.send(f"💼 Çalıştın! Kazandın: **{para}** kedi parası")

@bot.command()
async def gamble(ctx, miktar: int = None):
    if miktar is None:
        await ctx.send("🎰 Kaç para yatırmak istiyon? `!gamble 100`")
        return
    
    user = get_balance(ctx.author.id)
    
    if miktar > user['para']:
        await ctx.send(f"❌ Yetersiz para! Bakiye: {user['para']}")
        return
    
    if miktar <= 0:
        await ctx.send("❌ Geçersiz miktar!")
        return
    
    if random.random() < 0.5:
        kazanc = miktar * 2
        new_balance = user['para'] + kazanc - miktar
        set_balance(ctx.author.id, new_balance, user['daily'], user['work'])
        await ctx.send(f"🎉 Kazandın! +{kazanc} kedi parası! Toplam: {new_balance}")
    else:
        new_balance = user['para'] - miktar
        set_balance(ctx.author.id, new_balance, user['daily'], user['work'])
        await ctx.send(f"😢 Kaybettin... -{miktar} kedi parası. Kalan: {new_balance}")

@bot.command()
async def rob(ctx, kullanıcı: discord.Member = None):
    if kullanıcı is None:
        await ctx.send("❌ Kimi soyacağını belirt! `!rob @kullanıcı`")
        return
    
    user = get_balance(ctx.author.id)
    victim = get_balance(kullanıcı.id)
    
    if victim['para'] < 10:
        await ctx.send("❌ Bu kişinin parası az, soyamazsın!")
        return
    
    if random.random() < 0.3:
        çalınan = random.randint(10, min(100, victim['para']))
        new_balance = user['para'] + çalınan
        new_victim = victim['para'] - çalınan
        set_balance(ctx.author.id, new_balance, user['daily'], user['work'])
        set_balance(kullanıcı.id, new_victim, victim['daily'], victim['work'])
        await ctx.send(f"😈 Soydun! +{çalınan} kedi parası!")
    else:
        ceza = random.randint(20, 50)
        new_balance = user['para'] - ceza
        set_balance(ctx.author.id, new_balance, user['daily'], user['work'])
        await ctx.send(f"🚨 Yakalandın! -{ceza} kedi parası ceza ödedin!")

@bot.command()
async def leaderboard(ctx):
    data = load_data()
    if not data:
        await ctx.send("📊 Henüz kimse para kazanmamış!")
        return
    
    sıralı = sorted(data.items(), key=lambda x: x[1]['para'], reverse=True)[:5]
    msg = "🏆 **EN ZENGİN KEDİ PARASI SAHİPLERİ**\n\n"
    for i, (user_id, info) in enumerate(sıralı, 1):
        msg += f"{i}. Kullanıcı {user_id}: **{info['para']}** 💰\n"
    await ctx.send(msg)

bot.run("MTUwMDQ0NzA4NzI5MTI3MzM0OQ.GyUiXn.AB6PL9Yizkv-5_TJg4pqyxNjaYVdC62HD2ypG4")
