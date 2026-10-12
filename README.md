# Pobude meščanov – zajemi ČS Vič, Center in Šiška

## Repozitorij in lokalni zagon

GitHub: [container/ljubljanske-pobude](https://github.com/container/ljubljanske-pobude).
Repozitorij vsebuje skripte, analize, oblikovne reference in pripravljeno spletno stran v `deploy/site`.
Celotni zajemi v `data/vic_*`, `data/center_*` in `data/siska_*`, začasne datoteke ter izvozni arhivi ostanejo lokalno in so izključeni iz Gita. Spodnje povezave do zajemov zato delujejo le, če so te mape prisotne lokalno.

Za ogled pripravljene strani brez ponovnega zajema ali gradnje:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory deploy/site
```

Odpri `http://localhost:8000`. Ponovna gradnja s `scripts/deploy_site.sh` potrebuje lokalne zajeme; skript tudi objavi stran prek Railway CLI. Potisk v GitHub sam po sebi ni del tega skripta.

Zbirka javnih pobud s portala [pobude.ljubljana.si](https://pobude.ljubljana.si/).

Skripte podpirajo zajem za **Vič** (`--district vic`), **Center** (`--district center`) in **Šiško** (`--district siska`). Vključitev določa izključno spustni filter četrtne skupnosti na portalu, ob nastavitvah »Vse pobude« in obdobje »Vse«, na obeh seznamih. Vsak zajem je shranjen v svoji mapi; podatki ene četrti se ne združujejo s podatki druge.

## Šiška – zajem 9. oktobra 2026

Zajem v [data/siska_2026-10-09](data/siska_2026-10-09/README.md) vsebuje **7.331 pobud: 7.295 odgovorjenih in 36 neodgovorjenih**. Vse imajo koordinate. Najprej je bilo prenesenih in preverjenih **1.738 pobud z datumom prijave od vključno 9. oktobra 2023**, shranjenih tudi v [ločeni zbirki zadnjih treh let](data/siska_2026-10-09/zadnja_3_leta/README.md), nato še 5.593 starejših pobud. Prenos je potekal od najnovejših prijav proti najstarejšim, z obema statusoma v skupnem zaporedju. Seznama sta ob koncu ostala nespremenjena; omrežnih napak in napak razčlenjevanja ni. Zbirki sta lokalni, brez ZIP-a in brez objave na spletni strani.

## Center – zajem 1. oktobra 2026

Mapa: [data/center_2026-10-01](data/center_2026-10-01/). Imena izvozov se začnejo s `pobude_center`; struktura in pomen polj sta enaka kot pri Viču. Filter portala je **CENTER**, vrednost **11**. Končna števila, popolnost in čas prenosa so v `capture_report.json`, preverjanje nespremenjenosti seznamov v `source_list_verification.json`, primerjava izvozov pa v `validation_report.json`.

Zajem vsebuje **16.529 pobud: 16.479 odgovorjenih in 50 neodgovorjenih**. Vse imajo geografsko točko. Datumi prijav segajo od 9. decembra 2008 do 29. septembra 2026. Pri 3.346 pobudah je skupaj 4.912 povezav iz galerij prilog. Ponovna primerjava obeh seznamov je potrdila nespremenjen nabor, statuse, naslove in datume seznama. Omrežnih napak in napak razčlenjevanja ni.

Pri 2.991 pobudah trenutni šifrant ne vsebuje naziva kategorije; številčne šifre so ohranjene. Pobuda **55625, »Zahvala in pohvala«**, je na portalu označena kot odgovorjena, vendar njen blok odgovora vsebuje samo nedeljivi presledek. Prazno besedilo je ohranjeno brez dopolnjevanja. Zbirka ostane lokalno za nadaljnjo analizo; ZIP ni izdelan. Podrobnosti so v [dokumentaciji zajema za Center](data/center_2026-10-01/README.md).

## Vič – zajem 29. septembra 2026

Obseg določa izključno **spustni filter »VIČ«**, ob nastavitvah **»Vse pobude«** in **obdobje »Vse«**, na seznamih odgovorjenih in neodgovorjenih pobud. Prostorsko preverjanje, premeščanje med četrtnimi skupnostmi in iskanje pobud iz drugih četrti niso del tega zajema.

Zajem 29. septembra 2026 vsebuje **2.975 pobud: 2.952 odgovorjenih in 23 neodgovorjenih**. Vseh 2.975 ima geografsko točko. Datumi prijav segajo od 9. decembra 2008 do 27. septembra 2026. Pri 430 pobudah je skupaj 614 povezav iz galerij prilog. Naknadna ponovitev obeh filtriranih seznamov je potrdila nespremenjen nabor, statuse, naslove in datume seznama.

Pri 459 pobudah je ohranjena številčna šifra kategorije, ki je sedanji spustni meni ne vsebuje; njihovega naziva kategorije zato nismo ugibali. Vsebina teh pobud, odgovori in lokacije so zajeti.

## Datoteke

Zajem je v mapi [data/vic_2026-09-29](data/vic_2026-09-29/).

| Datoteka | Namen |
|---|---|
| `pobude_vic.json` | Celotna strukturirana zbirka, z besedili, HTML, datumi, koordinatami, kategorijami in povezavami do prilog. |
| `pobude_vic.jsonl` | Enak nabor, ena pobuda na vrstico, primeren za nadaljnjo strojno obdelavo. |
| `pobude_vic.sqlite` | Lokalna podatkovna baza; tabela `initiatives`, ena vrstica na pobudo. Celoten zapis je tudi v stolpcu `record_json`. |
| `pobude_vic.geojson` | Geografski izvoz; koordinate so v vrstnem redu **zemljepisna dolžina, zemljepisna širina**, WGS84. |
| `index.json` | Pobude in statusi iz obeh filtriranih seznamov portala. |
| `categories.json` | Šifrant vrst pobud, prebran iz spustnega menija portala. |
| `geometry.json` | Povezava ID-ja pobude z atributi in točko iz kartografskega servisa. |
| `capture_report.json` | Števila zapisov, čas zajema, manjkajoči podatki in morebitne napake. |
| `source_list_verification.json` | Primerjava seznamov pred in po zajemu. |
| `validation_report.json` | Končna primerjava izvozov, identifikatorjev, koordinat in kontrolnih vsot izvirnikov. |
| `checksums.sha256` | Kontrolne vsote vseh podatkovnih datotek. |
| `raw/details/<ID>.txt` | Izvirni besedilni odgovor strani za posamezno pobudo; ohranjen pred razčlenjevanjem. |
| `raw/*_list.txt` | Izvirna filtrirana seznama. |
| `raw/geometry_*.json` | Izvirni odgovori kartografskega servisa v paketih do 200 ID-jev. |
| `raw/*_page.html` | Posnetka strani, vključno s šifranti in nastavitvami obrazca. |

## Pomen pomembnih polj

- `id`: identifikator pobude na portalu. Povezuje sezname, podrobnosti in kartografski zapis `MOL_VNESENE_POBUDE_FC_ID`. ArcGIS `OBJECTID` je ločen identifikator in ni uporabljen kot ključ pobude.
- `portal_status`: `odgovorjena` ali `neodgovorjena`. **To ni ocena razrešenosti problema.**
- `district`: četrtna skupnost iz podrobnosti pobude. Vključitev v zbirko določa filter seznama.
- `reported_date`, `published_date`, `last_response_date`: datum prijave, objave in zadnjega objavljenega odgovora, zapisani kot `YYYY-MM-DD`. Izvorni datumski nizi so ohranjeni v poljih s pripono `_raw`.
- `list_date`: datum iz seznama. Njegov pomen je odvisen od seznama; ne uporablja se samodejno kot datum prijave.
- `initiative_text`, `response_text`: očiščeni besedili. Celotna razpoložljiva vsebina odgovora je ohranjena tudi kot `responses_html`, vključno z morebitnimi dodatnimi odgovori v istem bloku.
- `respondents_text`: besedilo portala o pripravljavcu odgovora oziroma obravnavi. To ne dokazuje, kdo mora izvesti ukrep.
- `category_id`, `category`: kategorija iz kartografskega zapisa in njen naziv iz šifranta portala. Neznane šifre ostanejo ohranjene, naziv pa je prazen.
- `geometry_wgs84`: koordinati, ki ju vrne kartografski servis z `outSR=4326`. Točka ni bila prestavljena ali uporabljena za preverjanje pripadnosti četrtni skupnosti.
- `source_x`, `source_y`: izvorni koordinati iz podrobnosti, brez pretvorbe; nista zemljepisna dolžina in širina.
- `gis_attributes`: izbrani atributi kartografskega servisa, vključno z izvornimi datumi. Njihova interna polja se ne interpretirajo kot dokaz izvedbe.
- `attachment_links`: povezave do slik in prilog iz obeh galerij. Slike in druge binarne priloge **niso prenesene**; zajeti so njihovi URL-ji in izvorni HTML galerij.
- `source_page`, `source_callback_argument`: izvorna stran in parameter, s katerim portal pridobi pobudo. Sam URL strani ne odpre nujno izbrane pobude.
- `captured_at`, `raw_detail_path`, `raw_sha256`: čas prenosa posameznega izvirnika, njegova pot in kontrolna vsota UTF-8 besedila.

## Omejitve zajema

Zajem ohranja javno vsebino, ki jo portal vrne v trenutku prenosa. Ne predstavlja zgodovine vseh prejšnjih različic odgovorov ali dokazila o izvedbi. `last_response_date` ni nujno datum prvega odgovora. Pobude z več odgovori v enem bloku še niso razdeljene na ločene dogodke; izvorni blok je shranjen v celoti.

V tej fazi ni izvedena tematska analiza, povezovanje podobnih pobud, ocenjevanje obljub ali preverjanje rešitev. Manjkajoče vrednosti se ne nadomeščajo z ugibanjem.

## Ponovitev zajema

Skript uporablja Pythonovo standardno knjižnico in običajne javne bralne zahtevke portala. Pridobi ASP.NET stanje obrazca, preveri izbrano možnost (`VIČ` z vrednostjo `15`, `CENTER` z vrednostjo `11` ali `ŠIŠKA` z vrednostjo `8`), prenese oba seznama, geografske podatke poveže samo z ID-ji iz teh seznamov in zaporedno pridobi podrobnosti. Izvorne odzive razčleni kot podatke; JavaScripta iz odgovorov ne izvaja.

```sh
python3 scripts/capture_pobude.py --district vic --folder data/vic_NOV_DATUM
python3 scripts/capture_pobude.py --district center --folder data/center_NOV_DATUM
```

Za nov posnetek uporabi novo mapo. Ponovitev v isti mapi je namenjena **nadaljevanju prekinjenega zajema**: že shranjenih podrobnosti ne prenese znova, razen če se je pripadajoča vrstica seznama (status, naslov ali datum) spremenila. To ni popolna osvežitev vseh podrobnosti; za nov posnetek vseh besedil je potrebna nova mapa.

Po zaključenem zajemu ponovno preveri oba seznama in preveri lokalno zbirko (primer za Center):

```sh
python3 scripts/verify_source_lists.py --folder data/center_2026-10-01
python3 scripts/package_capture.py --folder data/center_2026-10-01 --validate-only
```

Preverjanje prebere četrt iz `capture_config.json`. Možnost `--validate-only` pripravi poročilo in kontrolne vsote brez ZIP-a; zbirka za Center ostane lokalno za nadaljnjo analizo. Brez te možnosti skript dodatno izdela ZIP v `outputs/pobude_<ime_mape>.zip`.

Za ponovno razčlenitev in izvoz obstoječega zajema brez omrežnih zahtevkov:

```sh
python3 scripts/capture_pobude.py --folder data/vic_2026-09-29 --export-only
python3 scripts/capture_pobude.py --district center --folder data/center_2026-10-01 --export-only
```

Skript po vsakih 100 pobudah izpiše napredek, ob začasni omrežni napaki poskusi ponovno, končno popolnost pa zabeleži v `capture_report.json`. Morebitni izpuščeni ali nerazčlenljivi zapisi se izrecno navedejo kot napake.

Podpora za Šiško: `--district siska`, filter **ŠIŠKA (8)**. Novi prenosi podrobnosti združijo oba statusa in potekajo od najnovejšega vnosa proti najstarejšemu po `DATUM_VNOSA` iz GIS, ne po datumu odgovora na seznamu. Zapisi brez tega datuma pridejo na konec in so navedeni v `capture_order.json`. Pri nadaljevanju se že shranjene podrobnosti uporabijo ponovno. Izvozi JSON, JSONL in GeoJSON so urejeni po dejanskem `reported_date` padajoče, pri istem datumu po ID-ju padajoče; v SQLite vrstni red določi poizvedba (`ORDER BY reported_date DESC, id DESC`).

Za prednostni prenos zadnjih treh let ob zajemu 9. oktobra 2026:

```sh
python3 scripts/capture_pobude.py --district siska --folder data/siska_2026-10-09 --priority-since 2023-10-09
```

Pred prenosom starejših podrobnosti skript izvozi in preveri obdobje od vključno navedenega datuma v podmapi `zadnja_3_leta`. Njen `index.json` vsebuje samo izbrano obdobje, `full_source_index.json` pa celotna izvorna seznama za preverjanje nespremenjenosti vira. Obseg je izrecno zapisan v `capture_scope.json`. Začetni izbor uporablja datum vnosa GIS; izvožene datume prijave preveri tudi v podrobnostih. Če datum GIS manjka, se prednostni zajem ustavi, da ne bi tiho izpustil pobude. Po preverjanju prednostnega obdobja se nadaljuje prenos starejših pobud in končni izvoz celotne četrti v glavno mapo.
