import imghdr
from pathlib import Path

from PIL import Image

from src.core.services import Avatar
from tests.conftest import BIG_B64_IMAGE


async def test_avatar(temp_dirs: Path):
    with open(BIG_B64_IMAGE, 'rb') as f:
        original = f.read()

    user_id = '99'
    avatar = await Avatar(
        base64_data=original,
        user_id=user_id,
        avatars_dir=temp_dirs
    )
    assert imghdr.what(avatar.image) == 'png'

    user_avatars_dir = temp_dirs / user_id
    original_image = user_avatars_dir / 'original.png'
    assert original_image.exists()

    await avatar.save_resized_avatars()
    avatars = (
        img for img in user_avatars_dir.iterdir() if img.name != 'original.png'
    )
    sizes = set(avatar.sizes.copy())

    for image in avatars:
        size = Image.open(image).size
        sizes.remove(size)

    assert not sizes
