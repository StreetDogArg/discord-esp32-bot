import os, requests, discord

DISCORD_TOKEN   = os.getenv("DISCORD_TOKEN")
MY_USER_ID      = int(os.getenv("MY_USER_ID"))
ESP32_URL_GET   = os.getenv("ESP32_URL_GET")
ESP32_URL_POST  = os.getenv("ESP32_URL_POST")

# ⚙️ Configuración opcional
SEND_DM_ON_FAIL = True   # Cambia a False si no querés recibir DMs al fallar
SEND_MSG_IN_CHANNEL = False  # Cambia a True si querés que también avise en el canal

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True  # necesario para enviar DMs

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
                error_log = ""

                # 🚀 Intento GET al ESP32
                try:
                    r = requests.get(ESP32_URL_GET, timeout=4)
                    ok_get = (r.status_code == 200)
                except Exception as e:
                    error_log += f"GET: {e}\n"

                # 🚀 Intento POST al ESP32 con datos
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
                    error_log += f"POST: {e}\n"

                # 🚀 Si funcionó → solo reacción 🤖
                if ok_get or ok_post:
                    await message.add_reaction("🤖")
                    if SEND_MSG_IN_CHANNEL:
                        await message.channel.send("📡 Notificación enviada al ESP32 ✅")
                else:
                    print("⚠️ Error al contactar al ESP32")
                    if SEND_DM_ON_FAIL:
                        try:
                            user = await client.fetch_user(MY_USER_ID)
                            jump_url = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
                            dm_msg = (
                                f"⚠️ No pude contactar al ESP32.\n\n"
                                f"📢 Te mencionaron en **{message.guild}** / **#{message.channel}**\n"
                                f"👤 De: {message.author}\n"
                                f"💬 Mensaje: \"{message.content}\"\n"
                                f"🔗 [Abrir mensaje en Discord]({jump_url})\n\n"
                                f"Error: {error_log or 'Sin detalles adicionales.'}"
                            )
                            await user.send(dm_msg)
                            print("📩 Enviado DM de aviso.")
                        except Exception as e:
                            print("❌ No se pudo enviar DM:", e)

client.run(DISCORD_TOKEN)
