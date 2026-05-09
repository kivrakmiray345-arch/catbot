import os
import discord
from discord.ext import commands
import json
import random
from datetime import datetime, timedelta
import aiohttp

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

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
    """Miyav! Rastgele komik kedi sesi ve meme."""
    sesler = [
        "miyav!", "meow!", "miaou!", "mrrrow!", "miyav miyav!",
        "MIYAV!", "mreow~", "prrr... miyav!", "miyav? 👀", "miau!",
        "nyaa~", "miyaaaaav!", "meow meow meow!", "mrrp!", "miyav 😤",
    ]
    ses = random.choice(sesler)

    # Komik kedi meme URL listesi (yedek olarak kullanılır)
    meme_urls = [
        "https://i.imgur.com/LbDCmBP.jpeg",  # business cat
        "https://i.imgur.com/Oj3GtQS.jpeg",  # grumpy cat
        "https://i.imgur.com/vKFMOEP.jpeg",  # keyboard cat
        "https://i.imgur.com/3GNyBme.jpeg",  # surprised pikachu cat
        "https://i.imgur.com/sHQFRBa.jpeg",  # woman yelling at cat
        "https://i.imgur.com/nFDHMfN.jpeg",  # cat loaf
        "https://i.imgur.com/0Fy7Ybz.jpeg",  # cat in box
        "https://i.imgur.com/JFHjILJ.jpeg",  # ceiling cat
        "https://i.imgur.com/wkRNBpz.jpeg",  # cat with glasses
        "https://i.imgur.com/5YDPQYB.jpeg",  # dramatic cat
        "https://i.imgur.com/XgPHmqe.jpeg",  # cat judge
        "https://i.imgur.com/hUkSoSo.jpeg",  # cat stare
    ]

    embed = discord.Embed(
        title=f"🐱 {ses}",
        color=0xFF9900,
    )

    # Önce cataas.com'dan komik kedi meme almayı dene
    image_set = False
    try:
        async with aiohttp.ClientSession() as session:
            # cataas: kedi + rastgele komik metin
            tags = ["funny", "meme", "grumpy", "lol", "cute"]
            tag = random.choice(tags)
            url = f"https://cataas.com/cat/{tag}?json=true"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=4)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    cat_id = data.get("_id") or data.get("id")
                    if cat_id:
                        embed.set_image(url=f"https://cataas.com/cat/{cat_id}")
                        image_set = True
    except Exception:
        pass

    if not image_set:
        embed.set_image(url=random.choice(meme_urls))

    embed.set_footer(text="🐾 Kedi Bot — miyav!")
    await ctx.send(embed=embed)

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

# ── 8ball ──────────────────────────────────────────────────────────────────
@bot.command(name="8ball")
async def eightball(ctx, *, soru: str = None):
    """Kedi kehaneti — soruyu kediye sor!"""
    if soru is None:
        await ctx.send("🎱 Bir soru sormadan kehanet olmaz! `!8ball sorun nedir?`")
        return

    cevaplar = [
        "😸 Kesinlikle evet! Kedi onayladı.",
        "🐱 Evet, miyav!",
        "😺 Bence öyle.",
        "🐾 İşaretler evet diyor.",
        "😼 Şüpheli... ama belki.",
        "🙀 Bunu bilmiyorum, sor bakalım.",
        "😾 Hayır, kesinlikle hayır.",
        "🐱 Cevap bulanık, tekrar dene.",
        "😿 Hayır, kedi reddetti.",
        "🐾 Kesinlikle hayır! Miyav!",
        "😸 Çok muhtemel!",
        "😼 Pek sanmıyorum...",
    ]
    await ctx.send(f"🎱 **Soru:** {soru}\n**Kedi Kehaneti:** {random.choice(cevaplar)}")


# ── balance ─────────────────────────────────────────────────────────────────
@bot.command(name="balance")
async def balance(ctx):
    """Bakiyeni gör (bakiye komutunun İngilizce alias'ı)."""
    user = get_balance(ctx.author.id)
    await ctx.send(f"💰 Bakiyen: **{user['para']}** kedi parası")


# ── catfact ─────────────────────────────────────────────────────────────────
@bot.command()
async def catfact(ctx):
    """Rastgele gerçek bir kedi bilgisi."""
    gercekler = [
        "🐱 Kediler günde ortalama 12-16 saat uyur.",
        "🐾 Bir kedinin burnu parmak izi gibi benzersizdir.",
        "😸 Kediler tatlı tadını alamaz — tatlı reseptörleri yok!",
        "🐱 Kediler 'miyav' sesini yalnızca insanlarla iletişim için çıkarır.",
        "😺 Bir kedi düşerken her zaman ayakları üzerine iner — bu 'kedi hakemliği' refleksidir.",
        "🐾 Kedilerin 32 kulak kası vardır ve kulaklarını 180 derece döndürebilirler.",
        "😼 Kediler saatte 48 km'ye kadar koşabilir.",
        "🙀 Bir kedinin kalp atışı dakikada 140-220 arasındadır.",
        "🐱 Kediler koku almak için ağızlarını açar — buna 'flehmen tepkisi' denir.",
        "😸 Dünyanın en yaşlı kedisi 38 yıl yaşadı!",
        "🐾 Kediler mırıldanarak hem mutluluklarını hem de streslerini ifade eder.",
        "😺 Bir kedinin iskeleti 230 kemikten oluşur; insanınki 206.",
    ]
    await ctx.send(random.choice(gercekler))


# ── catfight ────────────────────────────────────────────────────────────────
@bot.command()
async def catfight(ctx, rakip: discord.Member = None):
    """İki kedi arasında epik bir dövüş!"""
    if rakip is None:
        await ctx.send("⚔️ Kiminle dövüşeceğini belirt! `!catfight @kullanıcı`")
        return
    if rakip == ctx.author:
        await ctx.send("🐱 Kendinle dövüşemezsin, bu biraz üzücü olurdu...")
        return

    kazanan = random.choice([ctx.author, rakip])
    kaybeden = rakip if kazanan == ctx.author else ctx.author

    hareketler = [
        "pençe saldırısı",
        "tüy savurma",
        "miyav çığlığı",
        "kuyruk tokadı",
        "süper zıplama",
        "gizli tırmalama",
    ]
    hareket = random.choice(hareketler)

    await ctx.send(
        f"⚔️ **KEDİ DÖVÜŞÜ BAŞLIYOR!**\n\n"
        f"🐱 {ctx.author.mention} vs 😼 {rakip.mention}\n\n"
        f"💥 {kazanan.mention} **{hareket}** kullandı!\n\n"
        f"🏆 **Kazanan: {kazanan.mention}!** 🎉\n"
        f"😿 {kaybeden.mention} yenildi ve köşeye çekildi..."
    )


# ── catimg ───────────────────────────────────────────────────────────────────
@bot.command()
async def catimg(ctx):
    """İnternetten rastgele bir kedi fotoğrafı."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.thecatapi.com/v1/images/search", timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    url = data[0]["url"]
                    embed = discord.Embed(title="🐱 Rastgele Kedi!", color=0xFF9900)
                    embed.set_image(url=url)
                    await ctx.send(embed=embed)
                    return
    except Exception:
        pass

    # API erişilemezse yedek
    yedek_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Cat_November_2010-1a.jpg/1200px-Cat_November_2010-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Kittyply_edit1.jpg/1200px-Kittyply_edit1.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Dog_Breeds.jpg/1200px-Dog_Breeds.jpg",
    ]
    embed = discord.Embed(title="🐱 Rastgele Kedi!", color=0xFF9900)
    embed.set_image(url=random.choice(yedek_urls))
    await ctx.send(embed=embed)


# ── benim kedim ──────────────────────────────────────────────────────────────
@bot.command(name="benim kedim")
async def benim_kedim(ctx):
    """Benim tatlı kedim! 🐱💕"""
    embed = discord.Embed(
        title="🐱💕 Benim Kedim!",
        description=(
            "İşte benim en tatlı kedim! 😻\n"
            "Çok tatlı değil mi?! Bakışlarına dayanmak imkânsız! 🥺✨\n\n"
            "🔗 [Pinterest'te gör](https://tr.pinterest.com/pin/886153664219557266/)"
        ),
        color=0xFF69B4,
        url="https://tr.pinterest.com/pin/886153664219557266/",
    )
    embed.set_image(url="https://i.pinimg.com/736x/cc/08/6e/cc086e0b3a2e1f4d8b7c9a0e2f3d1b5a.jpg")
    embed.set_footer(text="🐾 Dünyanın en tatlı kedisi — miyav! 💕")
    await ctx.send(embed=embed)


# ── flamingo ─────────────────────────────────────────────────────────────────
@bot.command()
async def flamingo(ctx):
    """Flamingo sürprizi — beklenmedik bir flamingo mesajı!"""
    mesajlar = [
        "🦩 FLAMINGO SALDIRISI! Neden burada bir flamingo var?!",
        "🦩 Flamingo seni izliyor... tek ayak üzerinde.",
        "🦩 Bu bir kedi botu ama flamingo da güzel hayvan.",
        "🦩 Pembe tüyler her yere saçıldı! Kaçın!",
        "🦩 Flamingo: 'Ben de komut istiyorum!' — Kedi: 'Hayır.'",
        "🦩 Beklenmedik flamingo dansı başladı! 💃",
        "🦩 Flamingo, kedinin en büyük rakibi. Bugün flamingo kazandı.",
        "🦩 Bir flamingo sunucuya girdi ve kimse fark etmedi.",
    ]
    await ctx.send(random.choice(mesajlar))


# ── help ─────────────────────────────────────────────────────────────────────
@bot.command(name="help")
async def yardim(ctx):
    """Tüm komutları listele."""
    embed = discord.Embed(
        title="🐱 Kedi Bot — Komut Listesi",
        description="Tüm komutlar `!` öneki ile kullanılır.",
        color=0xFF9900,
    )

    embed.add_field(
        name="🐾 Kedi Komutları",
        value=(
            "`!cat` — Miyav + rastgele komik kedi meme!\n"
            "`!miyav` — Miyav miyav!\n"
            "`!catfact` — Rastgele kedi bilgisi\n"
            "`!catimg` — Rastgele kedi fotoğrafı\n"
            "`!catfight @kullanıcı` — Kedi dövüşü\n"
            "`!randomcat` — Saçma kedi meme\n"
            "`!pet` — Kediyi sev\n"
            "`!benim kedim` — Benim tatlı kedim! 💕\n"
        ),
        inline=False,
    )
    embed.add_field(
        name="💰 Para Komutları",
        value=(
            "`!bakiye` / `!balance` — Bakiyeni gör\n"
            "`!daily` — Günlük para (24 saatte bir)\n"
            "`!work` — Çalış para kazan (saatte bir)\n"
            "`!gamble <miktar>` — Kumar oyna\n"
            "`!rob @kullanıcı` — Soy!\n"
            "`!leaderboard` — Zenginler sıralaması\n"
            "`!trivia` — Bilgi yarışması, para kazan\n"
        ),
        inline=False,
    )
    embed.add_field(
        name="🎉 Eğlence Komutları",
        value=(
            "`!8ball <soru>` — Kedi kehaneti\n"
            "`!mood` — Botun ruh hali\n"
            "`!ship @kullanıcı1 @kullanıcı2` — Uyum yüzdesi\n"
            "`!roast @kullanıcı` — Kedi değerlendirmesi\n"
            "`!flamingo` — Flamingo sürprizi\n"
            "`!no` — Hayır!\n"
            "`!uyarı` — Resmi kedi uyarısı\n"
        ),
        inline=False,
    )
    embed.set_footer(text="🐱 Kedi Bot — Miyav!")
    await ctx.send(embed=embed)


# ── mood ─────────────────────────────────────────────────────────────────────
@bot.command()
async def mood(ctx):
    """Botun bugünkü ruh halini öğren."""
    ruh_halleri = [
        ("😸 Mutlu", "Bugün her şey harika! Miyav!"),
        ("😼 Sinirli", "Beni rahatsız etme, uyumak istiyorum."),
        ("😺 Meraklı", "Bu düğmeye basarsam ne olur acaba..."),
        ("🙀 Şaşkın", "Neden bu kadar çok insan var burada?!"),
        ("😿 Hüzünlü", "Mama kabım boş. Hayat zor."),
        ("😾 Asabi", "Dokunma bana. Ciddi söylüyorum."),
        ("🐱 Sakin", "Her şey yolunda. Güneşte uzanıyorum."),
        ("😹 Neşeli", "Hahaha! Bir şey düştü ve ben ittirdim!"),
    ]
    ruh_hali, aciklama = random.choice(ruh_halleri)
    embed = discord.Embed(
        title=f"Botun Ruh Hali: {ruh_hali}",
        description=aciklama,
        color=0xFF9900,
    )
    await ctx.send(embed=embed)


# ── no ───────────────────────────────────────────────────────────────────────
@bot.command()
async def no(ctx):
    """Hayır!"""
    cevaplar = [
        "😾 HAYIR.",
        "🐱 Hayır, miyav.",
        "😼 Kesinlikle hayır.",
        "🙅 Hayır hayır hayır!",
        "😤 H-A-Y-I-R.",
        "🐾 Hayır. Son.",
        "😾 Hayır demek ne demek biliyor musun? İşte bu.",
    ]
    await ctx.send(random.choice(cevaplar))


# ── pet ──────────────────────────────────────────────────────────────────────
@bot.command()
async def pet(ctx):
    """Kediyi sev — belki karşılık verir."""
    cevaplar = [
        f"😸 {ctx.author.mention} seni seviyor! Mırıl mırıl...",
        f"😼 {ctx.author.mention} dokundu ama kedi kaçtı.",
        f"🐾 {ctx.author.mention} okşadı! Kedi gözlerini kıstı.",
        f"😺 {ctx.author.mention} sevdi! Kedi mutlu, mırıldıyor.",
        f"🙀 {ctx.author.mention} dokundu! Kedi şaşırdı ve ısırdı!",
        f"😾 {ctx.author.mention} yaklaştı ama kedi 'hayır' dedi.",
        f"🐱 {ctx.author.mention} okşadı! Kedi pençe attı ama sevgiyle.",
    ]
    await ctx.send(random.choice(cevaplar))


# ── randomcat ────────────────────────────────────────────────────────────────
@bot.command()
async def randomcat(ctx):
    """Tamamen saçma bir kedi meme."""
    memeler = [
        "🐱 *kedi klavyeye basar* `asdfghjkl` — Bu bir şiir.",
        "😸 Kedi: 'Beni besle.' Sen: 'Az önce besledim.' Kedi: 'Yalan.'",
        "🐾 Kedi saat 3'te koşmaya başladı. Neden? Bilinmiyor. Sorma.",
        "😼 Kedi bardağa bakıyor... bakıyor... itiyor. Tatmin oldu.",
        "🙀 Kedi kutunun içine girdi. Kutu küçük. Kedi umursamıyor.",
        "😺 Kedi: *bir şey düşürür* Ben: 'Neden?' Kedi: 'Çünkü yapabiliyorum.'",
        "🐱 Kedi yatağın tam ortasına yattı. Sen kenarda uyuyacaksın.",
        "😹 Kedi seni 3 saattir izliyor. Neden? Sır.",
        "😾 Kedi mama istiyor. Verdin. Yemedi. Şimdi ne yapacaksın?",
        "🐾 Kedi: *mırıldıyor* Sen: 'Mutlu musun?' Kedi: *pençe atar*",
    ]
    await ctx.send(random.choice(memeler))


# ── roast ────────────────────────────────────────────────────────────────────
@bot.command()
async def roast(ctx, hedef: discord.Member = None):
    """Kedi seni değerlendiriyor — acımasızca."""
    if hedef is None:
        hedef = ctx.author

    roastlar = [
        f"😼 {hedef.mention} — Kedi seni inceledi ve 'meh' dedi.",
        f"😾 {hedef.mention} — Kediye göre sen bir Pazartesi sabahısın.",
        f"🐱 {hedef.mention} — Kedi seni gördü ve uyumaya devam etti.",
        f"😼 {hedef.mention} — Kedi seni fare ile karıştırdı. Fare daha ilginçti.",
        f"🙀 {hedef.mention} — Kedi senden kaçtı. Bu çok şey söylüyor.",
        f"😹 {hedef.mention} — Kedi seni değerlendirdi: 2/10, tekrar dene.",
        f"😾 {hedef.mention} — Kedi seni gördü, kuyruk sallamadı. Bu kötü işaret.",
        f"🐾 {hedef.mention} — Kedi seni bir mobilya olarak sınıflandırdı.",
        f"😼 {hedef.mention} — Kedi sana baktı ve 'bu benim zamanıma değmez' dedi.",
    ]
    await ctx.send(random.choice(roastlar))


# ── ship ─────────────────────────────────────────────────────────────────────
@bot.command()
async def ship(ctx, kisi1: discord.Member = None, kisi2: discord.Member = None):
    """İki kullanıcı arasındaki uyumu ölç."""
    if kisi1 is None or kisi2 is None:
        await ctx.send("💕 İki kişi belirt! `!ship @kisi1 @kisi2`")
        return

    # Tutarlı sonuç için ID'leri kullan
    seed = (kisi1.id + kisi2.id) % 101
    oran = seed

    if oran >= 80:
        yorum = "💞 Mükemmel uyum! Kedi onayladı!"
        renk = 0xFF69B4
    elif oran >= 60:
        yorum = "💕 İyi uyum! Devam edin."
        renk = 0xFF9900
    elif oran >= 40:
        yorum = "💛 Fena değil, ama kedi şüpheli bakıyor."
        renk = 0xFFFF00
    elif oran >= 20:
        yorum = "💔 Pek uyumlu değilsiniz..."
        renk = 0xFF6600
    else:
        yorum = "😾 Kedi bu birlikteliği onaylamıyor."
        renk = 0xFF0000

    dolu = int(oran / 10)
    bos = 10 - dolu
    bar = "❤️" * dolu + "🖤" * bos

    embed = discord.Embed(title="💕 Uyum Testi", color=renk)
    embed.add_field(name="Çift", value=f"{kisi1.mention} & {kisi2.mention}", inline=False)
    embed.add_field(name="Uyum", value=f"{bar} **%{oran}**", inline=False)
    embed.add_field(name="Yorum", value=yorum, inline=False)
    await ctx.send(embed=embed)


# ── trivia ───────────────────────────────────────────────────────────────────
TRIVIA_SORULARI = [
    {
        "soru": "Kediler günde kaç saat uyur?",
        "cevap": ["12", "16", "12-16"],
        "ipucu": "10 ile 20 arasında bir sayı aralığı.",
        "odul": 30,
    },
    {
        "soru": "Kedilerin kaç kulak kası vardır?",
        "cevap": ["32"],
        "ipucu": "30'dan fazla.",
        "odul": 40,
    },
    {
        "soru": "Kediler hangi tadı alamaz?",
        "cevap": ["tatlı", "tatli", "şeker", "seker"],
        "ipucu": "Çocukların en sevdiği tat.",
        "odul": 35,
    },
    {
        "soru": "Bir kedinin iskeleti kaç kemikten oluşur?",
        "cevap": ["230"],
        "ipucu": "200'den fazla.",
        "odul": 50,
    },
    {
        "soru": "Kediler saatte kaç km koşabilir? (yaklaşık)",
        "cevap": ["48", "48 km"],
        "ipucu": "40 ile 50 arasında.",
        "odul": 45,
    },
    {
        "soru": "Kediler 'miyav' sesini kimlerle iletişim için çıkarır?",
        "cevap": ["insanlar", "insan", "insanlarla"],
        "ipucu": "Diğer kedilerle değil...",
        "odul": 25,
    },
]


@bot.command()
async def trivia(ctx):
    """Kedi bilgi yarışması — doğru cevapla para kazan!"""
    soru_data = random.choice(TRIVIA_SORULARI)

    embed = discord.Embed(
        title="🧠 Kedi Bilgi Yarışması",
        description=soru_data["soru"],
        color=0x00BFFF,
    )
    embed.add_field(name="💡 İpucu", value=soru_data["ipucu"], inline=False)
    embed.add_field(name="💰 Ödül", value=f"{soru_data['odul']} kedi parası", inline=False)
    embed.set_footer(text="30 saniye içinde cevapla!")
    await ctx.send(embed=embed)

    def kontrol(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        mesaj = await bot.wait_for("message", timeout=30.0, check=kontrol)
        verilen = mesaj.content.strip().lower()
        dogru_cevaplar = [c.lower() for c in soru_data["cevap"]]

        if verilen in dogru_cevaplar:
            user = get_balance(ctx.author.id)
            new_balance = user["para"] + soru_data["odul"]
            set_balance(ctx.author.id, new_balance, user["daily"], user["work"])
            await ctx.send(
                f"✅ **Doğru!** +{soru_data['odul']} kedi parası kazandın! "
                f"Toplam: **{new_balance}** 💰"
            )
        else:
            dogru = soru_data["cevap"][0]
            await ctx.send(f"❌ **Yanlış!** Doğru cevap: **{dogru}** 😿")
    except Exception:
        await ctx.send("⏰ Süre doldu! Cevap veremedin. 😿")


# ── uyarı ────────────────────────────────────────────────────────────────────
@bot.command(name="uyarı")
async def uyari(ctx, hedef: discord.Member = None):
    """Resmi kedi uyarısı ver."""
    if hedef is None:
        hedef = ctx.author

    uyarilar = [
        "miyav sesini çok yüksek çıkarmak",
        "kedi mamasını geç vermek",
        "kediyi uyurken rahatsız etmek",
        "kedi tüylerini temizlememek",
        "kediye 'köpek' demek",
        "kedi kutusunu paylaşmayı reddetmek",
        "kediyi yeterince övmemek",
        "kedi fotoğrafı çekmeden geçmek",
    ]

    embed = discord.Embed(
        title="⚠️ RESMİ KEDİ UYARISI ⚠️",
        description=f"{hedef.mention} resmi olarak uyarılmıştır.",
        color=0xFF0000,
    )
    embed.add_field(name="Suç", value=random.choice(uyarilar), inline=False)
    embed.add_field(name="Veren", value="🐱 Kedi Mahkemesi", inline=False)
    embed.add_field(name="Ceza", value="Bir hafta boyunca kedi fotoğrafı bakma yasağı.", inline=False)
    embed.set_footer(text="Bu uyarı kedi yasaları çerçevesinde verilmiştir.")
    await ctx.send(embed=embed)


# ── work ─────────────────────────────────────────────────────────────────────
@bot.command()
async def work(ctx):
    """Çalış para kazan — saatte bir kullanılabilir."""
    user = get_balance(ctx.author.id)
    now = datetime.now()

    if user["work"]:
        last_work = datetime.fromisoformat(user["work"])
        kalan = (last_work + timedelta(hours=1)) - now
        if kalan.total_seconds() > 0:
            dakika = int(kalan.total_seconds() // 60)
            saniye = int(kalan.total_seconds() % 60)
            await ctx.send(
                f"⏰ Çok yoruldun! **{dakika}dk {saniye}sn** sonra tekrar çalışabilirsin."
            )
            return

    isler = [
        ("🐟 Balık sattın", random.randint(10, 40)),
        ("🧶 Yumak sardın", random.randint(10, 40)),
        ("📦 Kedi maması taşıdın", random.randint(10, 40)),
        ("🖼️ Kedi portresi çizdin", random.randint(15, 50)),
        ("🎤 Kedi şarkısı söyledin", random.randint(10, 35)),
        ("🧹 Kedi tüyü süpürdün", random.randint(10, 30)),
        ("📸 Kedi fotoğrafı çektin", random.randint(15, 45)),
        ("🏠 Kedi oteli işlettin", random.randint(20, 60)),
    ]
    is_adi, kazanc = random.choice(isler)
    new_balance = user["para"] + kazanc
    set_balance(ctx.author.id, new_balance, user["daily"], now.isoformat())
    await ctx.send(
        f"{is_adi}! Kazandın: **{kazanc}** kedi parası 💰\n"
        f"Toplam bakiye: **{new_balance}**"
    )


# ── testeoji ─────────────────────────────────────────────────────────────────
@bot.command()
async def testeoji(ctx):
    """Test if the custom emoji reaction works."""
    emoji = bot.get_emoji(1498367793827942500)
    if emoji is None:
        await ctx.send(
            "❌ Emoji bulunamadı! (ID: 1498367793827942500) — "
            "Botun sunucuda olduğundan ve 'Use External Emojis' iznine sahip olduğundan emin ol."
        )
        return
    try:
        await ctx.message.add_reaction(emoji)
        await ctx.send(f"✅ Emoji reaksiyonu başarıyla eklendi: {emoji}")
    except discord.Forbidden:
        await ctx.send("❌ Hata: Botun 'Add Reactions' izni yok!")
    except discord.HTTPException as e:
        await ctx.send(f"❌ HTTP hatası: {e}")


# ── on_message (ALL CAPS auto-react) ─────────────────────────────────────────
CAPS_EMOJI_ID   = 1498367793827942500
CAPS_EMOJI_NAME = "buneamkhjsdhklsdkhds"
CAPS_THRESHOLD  = 0.80   # ≥80 % of letters must be uppercase


@bot.event
async def on_message(message: discord.Message):
    # Ignore messages from bots (including self)
    if message.author.bot:
        await bot.process_commands(message)
        return

    # Check for ALL CAPS: only consider alphabetic characters
    letters = [c for c in message.content if c.isalpha()]
    if len(letters) >= 3:
        upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        if upper_ratio >= CAPS_THRESHOLD:
            emoji = bot.get_emoji(CAPS_EMOJI_ID)
            if emoji is not None:
                try:
                    await message.add_reaction(emoji)
                except (discord.Forbidden, discord.HTTPException) as e:
                    print(f"[on_message] Emoji reaksiyonu eklenemedi: {e}")
            else:
                print(
                    f"[on_message] Emoji bulunamadı (ID: {CAPS_EMOJI_ID}). "
                    "Botun sunucuda olduğundan emin ol."
                )

    # Always process commands so other bot commands still work
    await bot.process_commands(message)


# TOKEN'İ ORTAM DEĞİŞKENİNDEN AL
# Railway kullanıcıları: Railway dashboard'unda servisinizin
# "Variables" sekmesine gidip DISCORD_TOKEN değişkenini
# Discord bot tokeninizle ayarlamanız gerekmektedir.
# Bkz: https://docs.railway.com/guides/variables
token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable is not set! "
        "If you are deploying on Railway, go to your service's "
        "'Variables' tab in the Railway dashboard and add "
        "DISCORD_TOKEN with your Discord bot token as the value. "
        "See: https://docs.railway.com/guides/variables"
    )

bot.run(token)
