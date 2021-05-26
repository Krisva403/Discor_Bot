from quart import Quart, render_template, request, session, redirect, url_for
from quart_discord import DiscordOAuth2Session
from discord.ext import ipc

app = Quart(__name__)
ipc_client = ipc.Client(secret_key="bot")

app.config["SECRET_KEY"] = "test123"
app.config["DISCORD_CLIENT_ID"] = "821014425015943178"
app.config["DISCORD_CLIENT_SECRET"] = "r-i6hOKtso5ZnPOznYd0hD3JflASvfY8"
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"

discord = DiscordOAuth2Session(app)


# Render the login site
@app.route("/")
async def home():
    return await render_template("index.html")


# logins through discord api
@app.route("/login")
async def login():
    return await discord.create_session()


# Callback to login screen or go to dashboard
@app.route("/callback")
async def callback():
    try:
        await discord.callback()
    except Exception:
        pass

    return redirect(url_for("dashboard"))


# Dashboard with all channels the user has admin on and if the bot is active on any of the channels
@app.route("/dashboard")
async def dashboard():
    if not await discord.authorized:
        return redirect(url_for("login"))

    guild_count = await ipc_client.request("get_guild_count")  # How many of the channels the bot is on
    guild_ids = await ipc_client.request("get_guild_ids")  # Requests the channel ids

    user_guilds = await discord.fetch_guilds()

    guilds = []

    for guild in user_guilds:
        if guild.permissions.administrator:
            guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
            guilds.append(guild)

    guilds.sort(key=lambda x: x.class_color == "red-border")
    name = (await discord.fetch_user()).name
    return await render_template("dashboard.html", guild_count=guild_count, guilds=guilds, username=name)


# Opens a new session for every channel
@app.route("/dashboard/<int:guild_id>")
async def dashboard_server(guild_id):
    if not await discord.authorized:
        return redirect(url_for("login"))

    guild = await ipc_client.request("get_guild", guild_id=guild_id)

    if guild is not None:
        return await render_template("guild.html", guild_name=guild["name"])
    else:
        return redirect(
            f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')
    return guild["name"]


if __name__ == "__main__":
    app.run(debug=True)
