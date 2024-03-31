# Discord Embed Rick Roller

[discord.jtw.sh/gen](https://discord.jtw.sh/gen)

Generate a perfect rickroll link with a realistic embed in Discord. Use the site above to paste a target URL, then copy the generated text it gives you by pressing <kbd>Ctrl+A</kbd> & <kbd>Ctrl+C</kbd>. 

This works by sending and copying a real embed from the link and generating an [oEmbed](https://oembed.com/) configuration that redirects the link to a rickroll. Then with some clever discord formatting, you can mask the original link to fool even your most attentive friends.

## Example

Fake             |  Real
:-------------------------:|:-------------------------:
![image](https://github.com/JorianWoltjer/discord-meta/assets/26067369/e721a3de-083b-4d60-aa8c-81e96e93c991)  |  ![image](https://github.com/JorianWoltjer/discord-meta/assets/26067369/e4124e4b-5738-4520-a8d5-ee757f9275f8)

Clicking on either the **link itself**, the **white title** or even the **organization name** will instantly open [Rick Astley - Never Gonna Give You Up](https://www.youtube.com/watch?v=dQw4w9WgXcQ) without any confirmation!

## Technical Details

You might be curious how this works. It turns out to be a combination of a few different tricks in Discord that cleverly combine into an almost undetectable rickroll. 

1. Using "masked links" like `[example](https://example.com)` to put a different link behind some text.
2. While you cannot put another URL as the front for this masked link, you can get the same effect using the Unicode unmapped [`\ufff4`](https://unicode-explorer.com/c/FFF4) character. This is an invisible character that we can insert into the URL protocol to fool Discord into thinking it is not really a URL, while it still looks like one to the user, like: `[http\ufff4s://fake.com](https://example.com)`.
3. Adding a custom embed to the URL without seeing the source of the embed in the message as a link using another masked link only containing `\ufff4` as the text, like: `[\ufff4](https://example.com)`.
4. Using some `<meta>` [Open Graph](https://ogp.me/) tags to respond with the correct embed information, excluding the title.
5. Using `<link type="application/json+oembed" href=...>` to my own page responding with a custom title and and URL behind it to a rickroll.
6. Redirecting to https://discord.com/vanityurl/dotcom/steakpants/flour/flower/index11.html which is an easter egg on the discord.com domain that redirects to a rickroll. This way, no confirmation is given to the user because discord.com is a trusted domain.

When a URL is given to the website, it will send that same URL to a real Discord channel and wait for Discord to fetch and embed the content. When it does, this is read by the bot and parsed to replicate all fields. Using the tricks above the clickable parts are transformed into rickrolls and a string is generated that you can copy-paste into Discord. 

Check out the code for all the details.

## Privacy

> [!WARNING]  
> As I host [discord.jtw.sh/gen](https://discord.jtw.sh/gen) myself, I will receive every URL you paste into the generator. Make sure you are OK with sharing this, or otherwise, host it yourself by cloning and running this repository.
