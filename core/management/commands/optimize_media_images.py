from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.image_optimization import encode_optimized_image_bytes, optimize_image_file


@dataclass
class Stats:
    total: int = 0
    changed: int = 0
    skipped: int = 0
    bytes_before: int = 0
    bytes_after: int = 0


def _iter_image_files(root: Path, *, extensions: set[str]) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in extensions:
            files.append(p)
    return sorted(set(files))


def _variant_path(original: Path, width: int) -> Path:
    return original.with_name(f"{original.stem}-{width}w{original.suffix}")


class Command(BaseCommand):
    help = "Resize/re-encode images under MEDIA_ROOT in-place (defaults to max 1080px)."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--max-dim", type=int, default=1080)
        parser.add_argument("--jpeg-quality", type=int, default=82)
        parser.add_argument("--webp-quality", type=int, default=80)
        parser.add_argument("--png-compress-level", type=int, default=9)
        parser.add_argument("--force", action="store_true", help="Re-encode even if already within max-dim.")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--allow-larger", action="store_true", help="Allow output bytes to exceed original.")
        parser.add_argument(
            "--variants",
            type=str,
            default="64,128,256,360,720",
            help="Comma-separated responsive widths to generate alongside originals, e.g. 360,720 (empty disables).",
        )
        parser.add_argument("--force-variants", action="store_true", help="Re-generate variants even if they exist.")
        parser.add_argument(
            "--extensions",
            type=str,
            default="jpg,jpeg,png,webp",
            help="Comma-separated list, e.g. jpg,jpeg,png",
        )
        parser.add_argument(
            "paths",
            nargs="*",
            help="Optional file/dir paths (relative to MEDIA_ROOT or absolute). Defaults to MEDIA_ROOT.",
        )

    def handle(self, *args, **options) -> None:
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            raise SystemExit(f"MEDIA_ROOT does not exist: {media_root}")

        exts = {("." + e.strip().lower().lstrip(".")) for e in str(options["extensions"]).split(",") if e.strip()}
        if not exts:
            raise SystemExit("No extensions provided.")

        max_dim = int(options["max_dim"])
        dry_run = bool(options["dry_run"])
        variants_raw = str(options["variants"] or "").strip()
        variant_widths: list[int] = []
        if variants_raw:
            try:
                variant_widths = sorted({int(x.strip()) for x in variants_raw.split(",") if x.strip()})
            except ValueError:
                variant_widths = [360, 720]

        roots: list[Path] = []
        if options["paths"]:
            for raw in options["paths"]:
                p = Path(raw)
                if not p.is_absolute():
                    p = media_root / p
                roots.append(p)
        else:
            roots = [media_root]

        files: list[Path] = []
        for root in roots:
            if root.is_file():
                files.append(root)
            elif root.is_dir():
                files.extend(_iter_image_files(root, extensions=exts))
            else:
                self.stderr.write(self.style.WARNING(f"Skipping missing path: {root}"))

        files = sorted(set(files))
        if not files:
            self.stdout.write("No images found.")
            return

        def display_path(p: Path) -> str:
            try:
                return str(p.relative_to(media_root))
            except ValueError:
                return str(p)

        stats = Stats(total=len(files))
        for i, path in enumerate(files, start=1):
            result = optimize_image_file(
                path,
                max_dim=max_dim,
                jpeg_quality=int(options["jpeg_quality"]),
                webp_quality=int(options["webp_quality"]),
                png_compress_level=int(options["png_compress_level"]),
                force_reencode=bool(options["force"]),
                allow_larger_bytes=bool(options["allow_larger"]),
                dry_run=dry_run,
            )
            stats.bytes_before += result.old_bytes
            stats.bytes_after += result.new_bytes if (result.changed and not result.skipped) else result.old_bytes

            if result.changed and not result.skipped:
                stats.changed += 1
                self.stdout.write(
                    f"[{i}/{stats.total}] OK {display_path(path)} "
                    f"{result.old_size}→{result.new_size} "
                    f"{result.old_bytes/1024:.1f}KiB→{result.new_bytes/1024:.1f}KiB"
                )
            else:
                stats.skipped += 1
                self.stdout.write(f"[{i}/{stats.total}] SKIP {display_path(path)} ({result.reason})")

            if variant_widths:
                for w in variant_widths:
                    if w <= 0:
                        continue
                    if max_dim and w > max_dim:
                        continue
                    vp = _variant_path(path, w)
                    if vp.exists() and not options["force_variants"]:
                        continue
                    try:
                        data, old_size, new_size, resized = encode_optimized_image_bytes(
                            path,
                            max_dim=w,
                            jpeg_quality=int(options["jpeg_quality"]),
                            webp_quality=int(options["webp_quality"]),
                            png_compress_level=int(options["png_compress_level"]),
                        )
                    except Exception:
                        continue
                    if not resized:
                        continue
                    if dry_run:
                        continue
                    vp.write_bytes(data)

        saved = stats.bytes_before - stats.bytes_after
        self.stdout.write("")
        self.stdout.write(f"Images: {stats.total} total, {stats.changed} optimized, {stats.skipped} skipped.")
        self.stdout.write(f"Bytes:  {stats.bytes_before/1024/1024:.2f}MiB → {stats.bytes_after/1024/1024:.2f}MiB")
        self.stdout.write(f"Saved:  {saved/1024/1024:.2f}MiB{' (dry-run)' if dry_run else ''}")
