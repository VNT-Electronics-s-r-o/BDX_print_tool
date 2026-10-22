"""Validate and archive a Windows build for VNT Updater."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZIP_DEFLATED, ZipFile

DIR_NAME = "bdx_print_tool"
APP_ID = "bdx-print-tool"

def create_release(
    build_dir: Path,
    assets_dir: Path,
    output_dir: Path,
    app_id: str,
    version: str,
    base_url: str,
) -> None:
    if not re.fullmatch(
        r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version
    ):
        raise ValueError("Version must be MAJOR.MINOR.PATCH without leading zeroes.")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", app_id):
        raise ValueError("Application ID must contain lowercase words separated by hyphens.")
    url = urlsplit(base_url)
    if url.scheme not in ("http", "https") or not url.netloc:
        raise ValueError("Release base URL must be an absolute HTTP(S) URL.")
    if url.query or url.fragment or url.username or url.password:
        raise ValueError("Release base URL must not contain credentials, query, or fragment.")
    build_dir = build_dir.resolve()
    output_dir = output_dir.resolve()
    if output_dir == build_dir or build_dir in output_dir.parents:
        raise ValueError("Release output must be outside the build directory.")
    if not assets_dir.is_dir() or not any(assets_dir.iterdir()):
        raise ValueError("Source assets directory is missing or empty.")
    required = [f"{DIR_NAME}.exe", ".env.example", "_internal"]
    for name in required:
        path = build_dir / name
        if not (path.is_dir() if name == "_internal" else path.is_file()):
            raise ValueError(f"Build output is missing {name}.")
    files = sorted(path for path in build_dir.rglob("*") if path.is_file())
    for path in files:
        if path.name.lower() == ".env" or (
            path.name.lower().startswith(".env.") and path.name != ".env.example"
        ):
            raise ValueError("Private environment files must not be packaged.")
    for source in assets_dir.rglob("*"):
        if source.is_file():
            bundled = build_dir / "_internal" / "assets" / source.relative_to(assets_dir)
            if not bundled.is_file() or bundled.read_bytes() != source.read_bytes():
                raise ValueError(f"Bundled asset is missing or changed: {source.name}")
    template = build_dir / ".env.example"
    if template.read_bytes() != (assets_dir.parent / ".env.example").read_bytes():
        raise ValueError("Packaged environment template differs from the safe source template.")
    output_dir = output_dir / version
    output_dir.mkdir(parents=True, exist_ok=True)
    version_bytes = (json.dumps({"version": version}, indent=2) + "\n").encode("utf-8")
    package = output_dir / "package.zip"
    with ZipFile(package, "w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            name = path.relative_to(build_dir).as_posix()
            if name != "version.json":
                archive.write(path, name)
        archive.writestr("version.json", version_bytes)
    with ZipFile(package) as archive:
        if archive.testzip() is not None:
            raise ValueError("Package ZIP failed its integrity check.")
        expected = {path.relative_to(build_dir).as_posix() for path in files}
        expected.add("version.json")
        if set(archive.namelist()) != expected:
            raise ValueError("Package ZIP file layout differs from the build.")
        if archive.read("version.json") != version_bytes:
            raise ValueError("Package version metadata does not match the release.")
        for path in files:
            name = path.relative_to(build_dir).as_posix()
            if name != "version.json" and archive.read(name) != path.read_bytes():
                raise ValueError(f"Package ZIP contents differ: {name}")
    manifest = {
        "app_id": app_id,
        "version": version,
        "package_url": (
            f"{base_url.rstrip('/')}/v1/apps/{app_id}/releases/{version}/package.zip"
        ),
        "sha256": hashlib.sha256(package.read_bytes()).hexdigest(),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", type=Path, default=Path(f"dist/{DIR_NAME}"))
    parser.add_argument("--assets-dir", type=Path, default=Path("assets"))
    parser.add_argument("--output-dir", type=Path, default=Path("release"))
    parser.add_argument("--app-id", default=f"{APP_ID}")
    parser.add_argument("--version", required=True)
    parser.add_argument("--base-url", required=True)
    args = parser.parse_args()
    create_release(
        args.build_dir, args.assets_dir, args.output_dir,
        args.app_id, args.version, args.base_url,
    )
