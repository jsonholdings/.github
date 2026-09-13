# .github — jsonholdings org

Org-wide GitHub configuration and assets for the `jsonholdings` GitHub organization.

## Org avatar

`assets/avatar-source.svg` is the single source (taken from jsonholdings.com's own
`favicon.svg`, never redrawn). `assets/avatar.png` (500x500) is built from it and is
what actually gets uploaded — GitHub has no API for an org's profile picture, so the
upload step is always a manual click.

**To change the logo, replace ONE file:**
1. Replace `assets/avatar-source.svg` with the new mark.
2. Run `python3 scripts/build_avatar.py`.
3. Upload the regenerated `assets/avatar.png` in GitHub org **Settings -> Profile
   picture**.

`python3 scripts/build_avatar.py --check` exits 1 if `avatar.png` no longer matches the
current `avatar-source.svg` (a sha256 of the source, recorded in
`assets/avatar.manifest.json` — never a byte-for-byte PNG comparison, since the SVG
renderer can legitimately produce different-but-correct bytes for the same source).

See [`ORG-SETTINGS.md`](ORG-SETTINGS.md) for the rest of the org's draft settings.
