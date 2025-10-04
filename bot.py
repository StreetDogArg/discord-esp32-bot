import os, requests, discord

DISCORD_TOKEN   = os.getenv("DISCORD_TOKEN")   # token del bot
MY_USER_ID      = int(os.getenv("MY_USER_ID")) # tu User ID
ESP32_URL_GET   = os.getenv("ESP32_URL_GET")   # ej: http://IP_PUBLICA:8888/notify?auth=1234
ESP32_URL_POST  = os.getenv("ESP32_URL_POST")  # ej: http://IP_PUBLICA:8888/data?auth=1234

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.mentions:
        for u in message.mentions:
            if u.id == MY_USER_ID:
                print(f"📢 Te mencionaron en {message.guild} / #{message.channel}")

                ok_get, ok_post = False, False

                # 🚀 GET simple al ESP32
                try:
                    r = requests.get(ESP32_URL_GET, timeout=4)
                    ok_get = (r.status_code == 200)
                except Exception as e:
                    print("❌ Error en GET:", e)

                # 🚀 POST con datos detallados
                try:
                    payload = {
                        "server": str(message.guild),
                        "user": str(message.author),
                        "channel": str(message.channel),
                        "msg": message.content
                    }
                    r = requests.post(ESP32_URL_POST, json=payload, timeout=5)
                    ok_post = (r.status_code == 200)
                except Exception as e:
                    print("❌ Error en POST:", e)

                # 🚀 Feedback en Discord
                if ok_get or ok_post:
                    await message.add_reaction("🤖")
                    await message.channel.send("📡 Notificación enviada al ESP32 ✅")
                else:
                    await message.channel.send("⚠️ Error al notificar al ESP32")

client.run(DISCORD_TOKEN)
