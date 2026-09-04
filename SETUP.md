# Setup

Everything here goes into a repo named **exactly `naitikk31`** (`github.com/naitikk31/naitikk31`).
That magic repo's README is what shows on your GitHub profile.

---

## 1. Install Python dependencies

```powershell
pip install Pillow
```

`Pillow` is only needed for `dotify.py` (the portrait generator). `radar.py` and `cards.py` use the stdlib.

---

## 2. Generate local assets

```powershell
# With your photo (recommended — run this first):
.\setup.ps1 -Image .\me.jpg

# Without a photo (skips portrait):
.\setup.ps1
```

This will:
- Draw the skill radar from `assets/skills.json`
- Attempt to pull the language radar from the GitHub API (works without a token)
- Generate the stat card and repo cards from `assets/projects.json`
- Dot-matrix your photo into `assets/portrait.svg`

Then open `preview.html` in a browser to check everything locally before pushing.

> **Portrait options** — the default command uses `--equalize --detail 0.5 --reveal --color`.
> See `SETUP.md` → Tuning the portrait for alternatives.

---

## 3. Fill in the social link placeholders

Open `README.md` and replace these strings:

| Placeholder | Replace with |
|---|---|
| `YOUR_LINKEDIN` | `https://linkedin.com/in/YOUR_HANDLE` |
| `YOUR_EMAIL` | `mailto:your@email.com` |
| `YOUR_LEETCODE` | `https://leetcode.com/u/YOUR_HANDLE` |
| `YOUR_CODEFORCES` | `https://codeforces.com/profile/YOUR_HANDLE` |
| `YOUR_PORTFOLIO` | `https://your-portfolio.com` |

---

## 4. Push to GitHub

```powershell
git init && git branch -M main
git add -A && git commit -m "feat: initial profile README"
git remote add origin https://github.com/naitikk31/naitikk31.git
git push -u origin main
```

The repo **must be public** — SVG assets are served by relative path, so a private repo shows broken images.

---

## 5. Allow Actions to write to the repo

Repo → **Settings** → **Actions** → **General** → **Workflow permissions** →
select **Read and write permissions** → Save.

Without this the Charts & cards and Snake workflows fail when they try to `git push`.

---

## 6. Add the METRICS_TOKEN secret

`lowlighter/metrics` needs its own token — the built-in `GITHUB_TOKEN` can't read profile-level data
like the contribution calendar.

1. Go to: https://github.com/settings/tokens → **Generate new token (classic)**
2. Scopes: **`read:user`** (add **`repo`** if you want private repos counted in language stats)
3. Copy the token
4. Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
5. Name: **`METRICS_TOKEN`**, paste the value → Save

---

## 7. Trigger the workflows

Repo → **Actions** tab → enable workflows if prompted, then run each one via **Run workflow**:

| Workflow | Produces | Lands in |
|---|---|---|
| **Metrics** | 3D isometric calendar, language chart, achievements | `assets/metrics.*.svg` on `main` |
| **Snake** | Snake eating your contribution graph | the `output` branch |
| **Charts and cards** | Skill radar, language radar, stat card, repo cards | `assets/radar*.svg`, `assets/card-*.svg` on `main` |

**Run order matters:** Metrics first, then Snake, then Charts. Each takes 1-3 minutes.

> The snake images (`raw.githubusercontent.com/.../output/snake*.svg`) will 404 until the Snake
> workflow has pushed to the `output` branch at least once. That's expected.

---

## 8. Verify

Visit `github.com/naitikk31` — all sections should be visible. If an image is missing:

| Symptom | Likely cause |
|---|---|
| Metrics SVGs missing | `METRICS_TOKEN` not set or expired |
| Snake SVGs 404 | Snake workflow hasn't run yet, or write permissions not enabled |
| Repo cards show nothing | Repo name in `projects.json` doesn't match GitHub exactly |
| Portrait missing | `dotify.py` not yet run locally (push `assets/portrait.svg` first) |

---

## Tuning the portrait

The default command used by `setup.ps1`:

```powershell
python scripts\dotify.py assets\photo.jpg -o assets\portrait `
  --cols 100 --equalize --detail 0.5 --color --reveal
```

Other looks you can try:

```powershell
# Green monochrome (matches the contribution-graph colour palette)
python scripts\dotify.py assets\photo.jpg -o assets\portrait `
  --cols 88 --equalize --detail 0.5 --animate

# Binary 0s and 1s grid
python scripts\dotify.py assets\photo.jpg -o assets\portrait `
  --mode binary --cols 62 --equalize --detail 0.5

# Circle-cropped (good for a tight headshot)
python scripts\dotify.py assets\photo.jpg -o assets\portrait `
  --cols 100 --equalize --detail 0.5 --color --circle --reveal

# Higher resolution (more detail, larger file)
python scripts\dotify.py assets\photo.jpg -o assets\portrait `
  --cols 130 --equalize --detail 0.5 --color --reveal
```

Key flags:
- `--equalize` — essential for a portrait: recovers shadow detail in dark hair/areas
- `--detail 0.5` — puts facial structure back after equalize flattens it
- `--color` — keeps original pixel colours (writes one `portrait.svg`, not a dark/light pair)
- `--reveal` — row-by-row load animation (plays once per page load)
- `--cols` — resolution dial: 60 is chunky/abstract, 100 is default, 130 is sharp but ~500 KB

---

## Tuning the skill radar

Edit `assets/skills.json` and re-run `setup.ps1` or:

```powershell
python scripts\radar.py --data assets\skills.json -o assets\radar
```

Values are 0–100 and purely self-rated. 5–8 axes reads best.

---

## Tuning the project cards

Edit `assets/projects.json` — the `repo` key must match the **exact** GitHub repo name.
Stars, forks and primary language are fetched live from the API on every workflow run.
