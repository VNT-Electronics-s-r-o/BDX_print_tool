import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "build_release", ROOT / "packaging" / "build_release.py"
)
assert spec is not None and spec.loader is not None
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

DIR_NAME = "bdx_print_tool"
APP_ID = "bdx-print-tool"


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.assets = self.root / "assets"
        self.assets.mkdir()
        self.build = self.root / "dist" / DIR_NAME
        self.bundled = self.build / "_internal" / "assets"
        self.bundled.mkdir(parents=True)
        for source in (ROOT / "assets").iterdir():
            (self.assets / source.name).write_bytes(source.read_bytes())
            (self.bundled / source.name).write_bytes(source.read_bytes())
        self.template = (ROOT / ".env.example").read_bytes()
        (self.root / ".env.example").write_bytes(self.template)
        (self.build / ".env.example").write_bytes(self.template)
        (self.build / f"{DIR_NAME}.exe").write_bytes(b"test executable")
        self.output = self.root / "release"

    def create(self, version="1.2.3", base_url="https://updates.example.com/"):
        release.create_release(
            self.build, self.assets, self.output,
            APP_ID, version, base_url,
        )

    def test_root_layout_hidden_template_all_assets_version_and_checksum(self):
        (self.build / "version.json").write_text('{"version":"old"}', encoding="utf-8")
        self.create()
        version_dir = self.output / "1.2.3"
        self.assertEqual({path.name for path in self.output.iterdir()}, {"1.2.3"})
        self.assertEqual(
            {path.name for path in version_dir.iterdir()}, {"package.zip", "manifest.json"}
        )
        package = version_dir / "package.zip"
        manifest = json.loads((version_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest), {"app_id", "version", "package_url", "sha256"})
        self.assertEqual(manifest["app_id"], APP_ID)
        self.assertEqual(manifest["version"], "1.2.3")
        self.assertEqual(
            manifest["package_url"],
            f"https://updates.example.com/v1/apps/{APP_ID}/releases/1.2.3/package.zip",
        )
        self.assertRegex(manifest["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["sha256"], hashlib.sha256(package.read_bytes()).hexdigest())
        with ZipFile(package) as archive:
            self.assertIn(f"{DIR_NAME}.exe", archive.namelist())
            self.assertEqual(archive.read(".env.example"), self.template)
            self.assertEqual(json.loads(archive.read("version.json")), {"version": "1.2.3"})
            self.assertEqual(archive.namelist().count("version.json"), 1)
            for asset in self.assets.iterdir():
                self.assertEqual(
                    archive.read("_internal/assets/" + asset.name), asset.read_bytes()
                )

    def test_output_folder_uses_requested_version(self):
        for version in ("1.1.0", "2.0.0"):
            self.create(version=version)
            version_dir = self.output / version
            manifest = json.loads((version_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["version"], version)
            with ZipFile(version_dir / "package.zip") as archive:
                self.assertEqual(json.loads(archive.read("version.json")), {"version": version})
        self.assertEqual(
            {path.name for path in self.output.iterdir()}, {"1.1.0", "2.0.0"}
        )

    def test_rejects_missing_or_changed_assets(self):
        asset = self.bundled / "pair.png"
        asset.unlink()
        with self.assertRaisesRegex(ValueError, "Bundled asset"):
            self.create()
        asset.write_bytes(b"wrong")
        with self.assertRaisesRegex(ValueError, "Bundled asset"):
            self.create()

    def test_rejects_private_environment_files_anywhere_in_build(self):
        for name in (".env", ".ENV", ".env.local", ".env.production"):
            with self.subTest(name=name):
                private = self.build / "_internal" / name
                private.write_text("API_KEY=not-a-real-key", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Private environment"):
                    self.create()
                private.unlink()

    def test_rejects_missing_required_files(self):
        for name in (f"{DIR_NAME}.exe", ".env.example"):
            path = self.build / name
            content = path.read_bytes()
            path.unlink()
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "missing"):
                self.create()
            path.write_bytes(content)

    def test_rejects_modified_environment_template(self):
        (self.build / ".env.example").write_text("API_KEY=not-a-real-key", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "safe source template"):
            self.create()

    def test_rejects_invalid_versions_and_urls(self):
        for version in ("", "v1.2.3", "1.2", "01.2.3", "1.2.3-beta", "../1.2.3"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.create(version=version)
        for url in ("", "updates.example.com", "ftp://example.com", "https://a/?token=x",
                    "https://user:password@example.com", "https://a/#fragment"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.create(base_url=url)

    def test_rejects_output_inside_build(self):
        self.output = self.build / "release"
        with self.assertRaisesRegex(ValueError, "outside"):
            self.create()


if __name__ == "__main__":
    unittest.main()
