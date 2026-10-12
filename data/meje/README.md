# Meje četrtnih skupnosti

Od 1. oktobra 2026 uporabljamo sloj [Četrtne skupnosti, MOL, register ulic – MapServer/31](https://pobude.ljubljana.si/arcgis/rest/services/mol_ulice/ulice_mol_interni/MapServer/31). Izvorne koordinate so v D96/TM (EPSG:3794); servis vrne geografski izvoz WGS84 z `outSR=4326`.

`cetrtne_skupnosti.json` vsebuje vseh 17 četrti, `vic.json` pa isti zapis za Vič. Skript `scripts/fetch_district_boundaries.py` prenese sloj, preveri število četrti in zaprte obroče ter shrani metapodatke, oba koordinatna izvoza in kontrolne vsote zahtevkov v `boundary_source.json` ter `raw/`.

Prejšnji sloj `MolPobudeSQL_L/MolCetrtneSkupnosti/MapServer/0` je shranjen kot `raw/legacy_pobude_cetrtne_skupnosti_4326.json`. V primerjavi s slojem registra ulic sta bili meji Viča in Centra zamaknjeni proti severozahodu. Na prvem ujemajočem se oglišču znaša popravek za Vič 26,10 m proti vzhodu in 64,67 m proti jugu, za Center pa 26,41 m proti vzhodu in 64,46 m proti jugu. Zamenjana je celotna geometrija iz uradnega vira; stari meji nista premaknjeni za ročno izbrano konstanto.

Pretvorbo vseh 11.764 oglišč novega sloja smo neodvisno preverili s PROJ/pyproj iz EPSG:3794 v EPSG:4326. Največje odstopanje od geografskega izvoza MOL je bilo 0,000105 m. Vizualna primerjava z OpenStreetMap pri Viču potrjuje potek ob Gradaščici, Barjanski in Aškerčevi.

`scripts/build_site.py` za obe četrti vedno vzame mejo iz skupnega sloja, tudi kadar podatki tem vsebujejo starejši predpomnjen obris. Zajem pobud in njihova pripadnost po filtru portala sta ločena od tega sloja. Koordinate pobud ter vsebinske oznake se s popravkom meja ne premikajo.

Datoteke ulic, cest in zelenih površin v tej mapi niso del popravka meja.

Ponovljeno geometrijsko preverjanje zajema Viča daje 143 točk zunaj nove meje: 91 iz obdobja pred 29. 9. 2023 in 52 novejših. Posodobljen je izračun `analysis/oznacevanje/cetrt_po_tocki.json`; prejšnji izračun je ohranjen v `cetrt_po_tocki_prejsnja_meja.json`. Točke in vsebinske oznake ostajajo izvorne. Geometrijska pripadnost točke sama po sebi ne dokazuje lokacije problema v besedilu pobude.
