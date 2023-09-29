import discord
import os
import time
import aiohttp, io
import asyncio
import datetime


class COLORS:
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


class DIRS:
    BASE = "./"
    LOGGING = f"{BASE}/logging_files"
    PY = f"{BASE}/py_files"
    JSON = f"{BASE}/json_files"
    WAVELINK = f"{BASE}/wavelink_files"


class actions:
    @classmethod
    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear"), print(COLORS.RESET, end="")

    @classmethod
    def _sleep(self, x: int | float | None = 0) -> None:
        time.sleep(x)

    @classmethod
    async def sleep(self, x: int | float | None = 0) -> None:
        asyncio.sleep(x)

    @classmethod
    async def request_http(
        self, link: str | None = None, client: aiohttp.ClientSession | None = None
    ) -> aiohttp.ClientResponse | str:
        if not client or not link:
            return None
        async with client.get(link) as resp:
            if resp.status != 200:
                return None
            return io.BytesIO(await resp.read())


class craft:
    @classmethod
    def activity(self, properties: dict | None = None) -> discord.Activity | None:
        if properties == None:
            raise TypeError("dict not provided")

        match (properties["type"]):
            case "Playing":
                activity = discord.Game(
                    name=properties["name"]
                    if properties["name"] is not None
                    else "something",
                )

            case "Streaming":
                activity = discord.Streaming(
                    name=properties["name"]
                    if properties["name"] is not None
                    else "something",
                    url=properties["url"]
                    if properties["url"] is not None
                    else "https://www.twitch.tv/thelivingpepsi",
                )

            case "Listening" | "Watching" | "Competing":
                activity = discord.Activity(
                    type=discord.ActivityType.competing
                    if properties["type"] == "Competing"
                    else discord.ActivityType.listening
                    if properties["type"] == "Listening"
                    else discord.ActivityType.watching,
                    name=properties["name"]
                    if properties["name"] is not None
                    else "something",
                )

            case _:
                raise ValueError("A key or value was not valid.")

        return activity

    @classmethod
    def mentions(
        self, properties: dict | None = None
    ) -> discord.AllowedMentions | None:
        if properties == None:
            raise TypeError("dict not provided")

        allowed_mentions = discord.AllowedMentions(
            everyone=properties["everyone"],
            users=properties["users"],
            roles=properties["roles"],
            replied_user=properties["replied_user"],
        )

        return allowed_mentions

    @classmethod
    async def _file(self, properties: dict | None = None) -> discord.File | None:
        if properties == None:
            raise TypeError("dict not provided")

        if properties["is_url"]:
            data = await self.file_from_url(properties["path"])
        else:
            with open(properties["path"], "rb") as fp:
                data = fp

        if data == None:
            return None

        d_file = discord.File(data, properties["filename"])

        return d_file

    @classmethod
    async def files(self, files: list | None = None) -> list | None:
        return [await self.file(d_file) for d_file in files]

    @classmethod
    async def file_from_url(
        self, url: str, client: aiohttp.ClientSession
    ) -> discord.File | None:
        if url and client and (fp := await actions.request_http(url, client)):
            return discord.File(fp, "image.png")
        return None

    @classmethod
    def formatted_time(self, seconds: int | float | None = None) -> str:
        if not seconds:
            return "0"

        (hours, seconds) = divmod(seconds, 3600)
        (minutes, seconds) = divmod(seconds, 60)

        hour = f"{hours:02d}:" if hours > 0 else ""
        timestamp = f"{minutes:02d}:{seconds:02d}"

        formatted = f"{hour}{timestamp}"

        return formatted

    @classmethod
    def embed(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
        timestamp: datetime.datetime | int | None = None,
        color: discord.Color | int | tuple | list | None = None,
        footer: dict | None = None,
        image: str | None = None,
        thumbnail: str | None = None,
        author: dict | None = None,
        fields: dict | None = None,
    ):
        new_embed = discord.Embed(
            color=color,
            title=title,
            url=url,
            description=description,
            timestamp=timestamp,
        )

        if author:
            new_embed = new_embed.set_author(
                name=author["name"], url=author["url"], icon_url=author["icon_url"]
            )

        if footer:
            new_embed = new_embed.set_footer(
                text=footer["text"], icon_url=footer["icon_url"]
            )

        if image:
            new_embed = new_embed.set_image(url=image)

        if thumbnail:
            new_embed = new_embed.set_thumbnail(url=thumbnail)

        if fields:
            for field in fields:
                if field["index"]:
                    new_embed = new_embed.insert_field_at(
                        index=field["index"],
                        name=field["name"],
                        value=field["value"],
                        inline=field["inline"],
                    )
                    continue

                new_embed = new_embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field["inline"],
                )

        return new_embed
