import base64
import io
from binascii import Error as BinError
from pathlib import Path

from asyncinit import asyncinit
from PIL import Image

from src.config import AVATAR_SIZES, AVATARS_DIR


@asyncinit
class Avatar:
    """Managing user avatars.
    """
    sizes: list[tuple[int, int]] = AVATAR_SIZES
    save_dir: str
    image: Path | None

    async def __init__(
        self, base64_data: bytes, user_id: str, avatars_dir: Path
    ) -> None:
        self.__set_save_dir(avatars_dir, user_id)
        self.image = await self.base64_to_image(base64_data)

    def __set_save_dir(self, avatars_dir: Path, user_id: str) -> None:
        """Set attr `self.save_dir`.

        #### Args:
          - user_id (str):
            A unique user ID to create a unique directory
            for saving user avatars.
        """
        self.save_dir = avatars_dir / user_id
        self.save_dir.mkdir(exist_ok=True)

    async def base64_to_image(self, base64_data: bytes) -> Path | None:
        """Convert and save binary data (`base64`) to an image(`png`).

        #### Args:
          - base64_data (bytes):
            The image is in the `base64` format.

        #### Returns:
          - Path | None:
            The path to the saved image or None if data is incorrect.
        """
        try:
            image = Image.open(io.BytesIO(base64.b64decode(base64_data)))
        except BinError:
            return

        image_name = self.save_dir / 'original.png'
        image.save(image_name)
        return image_name

    async def _save_resized_image(self, size: tuple[int, int]) -> None:
        """Resize the image and save it.

        #### Args:
          - size (tuple[int, int]):
            Size for the new image.
        """
        resized_image = Image.open(self.image)
        resized_image.thumbnail(size)
        image_name = self.save_dir / (str(size[0]) + '.png')
        resized_image.save(image_name)

    async def save_resized_avatars(self) -> None:
        """Save the image with different sizes.
        """
        for size in self.sizes:
            await self._save_resized_image(size)


def get_avatars_root() -> Path:
    """Returns the path to the avatars directory to use depending on.

    Returns:
      - Path:
        The path to the avatars directory.
    """
    return AVATARS_DIR
