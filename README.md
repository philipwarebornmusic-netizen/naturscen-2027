# Naturscen 2027

Shareable 3D seating and sightline model plus verified PDF material for proposal C.

## Live site

- Netlify: <https://naturscen.netlify.app/>
- 3D model: <https://naturscen.netlify.app/3d/>
- GitHub Pages mirror: <https://philipwarebornmusic-netizen.github.io/naturscen-2027/>
- Repository: <https://github.com/philipwarebornmusic-netizen/naturscen-2027>

The site compares:

- **A:** 2,353 original seats.
- **B:** 2,112 seats inside the 5° tighter, corner-anchored sight boundary.
- **C:** the same 2,112 seat IDs with 28 cm relative stagger between adjacent rows.

## Published material

`docs/` is the deployable static site used by GitHub Pages and Netlify.

- `docs/index.html` — share landing page.
- `docs/3d/index.html` — standalone Three.js model v4.3.
- `docs/*.pdf` — A, B and C seating plans.
- `docs/assets/platskarta-c-v1.5.png` — landing-page preview.
- `docs/*KAPACITET*.csv` — proposal C capacity and coordinates.

## Update workflow

From the project folder:

```bash
./build_staggered_v1_5.py
./sync_share_site.py
git add docs build_staggered_v1_5.py ny_karta_radplan_v1.md 3d/BYGGLOGG.md
git commit -m "Update Naturscen model"
git push
```

GitHub Pages publishes `docs/` from `main`. Netlify uses `netlify.toml` and the same `docs/` publish directory.

## Netlify

Netlify production is connected to the GitHub repository:

- Production URL: <https://naturscen.netlify.app/>
- Branch: `main`
- Publish directory: `docs`
- Configuration: `netlify.toml`
- Build command: none

Every push to `main` triggers a new production deploy. GitHub Pages remains available as a mirror.

## Local smoke test

```bash
python3 -m http.server 8080 --directory docs
```

Open <http://localhost:8080/>. Test the landing page, all three PDFs, A/B/C switching, exact seat selection and the seated view.

## Model limits

This is a digital planning and sightline study, not a surveyed or authority-approved audience, evacuation or set-out plan. Field measurement is required before operational use.
