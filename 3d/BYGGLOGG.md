# Bygglogg — Naturscen 3D siktverktyg

Syfte: dokumentera hur `naturscenen_3d_sikt_v4.3.html` är byggt, så att bygget kan
underhållas och **återskapas för andra arenor** (grunden för en produkt/tjänst).
Allt är avsiktligt en fristående HTML utan installation (Three.js via CDN).

Senast uppdaterad: 2026-10-10.

Aktuell modell: v4.3 / platskarta v1.5 lägger till C med 28 cm relativ förskjutning mellan intilliggande rader. C behåller samma 2 112 platser och röda 5°-gräns som B. A och B från v4.2 är oförändrade.

Aktuell jämförelsemodell v4.3: A visar 2 353 originalstolar, B visar 2 112 stolar innanför den 5° snävare hörnförankrade gränsen och C visar samma 2 112 plats-ID med förskjutna rader. Separat plats-/sittvyminne återställer vald plats per alternativ. Siktprovet använder ett geometriskt huvud med radie 10,5 cm i stället för den tidigare 32 cm breda plankorridoren och redovisar scenmitt plus nio mål över scenbredden.

---

## 1. Artefakter

| Fil | Innehåll |
|---|---|
| `naturscenen_3d_sikt_v4.3.html` | Aktuell A/B/C-modell: 2 353 / 2 112 / 2 112 stolar, separat sittplatsminne, geometrisk huvudkontroll och nio scenmål. |
| `naturscenen_3d_sikt_v4.2.html` | Tidigare A/B-modell. Historik och källa för v4.3. |
| `naturscenen_3d_sikt_v4.1.html` | Tidigare A/B-modell från v1.3. Historik: linjerna utgick från sparade scenankare strax bakom scenfronten. |
| `naturscenen_3d_sikt_v3.html` | Tidigare fast modell av 5°-alternativet. Behålls som historik. |
| `naturscenen_3d.html` | Ursprunglig terrängmodell (endast terräng + byggnader + en klickbar plats). Behålls som referens. |
| `naturscenen_hojddata_crop.tif` | DEM, GeoTIFF, 1 m, georefererad (SWEREF99 TM / RH2000). |
| `naturscenen_hojddata_3m.csv` | Samma DEM nedsamplat till 3 m grid (E,N,Z), 30 800 punkter. |
| `naturscenen-projektunderlag.md` | Ursprungligt underlag (koordinater, mått, byggnader, scen). |
| `../Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5.svg` | C-underlag med 2 112 förskjutna stolar. Källa för `ALTERNATIVES.staggered`. |
| `../Platskarta_Naturscen_2027_UTKAST_v1.4.svg` | B-underlag med 2 112 stolar och röd 5°-gräns. |
| `../Platskarta_Naturscen_2027_ORIGINAL_HORNFIX_v1.4.svg` | A-underlag med alla 2 353 stolar och gammal gräns flyttad till scenhörnen. |

---

## 2. Koordinatsystem och transform (kärnan)

- **3D-modell:** SWEREF99 TM (E,N i meter), höjder RH2000 (m ö.h.).
- **2D-platskarta:** drönarfoto-pixlar, **~12,5 px/m**, "scenen överst".
- Ingen färdig koppling fanns; den härleddes analytiskt och validerades.

**Transform px → SWEREF (180°-rotation, ingen spegling):**
```
E = 472510 − (x − 749.5) / 12.5
N = 6399861 + (y − 315.7) / 12.5
```
- Ankare: scenens ritade framkant-mittpunkt `(x=749.5, y=315.7)` px ↔ `(E 472510, N 6399861)`.
- Skala: 12,5 px/m (från grusgångarnas kalibrering; osäkerhet ±5 %).
- Orientering: publiken ligger **norr** om scenen (scenen mot maskinhallens norrsida, djup norrut) och skogsbrynet längst ned i fotot → "bild-ned = norr", öst=vänster. Alltså 180°-rotation, determinant +1 (ingen spegling).

**Validering (viktig för trovärdighet):**
- Aktuell B-modell innehåller 2 112 stolar, ett urval av originalets stolar norr om scenen. A-modellen innehåller alla 2 353 originalstolar.
- Markhöjden **stiger** från scenens fot (291,1 m) upp i publiken (upp till 295,7 m).
- Korrelation mellan avstånd-från-scen och markhöjd: **r = 0,97** (marken lutar konsekvent uppåt bort från scenen — rätt orientering).

Konstanterna (`PXPM`, `AX/AY`, `AE/AN`) ligger i 2D→3D-genereringen och i HTML:ens `STAGE`.

---

## 3. Terräng och nyckelobjekt

- **DEM:** Lantmäteriet öppen höjddata (Markhöjdmodell grid 1+), CC BY 4.0. Utsnitt NV-hörn `E 472245, N 6400000`, 600 × 462 m. I HTML: grid **200 × 154 celler, 3 m**, höjder 271,1–304,8 m.
- **Scen:** mot maskinhallens NV-hörn `E 472501, N 6399849`. Bredd 18 m (Ö–V), djup 11 m (N), valvtak R=9 m, scengolv default 1,0 m över mark (framkant). Referenspunkt sikt = framkantens mitt `E 472510, N 6399861`.
- **Byggnader:** Maskinhall (`E 472518.5, N 6399843.25`, 34×11,5 m, h≈9 m), Ladugård (`E 472526.5, N 6399801.5`, 50×13 m). Bäring 90° (rakt Ö–V).
- **Ljud & Ljus-tält:** kartmarkörens centrum `(x=755, y=719,5)` ger `E 472509,56, N 6399893,30`. 3D-markeringen är ett klassiskt popup-tält med **4 m bredd (Ö–V)** och **3 m djup (N–S)**, öppen konstruktion med fyra ben, pyramidtak och skylt.
- **Stol:** Klappstol ABERDEEN — sits 390×390, sitthöjd 445, totalhöjd 810 mm.

---

## 4. Datapipeline (2D → 3D)

1. Parsa A- och B-stolar ur v1.4-SVG (`data-section/-row/-seat` + `translate(x y)`).
2. Bygg C från B med nominellt −14/+14 cm längs varje rads lokala x-riktning. Sektionsvisa baskorrigeringar är högst 6,8 cm och bevarar 28 cm relativ skillnad.
3. Kontrollera unika och oförändrade ID, 56 cm normal stolcentrumdelning samt hela den roterade stolsymbolen innanför röd gräns.
4. Transformera px → (E,N) enligt §2.
5. Bädda in `ALTERNATIVES.original` (2 353), `ALTERNATIVES.inward` (2 112), `ALTERNATIVES.staggered` (2 112), `TERRAIN`, sektionsdata och siktgränser i HTML.
6. Terränggriden återanvänds från `naturscenen_3d.html`.
7. `../build_staggered_v1_5.py` återskapar v1.5-SVG/PNG/PDF/CSV och v4.3-HTML från de verifierade v1.4/v4.2-källorna.

Sektioner: `mitt1, mitt2, gul_o, gul_v, bla_o, bla_v, tredje` (röd/grön/gul/blå/orange).

---

## 5. 3D-appens funktioner

- **Motor:** Three.js r128 (CDN). InstancedMesh för stolar (ram + sits), personer (kropp + huvud) och fyllnad.
- **Alternativ:** A/B/C med bibehållen kamera och separat plats-/POV-minne.
- **Välj plats:** klicka i 3D eller skriv exakt parkett, sektion, rad och stol.
- **Sitt i stolen:** förstapersonsvy från vald stols ögonhöjd; höjdförstoring låses till 1×; egen stol döljs.
- **Personer:** lågpoly sittande figurer; huvudhöjd styrs av reglaget och gäller alla modellerade personer.
- **Geometrisk huvudkontroll:** minsta 3D-avstånd från siktstrålen till huvudcentrum jämförs med huvudradien 10,5 cm och säkerhetsmarginalen 5 cm.
- **Scenmål:** scenmitt används för huvudverdikt och nio mål mellan −8 och +8 m över scenbredden redovisas som `Fria scenmål`.
- **Terräng:** siktstrålen samplas mot aktuell DEM/fyllnadsmodell. Tvärsnittet visar mark, närliggande huvuden och siktlinje.
- **Markfyllning (amfiteater), per sektion:** se §6.
- **Perspektiv:** Översikt / Sidovy (lutning scen→publik) / Bakifrån.
- **Reglage:** höjdförstoring, scengolv, ögonhöjd sittande (1,20), huvudhöjd framför (1,25).

---

## 6. Fyllnadsmodeller (markmodellering mot verklig terräng)

Verktyget har nu två jämförbara modeller. Båda lägger fyllning **ovanpå befintlig
DEM**, höjer aldrig genom att gräva ur, och använder samma sektionmask
(stolarnas konvexa hull + 0,9 m buffert). Reglaget anger alltid **maximal
extra höjd längst bak i sektionen** — inte en konstant höjning av hela sektionen.

### 6.1 Radprofil — ny standardmodell

Radprofilen använder centrum för sektionens första och sista stolsrad som en
front→bak-axel. Varje terrängpunkt projiceras på axeln:

```
t = clamp(dot(P − front, back − front) / |back − front|², 0, 1)
fill(P) = lift · t
mark(P) = DEM(P) + fill(P)
```

- Första raden är modellens nollpunkt (`t = 0`).
- Sista raden når vald maxhöjd (`t = 1`).
- Mellanliggande rader höjs gradvis i radprofilens riktning.
- Den naturliga DEM-lutningen finns kvar under den nya profilen.
- Visad procent är `lift / front→bak-längd`.

Detta är den rekommenderade modellen när intentionen är: första raden orörd,
sedan en kontrollerad höjning rad för rad mot bakre raden.

### 6.2 Avståndskil — sparad tidigare modell

Den tidigare modellen finns kvar som `Avståndskil (sparad)`:

```
t = clamp((dist(P, scenreferens) − d0) / (d1 − d0), 0, 1)
fill(P) = lift · t
mark(P) = DEM(P) + fill(P)
```

- `d0` och `d1` hämtas från närmaste respektive bortersta stol i sektionen.
- Profilen följer radiellt avstånd från scenens referenspunkt.
- Den är därför inte uttryckligen bunden till första/sista radens centrumlinje.
- Den bevaras för reproducerbarhet och visuell jämförelse med tidigare bilder.

### 6.3 Praktisk skillnad och begränsningar

| Egenskap | Radprofil | Avståndskil |
|---|---|---|
| Nollpunkt | Första radens centrumlinje | Närmaste stolens scenavstånd |
| Riktning | Sektionens faktiska front→bak-riktning | Radiellt från scenen |
| Tolkning | Höjning rad för rad | Avståndsbaserad kil |
| Standard i appen | Ja | Nej, välj för jämförelse |
| Maxhöjd | Sista raden | Bortersta stol/zon |

Båda modellerna är visuella terrängprofiler, inte en färdig massberäkning.
Fyllnadsvolym påverkas fortfarande av den förenklade sektionmasken, DEM:ens
3 m-grid, slänter, kompaktering, gångar och eventuell massbalans. Ingen av
modellerna löser ännu automatiskt minsta fyllnad för ett givet C-värde.

Med `+2,2 m` i en sektion som är cirka 25 m djup blir den extra profilens
genomsnittliga storleksordning cirka 1,1 m och lutningen cirka 9 %, före
detaljerad projektering. Detta ska läsas som modellens geometriska
storleksordning, inte som en entreprenadmängd.

---

## 7. Att återskapa för en annan arena (Fas 1 — tjänst/generator)

Behövs som indata:
1. **DEM** över platsen (GeoTIFF, helst 1 m). SE: Lantmäteriet (CC BY). Annars Copernicus GLO-30 (~30 m, grövre).
2. **Scenens läge** i samma koordinatsystem: framkant-mitt (E,N), bredd, djup, golvhöjd.
3. **Stolskälla**: en SVG/CSV med sektion/rad/plats + position (px eller meter).
4. **Transform-kontrollpunkter**: minst 1 ankare (t.ex. scenframkant) + skala + verifierad orientering (nord). Kontrollera mot byggnadshörn/vägar i drönarfoto.

Steg:
1. Bygg terränggrid ur DEM (origin, cellstorlek, z-matris) → `TERRAIN`.
2. Härled px→världstransform (se §2) och **validera** (stolar på DEM, korrelation dist↔höjd).
3. Parsa stolar → `SEATS`.
4. Fyll i scen/byggnader (SWEREF-koordinater).
5. Byt ut `TERRAIN`, `SEATS`, `SECMETA/SECORDER/SECROWS`, scen/byggnadskonstanter i mallen.

**Mål (nästa steg):** lyfta ut ovanstående till en `venue.json`
(`{dem, transform:{pxpm,anchor_px,anchor_en,rotation}, stage, buildings[], sections}`)
så att en ny arena är en konfig, inte en kodändring.

---

## 8. Ändringslogg (denna session)

1. Placerade alla 2 353 stolar i 3D på verkliga höjder (transform + DEM).
2. Stolval (klick + inmatning), sitt-i-stolen-POV, artistobjekt, siktlinje med huvud-ocklusion.
3. Sidledsnavigering (WASD/piltangenter); byggnader byggs om vid höjdändring (fixade svävande byggnader i POV).
4. Personer i stolarna (togglas; alltid i sittvyn; egen stol döljs).
5. Personer → riktiga lågpoly-människor (varierade klädfärger); huvudhöjd kopplad till siktparameter.
6. Klappstol (Aberdeen) istället för lådor; sits tonad i sektionsfärg.
7. Fix: personer försvann/ögat följde inte marken vid fyllnadsändring i POV.
8. Ny grafisk profil: Inter/Space Grotesk, kort-system, vänster/höger-listor, tomt-lägen.
9. Fyllnad zonindelad → **målhöjd per sektion** (kil ovanpå verklig terräng).
10. Perspektiv-knappar (Översikt/Sidovy/Bakifrån); färgprickar per sektion i fyllnadslistan.
11. "Från scenen"-vy + panorering (Shift+dra / högerdra / WASD).
12. Bekräftat: fyllnad "av"/0 = orörd befintlig mark (mark = DEM exakt, endast pålägg).
13. Satellitdrapering (Esri World Imagery) med exakt UV via invers TM per vertex; växlare Digital/Satellit; modell-byggnader döljs i satellitläge så verkliga syns. Källa bör bytas mot Lantmäteriets ortofoto i produkt.
14. Musiker + instrument för orkester/band/kör (flygel, trummor, gitarr, bas, klaviatur, notställ, mikrofon, körgradäng) istället för stolpar.
15. Ljud & Ljus-märkningen från 2D-platskartan byggdes in som popup-tält i 3D (4 × 3 m, synligt som standard, kan döljas i Markyta).
16. Modellkortet visar nu scentakets höjd över scengolvet, scengolv över mark, avvikelse mot standardvärdet 1,00 m, tak över mark och takets toppnivå. Höjdförstoring markeras uttryckligen som visuell terrängskala.

17. V2.0 / platskarta v1.1: tidigare, felaktigt tolkat försök med ändrad flankradläggning. Ersatt av v3.0 för det aktuella uppdraget.
18. V3.0/v4.1: originalets två yttre siktgränser roterades 5° inåt från sparade scenankare. Kvarvarande 2 163 stolar hade originalets lägen, ID och vinklar. Detta var rätt typ av ändring men fel startpunkt enligt senare detaljkontroll.
19. V4.0–v4.1: direkt alternativväxling med bibehållen översiktskamera, personvisning och markreglage. Verifierat 2 353↔2 163 renderade stolar, separata platsval och PDF-länkar till original/5°-underlag.
20. V4.2 / platskarta v1.4: gammal och ny yttergräns startar i scenens framhörn. Gammal gräns behåller tidigare fjärrpunkter; ny gräns är 5° snävare från samma hörn. B-modellen har 2 112 stolar (−241), A-modellen 2 353. PDF-länkar uppdaterade till v1.4. Exakt biljettplatsinmatning kvar: parkett, sektion, rad och stol.
21. V4.3 / platskarta v1.5: lade till C med 28 cm relativ förskjutning, samma 2 112 plats-ID som B och oförändrad kapacitet. Ersatte 32 cm plankorridor för huvudkontroll med geometriskt stråle–huvud-avstånd, lade till nio scenmål och länkade C-PDF. Vid 1,20 m öga/1,25 m huvud förbättrades fri scenmitt från 1 201 B-platser till 1 360 C-platser; fria strålar över nio scenmål ökade från 11 253 till 11 489 av 19 008. PDF sida 3 dokumenterar resultat, metod, tolkning och begränsningen i 1,50 m all-heads-testet.
---

## 9. Begränsningar och ansvar

- Skala ±5 % (fotokalibrering); orientering verifierad men inte inmätt på marken.
- DEM är **bar mark** — innehåller inte fyllnad, tält, scen eller temporära strukturer.
- Huvudprovet använder sfärisk radie 10,5 cm och samma valda huvudhöjd för alla personer. Kroppsrörelse, individuella längder, hattar och lutande personer modelleras inte.
- När samtliga huvuden sätts till 1,50 m förbättrar C inte totalresultatet jämfört med B. Radförskjutning är därför ett komplement, inte ersättning för vertikal siktprojektering.
- De nio scenmålen mäter punkter på samma höjd över scenbredden. De bevisar inte fri sikt till hela artisten, scenkant, dekor eller alla artistpositioner.
- **Höjdförstoring:** `1,0×` är verklig höjdskala. Högre värden förstorar endast terrängens visuella skillnader.
- **Detta är ett arbetsförslag/visualisering — inte den juridiska plats-, säkerhets- eller utsättningsritningen.** Måste kontrollmätas före utsättning/biljettimport.

## 10. Massor & kostnad — utkast

Appen har nu en andra vy, **Massor & kostnad**, som kan öppnas från toppmenyn.
Den räknar på den aktiva fyllnadsmodellen och uppdateras när sektioner, maxhöjder
eller prisantaganden ändras.

### 10.1 Volymmodell

- Volymen är endast **extra fyllnad ovanpå DEM**; aktuell modell schaktar aldrig bort mark.
- Varje 3 m DEM-cell vars centrum ligger i sektionens förenklade hull räknas som
  `cellarea × max(0, vald lyft × fyllnadsprogress)`.
- Volymen är därför en tidig jämförelsevolym, inte en massberäkning för bygghandling.
- Vikt räknas som `volym × densitet`; standardantagandet är 1,7 ton/m³.
- Schakt, bortforsling, geotextil, dränering, gångar, slänter, massbalans och
  förorenade massor ingår inte ännu.

### 10.2 Prisantaganden i första utkastet

Alla värden är redigerbara i appen och avser grova **exklusive-moms-antaganden**:

| Post | Startvärde |
|---|---:|
| Densitet fyllnad | 1,7 ton/m³ |
| Material | 150 kr/ton |
| Transport in | 250 kr/ton |
| Utbredning + packning | 320 kr/m³ |
| Underarbete/finplanering | 120 kr/m² |
| Etablering | 25 000 kr |
| Riskreserv | 15 % |

Detta ska läsas som ett diskussionsunderlag för södra Sverige, inte som
snittpris eller offert. Priset påverkas kraftigt av massornas kvalitet,
köravstånd, tipp-/lastningsmöjlighet, tillgänglighet, säsong och entreprenör.
Som externa orienteringspunkter anger prisguider ungefär 150–400 kr/m³ för
schaktning och 300–800 kr/ton för transport/deponi, medan materialleverantörer
ibland anger mycket lägre materialpris när det gäller enklare massor och
transport prissätts separat:

- [DittBygg — schaktning och markarbete](https://dittbygg.se/markarbete/gravning/)
- [BraByggare — markarbeten och prisfaktorer](https://www.brabyggare.se/info/markarbeten-kostnad-pris/)
- [KITS Recycling — fyllnadsmassor](https://kitscontractor.se/produkter/fyllnadsmassor/)

Nästa förbättring bör vara separata scenarier för **köpta massor**,
**återanvändning på plats** och **bortforsling/deponi**, samt indata för
transportavstånd och lastbilens lass. Prisvärdena bör uppdateras mot lokala
offerter innan de används i beslut.
