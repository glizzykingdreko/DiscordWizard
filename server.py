import asyncio, websockets, discord, logging, aiohttp
from discord.ext import commands
from yaml import load, Loader
from json import load as j_load, dump as j_dump, loads
from resilient_caller import resilient_call, update_session_proxy 
from random import choice

# Define logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Disable logging for discord
discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.WARNING)

# Load settings
settings = load(open("settings.yaml", "r"), Loader=Loader)
TOKEN = settings["server"]['token']
SERVER_ID = settings["server"]['server_id']
INTERVAL = settings["server"]['interval']
WEBHOOK_NAME = settings["server"]['webhook_name']
PORT, HOST = list(settings['server']['websocket'].values())
PROXIES = open("proxies.txt", "r").read().splitlines()
bot = commands.Bot(command_prefix='>', self_bot=True)

@resilient_call()
async def send_webhook_to_discord(webhook_url: str, webhook_data: dict):
    # Send async request to discord webhook
    async with aiohttp.ClientSession() as session:
        if len(PROXIES) > 0:
            update_session_proxy(session, choice(PROXIES))
        async with session.post(webhook_url, json=webhook_data) as response:
            return await response.text()

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")

async def update_server_structure(sitemap: dict, sitemap_file: str):
    server = bot.get_guild(SERVER_ID)
    if server is None:
        return
    try:
        with open(sitemap_file, "r") as infile:
            updated_sitemap = j_load(infile)
    except FileNotFoundError:
        updated_sitemap = {"categories": [], "standalone_channels": []}
    if updated_sitemap == sitemap:
        return
    for cat_data in sitemap["categories"]:
        category = discord.utils.get(server.categories, name=cat_data["name"])
        if category is None:
            category = await server.create_category(cat_data["name"])
            logging.info(f"Category created: {cat_data['name']}")
        await asyncio.sleep(INTERVAL)
        updated_channels = []
        for channel_data in cat_data["channels"]:
            channel = discord.utils.get(category.channels, name=channel_data["name"])
            if channel is None:
                channel = await server.create_text_channel(channel_data["name"], category=category)
                webhook = await channel.create_webhook(name=WEBHOOK_NAME)
                updated_channels.append({"name": channel.name, "id": channel.id, "webhook": webhook.url})
                logging.info(f"Channel created: {channel_data['name']} in category {cat_data['name']}")
                await asyncio.sleep(INTERVAL)
            else:
                webhook = None
                webhooks = await channel.webhooks()
                for hook in webhooks:
                    if hook.name == WEBHOOK_NAME:
                        webhook = hook
                        break
                if webhook is None:
                    webhook = await channel.create_webhook(name=WEBHOOK_NAME)
                updated_channels.append({"name": channel.name, "id": channel.id, "webhook": webhook.url})
                logging.debug(f"Channel already exists: {channel_data['name']} in category {cat_data['name']}")
            await asyncio.sleep(INTERVAL)
        updated_sitemap["categories"].append({"name": category.name, "channels": updated_channels})
        await save_sitemap_to_file(updated_sitemap, sitemap_file)
    for channel_data in sitemap["standalone_channels"]:
        channel = discord.utils.get(server.text_channels, name=channel_data["name"], category=None)
        if channel is None:
            channel = await server.create_text_channel(channel_data["name"])
            webhook = await channel.create_webhook(name=WEBHOOK_NAME)
            updated_sitemap["standalone_channels"].append({"name": channel.name, "id": channel.id, "webhook": webhook.url})
            logging.info(f"Standalone channel created: {channel_data['name']}")
            await asyncio.sleep(INTERVAL)
        else:
            webhook = None
            webhooks = await channel.webhooks()
            for hook in webhooks:
                if hook.name == WEBHOOK_NAME:
                    webhook = hook
                    break
            if webhook is None:
                webhook = await channel.create_webhook(name=WEBHOOK_NAME)
            updated_sitemap["standalone_channels"].append({"name": channel.name, "id": channel.id, "webhook": webhook.url})
            logging.debug(f"Standalone channel already exists: {channel_data['name']}")
        await save_sitemap_to_file(updated_sitemap, sitemap_file)
        await asyncio.sleep(INTERVAL)

    return updated_sitemap

async def save_sitemap_to_file(sitemap, filename="final.json"):
    with open(filename, "w") as outfile:
        j_dump(sitemap, outfile, indent=4)

def compare_sitemaps(old_sitemap, new_sitemap):
    removed_channels = []
    title_changes = []

    # Compare category channels
    for old_cat in old_sitemap["categories"]:
        new_cat = next((cat for cat in new_sitemap["categories"] if cat["name"] == old_cat["name"]), None)
        if new_cat is None:
            removed_channels.extend(old_cat["channels"])
        else:
            for old_channel in old_cat["channels"]:
                new_channel = next((chan for chan in new_cat["channels"] if chan["id"] == old_channel["id"]), None)
                if new_channel is None:
                    removed_channels.append(old_channel)
                elif new_channel["name"] != old_channel["name"]:
                    title_changes.append({"type": "channel", "old": old_channel, "new": new_channel})

            # Check for category title changes
            if old_cat["name"] != new_cat["name"]:
                title_changes.append({"type": "category", "old": old_cat, "new": new_cat})

    # Compare standalone channels
    for old_channel in old_sitemap["standalone_channels"]:
        new_channel = next((chan for chan in new_sitemap["standalone_channels"] if chan["id"] == old_channel["id"]), None)
        if new_channel is None:
            removed_channels.append(old_channel)
        elif new_channel["name"] != old_channel["name"]:
            title_changes.append({"type": "channel", "old": old_channel, "new": new_channel})

    return removed_channels, title_changes

async def websocket_handler(websocket, path):
    sitemap_file = "final.json"
    try:
        with open(sitemap_file, "r") as infile:
            old_sitemap = j_load(infile)
    except FileNotFoundError:
        old_sitemap = None

    async for message in websocket:
        data = loads(message)
        if data["type"] == "sitemap":
            logging.info("Sitemap received")
            updated_sitemap = await update_server_structure(data["data"], sitemap_file)
            if updated_sitemap is not None:
                await save_sitemap_to_file(updated_sitemap, sitemap_file)

            if old_sitemap is not None:
                removed_channels, title_changes = compare_sitemaps(old_sitemap, updated_sitemap)
                if removed_channels:
                    logging.info("Removed channels:", removed_channels)
                if title_changes:
                    logging.info("Title changes:", title_changes)
                if not removed_channels and not title_changes:
                    logging.info("Nothing changed")

            old_sitemap = updated_sitemap
        elif data["type"] == "ping":
            logging.info("Ping received")
        elif data["type"] == "message":
            logging.info("New message received")
            webhook = None
            sitemap = loads(open(sitemap_file, "r").read())
            for ncat, cat in enumerate(sitemap["categories"]):
                for channel in cat["channels"]:
                    if channel["name"] == data["channel_name"]:
                        if channel.get("webhook") is None:
                            webhooks = await channel.webhooks()
                            for hook in webhooks:
                                if hook.name == WEBHOOK_NAME:
                                    webhook = hook
                                    break
                            if webhook is None:
                                webhook = await channel.create_webhook(name=WEBHOOK_NAME)
                            webhook = webhook.url
                            sitemap["categories"][ncat]["channels"][channel]["webhook"] = webhook
                            await save_sitemap_to_file(sitemap, sitemap_file)
                        else:
                            webhook = channel["webhook"] 
                        break
            if webhook is None:
                for channel in sitemap["standalone_channels"]:
                    if channel["name"] == data["channel_name"]:
                        if channel.get("webhook") is None:
                            webhooks = await channel.webhooks()
                            for hook in webhooks:
                                if hook.name == WEBHOOK_NAME:
                                    webhook = hook
                                    break
                            if webhook is None:
                                webhook = await channel.create_webhook(name=WEBHOOK_NAME)
                            webhook = webhook.url
                            sitemap["standalone_channels"][channel]["webhook"] = webhook
                            await save_sitemap_to_file(sitemap, sitemap_file)
                        else:
                            webhook = channel["webhook"]
                        break
            if webhook is not None: 
                res = await send_webhook_to_discord(
                    webhook,
                    data["content"]
                )
                logging.info(f"Message sent to discord: {res}")
            else:
                logging.warning(f"Message received for unknown channel: {data['channel_id']}")
        else:
            logging.warning(f"Unknown message type received from websocket: {data['type']}")

start_server = websockets.serve(websocket_handler, HOST, PORT)
bot.loop.run_until_complete(start_server)
bot.run(TOKEN)
