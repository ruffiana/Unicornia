import io
from pathlib import Path
import discord
import requests


class Embed:
    CACHE_DIR = Path("image_cache")

    # @classmethod
    # def create(
    #     cls,
    #     title=None,
    #     description=None,
    #     color=const.EMBED_COLOR,
    #     image=None,
    #     thumnail=None,
    #     authors=None,
    #     credits=None,
    #     spoiler=False,
    # ):
    #     embed = discord.Embed()

    #     if authors:
    #         if isinstance(authors, list):
    #             authors = ", ".join(authors)
    #         embed.set_author(authors)

    #     footer = const.EMBED_FOOTER
    #     if action.credits:
    #         footer = f'{footer}\ncredits: {", ".join(action.credits)}'
    #     self.logger.debug(f"footer : {footer}")

    #     return embed

    @classmethod
    def get_image(cls, url: str) -> Path:
        cache_path = cls.CACHE_DIR / Path(url).name

        if cache_path.exists():
            return cache_path

        try:
            response = requests.get(url)
        # put this here to resolve SSLError(SSLCertVerificationError with images on
        # https://panel.unicornia.net
        except:
            response = requests.get(url, verify=False)

        if response.status_code == 200:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, "wb") as file:
                file.write(response.content)
            return cache_path
        else:
            raise Exception(f"Failed to download image: {url}")

    @classmethod
    def spoiler_image(
        cls, url: str, embed: discord.Embed
    ) -> tuple[discord.Embed, discord.File]:
        image_path = cls.get_image(url)
        file_extension = image_path.suffix

        with image_path.open("rb") as file:
            file_content = file.read()

        file = discord.File(
            io.BytesIO(file_content),
            filename=f"SPOILER_image{file_extension}",
            spoiler=True,
        )
        # embed.set_image(url=f"attachment://SPOILER_image{file_extension}")
        return embed, file


if __name__ == "__main__":
    # Example usage
    image_url = "https://cdn.weeb.sh/images/rJaog0FtZ.gif"
    cached_image_path = Embed.get_image(image_url)
    print(f"Cached image path: {cached_image_path}")
