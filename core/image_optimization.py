from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps


@dataclass(frozen=True)
class OptimizeResult:
    path: Path
    changed: bool
    skipped: bool
    reason: str
    old_bytes: int = 0
    new_bytes: int = 0
    old_size: tuple[int, int] | None = None
    new_size: tuple[int, int] | None = None


_EXT_TO_FORMAT: dict[str, str] = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}


def _resize_to_max_dim(img: Image.Image, max_dim: int) -> Image.Image:
    width, height = img.size
    largest = max(width, height)
    if largest <= max_dim:
        return img
    scale = max_dim / float(largest)
    new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return img.resize(new_size, Image.Resampling.LANCZOS)


def encode_optimized_image_bytes(
    path: Path,
    *,
    max_dim: int,
    jpeg_quality: int,
    webp_quality: int,
    png_compress_level: int,
) -> tuple[bytes, tuple[int, int], tuple[int, int], bool]:
    ext = path.suffix.lower()
    out_format = _EXT_TO_FORMAT.get(ext)
    if not out_format:
        raise ValueError(f"Unsupported extension: {ext}")

    with Image.open(path) as img_in:
        img = ImageOps.exif_transpose(img_in)
        old_size = img.size
        if max_dim:
            img_resized = _resize_to_max_dim(img, max_dim)
        else:
            img_resized = img
        resized = img_resized.size != img.size
        img = img_resized

        # Drop fully-opaque alpha to improve encodes (esp. PNG).
        if "A" in img.getbands():
            try:
                alpha = img.getchannel("A")
                if alpha.getextrema() == (255, 255):
                    img = img.convert("RGB")
            except Exception:
                pass

        save_kwargs: dict[str, object] = {}
        if out_format == "JPEG":
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            save_kwargs.update(
                quality=int(jpeg_quality),
                optimize=True,
                progressive=True,
            )
        elif out_format == "PNG":
            if img.mode == "P":
                img = img.convert("RGBA")
            save_kwargs.update(
                optimize=True,
                compress_level=int(png_compress_level),
            )
        elif out_format == "WEBP":
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            save_kwargs.update(
                quality=int(webp_quality),
                method=6,
            )

        buf = BytesIO()
        img.save(buf, format=out_format, **save_kwargs)
        return buf.getvalue(), old_size, img.size, resized


def optimize_image_file(
    path: Path,
    *,
    max_dim: int = 1080,
    jpeg_quality: int = 82,
    webp_quality: int = 80,
    png_compress_level: int = 9,
    force_reencode: bool = False,
    allow_larger_bytes: bool = False,
    dry_run: bool = False,
) -> OptimizeResult:
    ext = path.suffix.lower()
    if ext not in _EXT_TO_FORMAT:
        return OptimizeResult(path=path, changed=False, skipped=True, reason="unsupported extension")

    try:
        old_bytes = path.stat().st_size
    except FileNotFoundError:
        return OptimizeResult(path=path, changed=False, skipped=True, reason="missing file")

    try:
        new_data, old_size, new_size, resized = encode_optimized_image_bytes(
            path,
            max_dim=max_dim,
            jpeg_quality=jpeg_quality,
            webp_quality=webp_quality,
            png_compress_level=png_compress_level,
        )
        should_encode = force_reencode or resized
        if not should_encode:
            return OptimizeResult(
                path=path,
                changed=False,
                skipped=True,
                reason="already within max_dim",
                old_bytes=old_bytes,
                new_bytes=old_bytes,
                old_size=old_size,
                new_size=old_size,
            )
        new_bytes = len(new_data)
    except (OSError, ValueError) as e:
        return OptimizeResult(path=path, changed=False, skipped=True, reason=f"cannot open: {e}")

    if not allow_larger_bytes and new_bytes > old_bytes:
        return OptimizeResult(
            path=path,
            changed=False,
            skipped=True,
            reason="re-encode larger than original",
            old_bytes=old_bytes,
            new_bytes=new_bytes,
            old_size=old_size,
            new_size=new_size,
        )

    if dry_run:
        return OptimizeResult(
            path=path,
            changed=True,
            skipped=False,
            reason="dry-run",
            old_bytes=old_bytes,
            new_bytes=new_bytes,
            old_size=old_size,
            new_size=new_size,
        )

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_bytes(new_data)
    tmp_path.replace(path)

    return OptimizeResult(
        path=path,
        changed=True,
        skipped=False,
        reason="optimized",
        old_bytes=old_bytes,
        new_bytes=new_bytes,
        old_size=old_size,
        new_size=new_size,
    )
