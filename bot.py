import os
import discord
from discord.ext import commands
import json
import random
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Veri dosyası
DATA_FILE = "veriler.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_balance(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"para": 100, "daily": None, "work": None}
        save_data(data)
    return data[str(user_id)]

def set_balance(user_id, para, daily, work):
    data = load_data()
    data[str(user_id)] = {"para": para, "daily": daily, "work": work}
    save_data(data)

@bot.event
async def on_ready():
    print(f"🐱 {bot.user} olarak giriş yapıldı!")
    print("Cat Bot aktif!")

@bot.command()
async def cat(ctx):
    await ctx.send("🐱 miyav!")

@bot.command()
async def miyav(ctx):
    await ctx.send("😺 miyav miyav!")

@bot.command()
async def bakiye(ctx):
    user = get_balance(ctx.author.id)
    await ctx.send(f"💰 Bakiyen: **{user['para']}** kedi parası")

@bot.command()
async def daily(ctx):
    user = get_balance(ctx.author.id)
    now = datetime.now()
    
    if user['daily']:
        last_daily = datetime.fromisoformat(user['daily'])
        kalan = (last_daily + timedelta(hours=24)) - now
        if kalan.total_seconds() > 0:
            await ctx.send(f"⏰ Çalışmak için {int(kalan.total_seconds() // 3600)} saat bekle!")
            return
    
    para = random.randint(20, 100)
    new_balance = user['para'] + para
    set_balance(ctx.author.id, new_balance, now.isoformat(), user['work'])
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
        msg += f"{i}. <@{user_id}>: **{info['para']}** 💰\n"
    await ctx.send(msg)

# TOKEN'İ ORTAM DEĞİŞKENİNDEN AL
token = os.environ.get("MTUwMDQ0NzA4NzI5MTI3MzM0OQ.G7-mat.cPyxJNaua4UXdoBk5KGIvq0j45EfuK3zt0d8Bo")
if not token:
    raise RuntimeError("DISCORD_TOKEN environment variable is not set!")

bot.run(MTUwMDQ0NzA4NzI5MTI3MzM0OQ.G7-mat.cPyxJNaua4UXdoBk5KGIvq0j45EfuK3zt0d8Bo)
