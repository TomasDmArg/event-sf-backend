import base64
import binascii
import io

from PIL import Image, UnidentifiedImageError

ACCEPTED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_DECODED_BYTES = 2 * 1024 * 1024  # 2 MB
MAX_DIMENSION = 512
WEBP_QUALITY = 85


def decode_and_recompress(data_url: str) -> str:
    """
    Decode, verify, and re-compress an uploaded contact photo.

    Accepts a `data:image/{jpeg,png,webp,gif};base64,...` string. The declared
    MIME type is not trusted on its own: the bytes are decoded and verified with
    Pillow, rejecting anything that isn't genuinely a decodable image. On success
    the image is downscaled (if needed) and re-encoded as WebP, so the value
    actually stored is always `data:image/webp;base64,...` regardless of the
    upload format. Raises `ValueError` with a user-facing message on any
    rejection.
    """
    header, _, encoded = data_url.partition(",")
    if not header.startswith("data:") or ";base64" not in header or not encoded:
        raise ValueError("Photo must be a base64 data URL, e.g. data:image/png;base64,...")

    mime_type = header.removeprefix("data:").split(";", 1)[0]
    if mime_type not in ACCEPTED_MIME_TYPES:
        raise ValueError(f"Unsupported photo type {mime_type!r}; use JPEG, PNG, WebP, or GIF")

    try:
        raw = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Photo is not valid base64 data") from exc

    if len(raw) > MAX_DECODED_BYTES:
        raise ValueError(f"Photo exceeds the {MAX_DECODED_BYTES // (1024 * 1024)} MB size limit")

    try:
        Image.open(io.BytesIO(raw)).verify()
        image = Image.open(io.BytesIO(raw))  # verify() consumes the parser; reopen to use it
        image.load()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("Photo is not a valid, decodable image") from exc

    image = image.convert("RGBA" if image.mode in ("RGBA", "LA", "P") else "RGB")
    if max(image.size) > MAX_DIMENSION:
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))

    buffer = io.BytesIO()
    image.save(buffer, format="WEBP", quality=WEBP_QUALITY)
    recompressed = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/webp;base64,{recompressed}"
