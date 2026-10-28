"""Verify the published browser artifact, without access to private development data."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
for path in root.rglob('*'):
    relative = path.relative_to(root)
    if relative.parts[0] == '.git' or not path.is_file():
        continue
    allowed = (str(relative) in ('README.md', 'LICENSE', 'NOTICE.md', 'CREDITS.md', 'release.json', 'verify_release.py', '.github/workflows/pages.yml')
               or relative.parts[0] == 'site'
               or (relative.parts[0] == 'media' and path.suffix == '.png'))
    if not allowed:
        raise SystemExit(f'Unexpected repository file: {relative}')
manifest = json.loads((root / 'release.json').read_text())
site = root / 'site'
actual = {}
for path in site.rglob('*'):
    if path.is_symlink():
        raise SystemExit(f'Symlinks are not allowed: {path}')
    if path.is_file():
        relative = path.relative_to(site)
        allowed = (str(relative) in ('index.html', 'LICENSE.txt', 'THIRD_PARTY_NOTICES.txt', 'data/public_catalog.json', 'robots.txt', 'sitemap.xml')
                   or (relative.parts[0] == 'assets' and path.suffix in ('.js', '.css'))
                   or (relative.parts[0] == 'brand' and path.suffix in ('.svg', '.png', '.ico', '.webmanifest')))
        if not allowed:
            raise SystemExit(f'Unexpected public file: {relative}')
        actual[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
if actual != manifest['files']:
    raise SystemExit('Release files do not match the verified build manifest')
for required in ('index.html', 'LICENSE.txt', 'THIRD_PARTY_NOTICES.txt', 'data/public_catalog.json'):
    if required not in actual:
        raise SystemExit(f'Missing release file: {required}')
print(f'Verified browser release: {manifest["sourceRevision"][:12]}, {len(actual)} files')
