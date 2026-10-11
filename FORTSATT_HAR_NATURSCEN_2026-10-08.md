# Fortsätt här - Naturscen

Sparat: 2026-10-10

## Projektmapp
`/Users/philipwareborn/Documents/OMP/naturscen`

## Läs först nästa gång
1. `FORTSATT_HAR_NATURSCEN_2026-10-08.md` - denna handoff.
2. `ny_karta_radplan_v1.md` - aktuell projektstatus och leveranslista.
3. `3d/BYGGLOGG.md` - teknisk bygglogg för 3D-verktyget.

## Aktuell status
Arbetet är sparat och verifierat. Nästa gång ska arbetet fortsätta från:
- 2D-kartor: **v1.5**
- 3D-verktyg: **v4.3**

A/B från v1.4/v4.2 finns kvar oförändrade. C v1.5/v4.3 är det nya förslaget med förskjutna rader.

## Viktig användaravsikt
De två yttre siktgränserna ska fortsatt starta i scenens framhörn. A/B ska bevara tidigare stolsgeometri. C ska testa 28 cm relativ förskjutning mellan intilliggande rader för bättre möjlighet att se mellan personer framför.

## Genomförda huvudspår / threads

### Thread 1 - Exakt platsinmatning i 3D
Implementerat i `3d/naturscenen_3d_sikt_v4.1.html` och följer med i `3d/naturscenen_3d_sikt_v4.2.html`.

Funktion:
- Välj parkett.
- Välj sektion.
- Skriv rad.
- Skriv stol.
- Klicka `Visa plats`.
- Kameran går till exakt stol.
- Klicka `Sitt i stolen` för biljettköparens POV.

Verifierat:
- Browser smoke test utan JS-fel.
- Exakt plats i B-läge testad: `2:a parkett -> mitt -> rad 1 -> stol 1`.
- POV-läge öppnade korrekt.

### Thread 2 - Korrigerade siktgränser från scenhörn
Tidigare v1.3/v4.1 använde sparade linjeankare strax bakom scenfronten. Det är nu rättat.

Nya v1.4/v4.2:
- Svart linje = gamla yttergränsen, men start flyttad till scenens framhörn.
- Röd streckad linje = 5° snävare från samma scenhörn.
- Stolar/rader är inte flyttade, vridna eller ompackade.
- Stol tas bort om något hörn av stolsymbolen hamnar utanför ny röd gräns.

Scenhörn i SVG-pixlar:
- Vänster: `(637, 315.7)`
- Höger: `(862, 315.7)`

Kapacitet:
- Original/A: 2 353 platser.
- Ny 5° snävare/B: 2 112 platser.
- Bortfall: 241 platser / 10,24 %.

Per sektion:
| Sektion | Före | Ny | Bort |
|---|---:|---:|---:|
| 1:a parkett mitt | 364 | 364 | 0 |
| 1:a vänster | 146 | 106 | 40 |
| 1:a höger | 148 | 103 | 45 |
| 2:a parkett mitt | 390 | 390 | 0 |
| 2:a vänster | 279 | 248 | 31 |
| 2:a höger | 458 | 366 | 92 |
| 3:e parkett | 568 | 535 | 33 |
| Totalt | 2 353 | 2 112 | 241 |

### Thread 3 - Nya 2D-underlag och PDF:er
Skapade/uppdaterade filer i projektroten:
- `Platskarta_Naturscen_2027_UTKAST_v1.4.pdf`
- `Platskarta_Naturscen_2027_UTKAST_v1.4.svg`
- `Platskarta_Naturscen_2027_UTKAST_v1.4.png`
- `Platskarta_Naturscen_2027_FOTOKONTROLL_v1.4.svg`
- `Platskarta_Naturscen_2027_FOTOKONTROLL_v1.4.png`
- `Platskarta_Naturscen_2027_KAPACITET_v1.4.csv`
- `Platskarta_Naturscen_2027_ORIGINAL_HORNFIX_v1.4.pdf`
- `Platskarta_Naturscen_2027_ORIGINAL_HORNFIX_v1.4.svg`
- `Platskarta_Naturscen_2027_ORIGINAL_HORNFIX_v1.4.png`
- `Platskarta_Naturscen_2027_ORIGINAL_HORNFIX_FOTOKONTROLL_v1.4.svg`
- `Platskarta_Naturscen_2027_ORIGINAL_HORNFIX_FOTOKONTROLL_v1.4.png`
- `Platskarta_Naturscen_2027_ALTERNATIV_HORNFIX_5GRADER_v1.4.pdf`
- `Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5.pdf`
- `Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5.svg/.png`
- `Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5_FOTOKONTROLL.svg/.png`
- `Platskarta_Naturscen_2027_KAPACITET_FORSKJUTNA_RADER_28CM_v1.5.csv`

### Thread 4 - 3D v4.3
Aktuell 3D-fil:
- `3d/naturscenen_3d_sikt_v4.3.html`

Innehåll:
- A-läge: 2 353 originalstolar.
- B-läge: 2 112 stolar med 5° snävare hörnförankrad yttergräns.
- C-läge: samma 2 112 plats-ID med 28 cm relativ förskjutning mellan intilliggande rader.
- Exakt platsinmatning och separat plats-/sittvyminne för A/B/C.
- Geometrisk huvudkontroll med 10,5 cm huvudradie och 5 cm säkerhetsmarginal.
- Scenmitt som huvudverdikt och nio mål över scenbredden.
- PDF-länkar till A-, B- och C-underlag.

Verifierat:
- Inbäddade counts: `original = 2353`, `inward = 2112`, `staggered = 2112`.
- Browser smoke: C-läge, exakt platsval, POV och återställning mellan B/C fungerade utan JS-fel.

### Thread 5 - Förslag C med 28 cm radförskjutning
- Normal stolcentrumdelning är 56 cm; 28 cm är exakt en halv delning.
- C byggs nominellt som −14/+14 cm mellan varannan rad.
- Sektionsvisa baskorrigeringar på högst 6,8 cm håller alla 2 112 stolar innanför röd gräns.
- Stolavstånd 56 cm, radavstånd 92 cm, sektionsvinklar och alla B-ID behålls.
- Vid 1,20 m öga/1,25 m huvud ökade fri scenmitt från 1 201 B-platser till 1 360 C-platser.
- Över nio scenmål ökade fria strålar från 11 253 till 11 489 av 19 008.
- Om alla huvuden sätts till 1,50 m är C inte bättre totalt. Förslaget är därför en förbättringsmöjlighet, inte en siktgaranti.

### Thread 6 - Delningssajt, GitHub och Netlify
- Primär publik sajt: `https://naturscen.netlify.app/`
- Direkt till 3D: `https://naturscen.netlify.app/3d/`
- GitHub Pages-spegel: `https://philipwarebornmusic-netizen.github.io/naturscen-2027/`
- GitHub: `https://github.com/philipwarebornmusic-netizen/naturscen-2027`
- `docs/` innehåller den publicerade sajten, 3D v4.3, A/B/C-PDF:er, C-förhandsbild och kapacitets-CSV.
- `sync_share_site.py` kopierar verifierade projektfiler till `docs/` inför publicering.
- Netlify publicerar automatiskt `docs/` från `main`; GitHub Pages publicerar samma mapp som spegel.

## Verifiering utförd
- SVG:
  - C ren karta: 2 112 unika stolar.
  - C fotokontroll: samma 2 112 ID och koordinater.
  - Alla roterade stolshörn innanför röd 5°-gräns.
- CSV:
  - `kvar_forskjuten = 2112`
  - `bort_siktgrans = 241`
- PDF/PNG:
  - Tre PDF-sidor renderade: ren karta, fotokontroll och dokumenterad siktanalys.
  - Analysens nyckeltal, förklaring och lång-person-begränsning finns på sida 3.
  - Båda PNG-filerna öppnade och kontrollerade visuellt.
- 3D/browser:
  - v4.3 laddade utan konsol- eller sidfel.
  - A/B/C visade 2 353 / 2 112 / 2 112 stolar.
  - C visade `C: 2 112 stolar · 28 cm förskjutna rader`.
  - Exakt plats `1:a parkett mitt · rad 2 · plats 13`, nio scenmål, POV och B/C-minne testades.

## Rekommenderad nästa start
1. Öppna projektmappen:
   `open /Users/philipwareborn/Documents/OMP/naturscen`
2. Öppna 3D-verktyget:
   `3d/naturscenen_3d_sikt_v4.3.html`
3. För presentation av det nya förslaget, använd:
   - `Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5.pdf`
   - `3d/naturscenen_3d_sikt_v4.3.html`
4. A/B-underlagen v1.4 finns kvar för jämförelse.

## Risk/notering
PDF/SVG/PNG är framtagna från modellen och kontrollerade digitalt. Det är fortfarande en planmodell, inte inmätning eller myndighetsgodkänd publik-/utrymningsplan. Kontrollmätning på plats krävs innan skarpa beslut.
