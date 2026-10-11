# Ny platskarta 2027 — förslag C med förskjutna rader v1.5

## Återuppta arbetet — sparat 2026-10-10
- Projektmapp: `/Users/philipwareborn/Documents/OMP/naturscen`.
- Läs detta dokument och `3d/BYGGLOGG.md` innan nästa ändring. Aktuell 3D-fil är `3d/naturscenen_3d_sikt_v4.3.html`.
- A: 2 353 originalstolar och gammal yttergräns från scenhörnen.
- B: 2 112 stolar innanför den 5° snävare yttergränsen från samma scenhörn.
- C: samma 2 112 platser som B, men intilliggande rader ligger 28 cm förskjutna relativt varandra.
- A/B bevarar v1.4-geometrin. Endast C flyttar stolar; rad- och plats-ID, stolavstånd 56 cm, radavstånd 92 cm och sektionsvinklar behålls.
- A/B/C-växling, exakt parkett/sektion/rad/stol-inmatning och separat plats-/sittvyminne är implementerade.
- 3D v4.3 testar huvuden geometriskt med 10,5 cm radie och redovisar fri sikt mot scenmitt samt fria mål över nio punkter på scenen.
- Behåll tidigare filer som historik. Nästa arbete ska utgå från v1.5/v4.3.

## Aktuell leverans
- `Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5.pdf`: förslag C, sida 1 ren karta, sida 2 fotokontroll och sida 3 dokumenterad siktanalys.
- `Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5.svg/.png`: ren C-karta med 2 112 förskjutna stolar.
- `Platskarta_Naturscen_2027_FORSKJUTNA_RADER_28CM_v1.5_FOTOKONTROLL.svg/.png`: samma C-geometri på drönarfotot.
- `Platskarta_Naturscen_2027_KAPACITET_FORSKJUTNA_RADER_28CM_v1.5.csv`: alla 2 353 original-ID med B- och C-koordinater, radförskjutning och status.
- `build_staggered_v1_5.py`: reproducerbar generator och geometrikontroll för v1.5/v4.3.
- `3d/naturscenen_3d_sikt_v4.3.html`: aktuell A/B/C-modell med separat platsminne, geometrisk huvudkontroll och nio scenmål.
- A/B-underlagen från v1.4 finns kvar oförändrade och länkas tillsammans med C-PDF:en från 3D v4.3.

## Rättelse av tidigare tolkning
V1.1, jämförelsedokument v1.2 och 3D v2 besvarade fel fråga: de ändrade radläggningen, inte de yttre siktgränserna från scenen. V1.3/v4.1 ändrade rätt typ av linje men använde originalets sparade linjeankare strax bakom scenfronten. V1.4/v4.2 korrigerar detta: både gammal och ny yttergräns startar i scenens framhörn.

## Geometri och räkneregel
- Scenens framhörn i SVG-pixlar är vänster `(637, 315,7)` och höger `(862, 315,7)`. De motsvarar SWEREF ungefär `E 472519, N 6399861` respektive `E 472501, N 6399861`.
- Svart gammal gräns behåller tidigare fjärrpunkter men startar i framhörnen: vänster `(637,315,7)→(154,70;930)`, höger `(862,315,7)→(1428,29;930)`.
- Röd ny gräns är exakt 5° snävare från samma framhörn.
- Vinkel från bildens lodlinje: vänster 38,130°→33,130°; höger 42,664°→37,664°.
- Vid `y=930` hamnar nya gränserna på `x=235,989389` respektive `x=1336,293438`.
- En stol behålls endast om hela den roterade symbolen (5,4×4,6 px) ligger mellan de nya gränserna. Samma regel används även för tredje parkett.
- Kvarvarande stolar flyttas, vrids eller packas inte om. Originalets rad- och plats-ID behålls. Helt borttagna rader och enstolsrader kan förekomma; detta är ren kapacitetseffekt av gränsen, inte en ny optimerad radplan.
- Scen, gångar, sektionskonturer, stolavstånd och radavstånd ändras inte. Gamla sektionskonturer visas för jämförelse; inga kvarvarande stolar ligger utanför nya gränserna.
- På ren karta: svart = gammal hörnförankrad gräns, röd streckad = ny 5° snävare gräns. På foto: samma färger. I 3D: ljus heldragen = gammal, röd streckad = ny. 3D-linjerna följer modellens markhöjd.
- Vänster/höger avser bilden med scenen uppåt.

## Förslag C — radförskjutning
- Normal stolcentrumdelning är 56 cm. C använder halva delningen, 28 cm, mellan intilliggande rader.
- Grundprincipen är nominellt −14/+14 cm längs respektive rads lokala riktning.
- Små sektionsvisa baskorrigeringar på högst 6,8 cm håller samtliga stolsymboler innanför den röda gränsen. Den relativa skillnaden mellan intilliggande rader är fortfarande 28 cm.
- Alla 2 112 B-platser behålls med samma sektion/rad/plats-ID. Stolavstånd, radavstånd, sektionsvinkel, scen, gångmarkeringar och siktgränser ändras inte.
- Generatorn underkänner leveransen om ett ID ändras, normal stolcentrumdelning avviker eller något hörn av en roterad stolsymbol hamnar utanför den röda gränsen.
- Förskjutningen förbättrar främst möjligheten att se en punkt mellan två huvuden i raden framför. Den ersätter inte vertikal siktprojektering och garanterar inte fri sikt över hela scenen.

## Kapacitetsjämförelse
| Sektion i bilden | Original A | B | C | B → C |
|---|---:|---:|---:|---:|
| 1:a parkett mitt | 364 | 364 | 364 | 0 |
| 1:a vänster | 146 | 106 | 106 | 0 |
| 1:a höger | 148 | 103 | 103 | 0 |
| 2:a parkett mitt | 390 | 390 | 390 | 0 |
| 2:a vänster | 279 | 248 | 248 | 0 |
| 2:a höger | 458 | 366 | 366 | 0 |
| 3:e parkett | 568 | 535 | 535 | 0 |
| **Totalt** | **2 353** | **2 112** | **2 112** | **0** |

## Kontroll
- Ren C-karta och C-fotokontroll innehåller samma 2 112 unika platser.
- Alla C-stolar behåller B:s ID, radavstånd, stolavstånd och sektionsvinkel.
- Alla fyra hörn på varje C-stol ligger innanför den röda 5°-gränsen.
- CSV innehåller 2 112 `kvar_forskjuten` och 241 `bort_siktgrans`.
- 3D v4.3 innehåller `original = 2353`, `inward = 2112`, `staggered = 2112`.
- Vid standardhöjder 1,20 m öga/1,25 m huvud gav 3D-modellen fri scenmitt för 1 201 B-platser och 1 360 C-platser, 56,9 % respektive 64,4 %.
- Över nio scenmål gav B 11 253 av 19 008 fria strålar och C 11 489, 59,2 % respektive 60,4 %.
- PDF har tre sidor inklusive siktanalysen; PNG/SVG har kontrollerats visuellt.

## Begränsningar
Fotoavlästa gränser och ungefärlig skala (12,5 px/m). Stolssymbolens plats är inte personers utrymmesbehov. C är en siktförbättrande planmodell, inte bevis på fri sikt. När alla modellerade huvuden höjs till 1,50 m förbättras inte totalresultatet; förskjutning ersätter därför inte höjdskillnad, lutning eller individuell kontroll från utsatta platser. Kapaciteten är ritad modellbeläggning, inte godkänd publik-, utrymnings- eller utsättningsplan.
