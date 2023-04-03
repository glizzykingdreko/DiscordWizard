import websockets, discord, re, logging
from time import sleep
from discord.ext import commands, tasks
from yaml import load, Loader
from json import dumps
from os import _exit
from resilient_caller import resilient_call, RETRY_EVENT

# Define logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Disable logging for discord
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.WARNING)

# Load settings
settings = load(open("settings.yaml", "r"), Loader=Loader)
TOKEN = settings["client"]['token']
SERVER_ID = settings["client"]['server_id']
REGEX_FILTER = re.compile(settings["client"]['regex_filter'])
EXCLUDED_CHANNELS = settings["client"]['excluded_channels']
port, host = list(settings['server']['websocket'].values())
WEBSOCKET_URI = f"ws://{host}:{port}"
bot = commands.Bot(command_prefix='>', self_bot=True)

# Handle connection errors
def on_exception(exception, tries):
    logging.error(f"Exception connecting: {type(exception).__name__}: {str(exception)}")
    if tries > 2:
        logging.error("Too many retries. Aborting...")
        _exit(0)
    sleep(15)
    return RETRY_EVENT

EXCEPTION_HANDLE = {
    "all": on_exception,
}
ON_RETRY = lambda tries: logging.info(f"({tries}) Retrying connection...")

@resilient_call()
async def send_message_to_websocket(message):
    async with websockets.connect(WEBSOCKET_URI) as websocket:
        # Parse into webhook
        logging.info(f"New message detected - {message.channel.name}")
        hooks_data = []
        try:
            # Format message / embed as webhook
            username, avatar_url = None if not message.author else str(message.author).replace("#0000", ""), str(message.author.avatar_url)
            hooks_data.append({
                "content": None if not message.content else message.content, 
                "username": username,
                "avatar_url": avatar_url,
                "embeds": [{
                    "title": None if not embed.title else embed.title, 
                    "url": None if not embed.url else embed.url,
                    "description": None if not embed.description else embed.description, 
                    "color": None if not embed.color else embed.color.value,
                    "author": None if not embed.author else {"name": embed.author.name, "url": None if not embed.footer.icon_url else embed.footer.icon_url, "icon_url": None if not embed.footer.icon_url else embed.footer.icon_url},
                    "thumbnail": None if not embed.thumbnail else {"url": embed.thumbnail.url},
                    "fields": [{"name": fld.name, "value": fld.value, "inline": fld.inline} for fld in embed.fields],
                    "image": None if not embed.image else {"url": embed.image.url},
                    "footer": None if not embed.footer else {"text": embed.footer.text, "icon_url": None if not embed.footer.icon_url else embed.footer.icon_url},
                    "timestamp": None if not embed.timestamp else str(embed.timestamp)
                } for embed in message.embeds]
            }) 

            # Send any other type of file as link in a different webhook
            for attach in message.attachments: hooks_data.append({"username": username, "avatar_url": avatar_url, "content": attach.url})
        except Exception as e:
            # Unexcepted error parsing message. Will probably never happen
            logging.warning(f"Unable to load message ({type(e).__name__}: {str(e)})")
            return
        
        # Check and remove for empty ones just in case
        good_hooks = [hook for hook in hooks_data if hook['content'] or len(hook['embeds']) > 0] 
        
        # Send webhook
        for n, hook_data in enumerate(good_hooks, 1):
            logging.info(f"({n}/{len(good_hooks)}) Sending message to server...")
            await websocket.send(dumps({"type": "message", "channel_name": message.channel.name, "content": hook_data}))
        
@resilient_call()    
async def send_sitemap_to_websocket(sitemap: dict):
    async with websockets.connect(WEBSOCKET_URI) as websocket:
        await websocket.send(dumps({"type": "sitemap", "data": sitemap}))

async def get_server_sitemap(server_id: int):
    server = bot.get_guild(server_id)
    if server is None:
        return
    sitemap = {"categories": [], "standalone_channels": []}
    for category in server.categories:
        cat_data = {"name": category.name, "channels": []}
        for channel in category.channels:
            if isinstance(channel, discord.TextChannel):
                cat_data["channels"].append({"name": channel.name, "id": channel.id})
        sitemap["categories"].append(cat_data)
    for channel in server.channels:
        if isinstance(channel, discord.TextChannel) and channel.category is None:
            sitemap["standalone_channels"].append({"name": channel.name, "id": channel.id})
    # Debugging purposes
    open("sitemap.json", "w").write(dumps(sitemap, indent=4))
    return sitemap

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name}")
    send_sitemap.start()

@bot.event
async def on_message(message):
    if message.guild.id == SERVER_ID and message.channel.id not in EXCLUDED_CHANNELS:
        if not REGEX_FILTER.search(message.content):
            await send_message_to_websocket(message, exceptions=EXCEPTION_HANDLE, on_retry=ON_RETRY)

def generate_sitemap(server: discord.Guild) -> dict:
    categories = []
    standalone_channels = []

    for category in server.categories:
        channels = [{"name": channel.name, "id": channel.id} for channel in category.channels if isinstance(channel, discord.TextChannel)]
        categories.append({"name": category.name, "channels": channels})

    for channel in server.text_channels:
        if channel.category is None:
            standalone_channels.append({"name": channel.name, "id": channel.id})

    return {"categories": categories, "standalone_channels": standalone_channels}

@tasks.loop(minutes=5)
async def send_sitemap():
    server = bot.get_guild(SERVER_ID)
    if server:
        logging.info("Sending sitemap")
        sitemap = generate_sitemap(server)
        await send_sitemap_to_websocket(sitemap, exceptions=EXCEPTION_HANDLE, on_retry=ON_RETRY)

@send_sitemap.before_loop
async def before_send_sitemap():
    await bot.wait_until_ready()

bot.run(TOKEN)