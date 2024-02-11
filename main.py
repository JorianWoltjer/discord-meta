import asyncio
from hashlib import sha256
import json
import os
from threading import Thread
from urllib.parse import quote, unquote, urlparse, urlunparse
import discord
from discord.ext import commands
from discord import Message
import time
from flask import Flask, Response, abort, redirect, request, render_template
from jinja2 import Undefined
from dotenv import load_dotenv

intents = discord.Intents.default()

bot = commands.Bot('/', intents=intents)
app = Flask(__name__)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
RICKROLL = "https://discord.com/vanityurl/dotcom/steakpants/flour/flower/index11.html"
TIMEOUT = 7  # seconds


class SilentUndefined(Undefined):
    """Don't error when a jinja2 variable is undefined."""

    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''


app.jinja_env.undefined = SilentUndefined


# Discord

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


async def fetch(url):
    """Send URL in testing channel and fetch the embed Discord creates."""
    channel = bot.get_channel(CHANNEL_ID)
    message = await channel.send(url)
    if message.embeds:
        return message.embeds[0].to_dict()

    start_time = time.time()
    while True:
        if time.time() - start_time > TIMEOUT:
            break

        print("fetching...")
        message: Message = await channel.fetch_message(message.id)
        if message.embeds:
            return message.embeds[0].to_dict()

        await asyncio.sleep(1)


def fetch_from_flask(url):
    """Syncronous wrapper for fetch from other threads. Also caches the result."""
    hash = sha256(url.encode()).hexdigest()
    if os.path.exists(f'cache/{hash}.json'):
        with open(f'cache/{hash}.json') as f:
            return json.load(f)

    send_fut = asyncio.run_coroutine_threadsafe(fetch(url), bot.loop)
    embed = send_fut.result()

    with open(f'cache/{hash}.json', 'w') as f:
        json.dump(embed, f)

    return embed


# Flask

def quote_path(url):
    """Encode the path part of a URL.

    Reference: https://github.com/pallets/werkzeug/blob/68227737cbdb39663a6f203decd2bf869987ca80/src/werkzeug/urls.py#L757
    """
    parts = urlparse(url)
    return urlunparse(parts._replace(
        path=quote(parts.path, '/%'),
        query=quote(parts.query, ':&='),
    ))


@app.route('/')
def index():
    """Render the embed as HTML"""
    url = quote_path(unquote(request.query_string.decode()))
    if not url.startswith('http'):
        abort(400)

    if 'Discordbot' not in request.headers.get('User-Agent'):
        return redirect(RICKROLL)

    embed = fetch_from_flask(url)
    if not embed:
        abort(404)

    print(embed)
    return render_template('index.html', **embed, base=request.url_root)


@app.route("/oembed.json")
def oembed():
    """Utility to generate more complex oEmbed responses."""
    author = request.args.get('author')
    provider = request.args.get('provider')

    result = {}
    if author:
        result['author_name'] = author
        result['author_url'] = RICKROLL
    if provider:
        result['provider_name'] = provider
        result['provider_url'] = RICKROLL

    return result


@app.route("/gen")
def gen():
    """Generate a copy-pastable markdown link that spoofs the URL."""
    url = quote_path(unquote(request.query_string.decode()))
    if not url.startswith('http'):
        abort(400)

    url_text = "http" + "\ufff4" + url[4:]

    return Response(f"[{url_text}](<{RICKROLL}>) [\ufff4]({request.url_root}?{quote(url)})", mimetype="text/plain")


if __name__ == '__main__':
    t = Thread(target=app.run, args=(), kwargs={'host': "0.0.0.0"})
    t.start()

    bot.run(BOT_TOKEN)
