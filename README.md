# Ljubljanske pobude

Zajemi javnega portala [Pobude meščanov MOL](https://pobude.ljubljana.si/), analize odgovorov in spletna aplikacija za pregled po četrtih. Namen je prepoznati ponavljajoče se probleme ter razlikovati med odgovorom, obljubo in navedbo izvedbe.

Repozitorij: [container/ljubljanske-pobude](https://github.com/container/ljubljanske-pobude). Ta README opisuje stanje predaje po pospravljanju **17. oktobra 2026**. Datumi v podatkih so datumi posameznih zajemov, ne datum zadnje spremembe projekta.

## Najprej: ogled ali nadaljevanje analize

Za ogled že pripravljene aplikacije potrebuješ Python 3, brez ponovnega zajema ali gradnje. Ukaze izvajaj iz glavne mape projekta:

```sh
python3 -m http.server 8000 --bind 127.0.0.1 --directory app
```

Odpri `http://localhost:8000/?cetrt=vic`. Spletni prikaz uporablja Leaflet iz CDN, podlago OpenStreetMap in zunanje povezave do prilog, zato za celoten prikaz potrebuje internet. Podatki pobud in pisave so v projektu.

Za nadaljevanje vsebinske analize so na voljo **48.160 zapisov po desetih četrtih** v `app/d/`, skupaj z obstoječimi oznakami in poročili v `analysis/`. Za nov zajem uporabi spodnji postopek; zajem lahko začne iz prazne mape.

## Kaj je kje

| Mapa | Vsebina in namen |
|---|---|
| `app/` | Pripravljena aplikacija, njeni podatki, pisave in nastavitve gostovanja. Prej `deploy/site/`. |
| `app/source/` | Izvorna koda strani (`template.html`), razlaga »O strani« (`o_strani.html`) in skupni slogi zemljevida (`leaflet.css`). Prej `analysis/site/` in `analysis/teme/leaflet.css`. |
| `app/d/` | Izvozi za aplikacijo: besedila, točke, statistike, oznake in potrjene skupine problemov. |
| `data/` | Register za gradnjo in geografski podatki. Sem skripta privzeto shranjuje nove izvorne zajeme. |
| `analysis/` | Analitične oznake, navodila, poročila, podatki za prikaze in orodja za pregled analiz. |
| `scripts/` | Skripte za zajem, preverjanje, analizo, gradnjo in objavo; pregled je spodaj. |
| `design-library/` | Samostojna oblikovna referenca CILJ: barve, pisave, ikone, slogi in izvorni posnetki. |
| `outputs/` | Ohranjeni izvorni zajemi in gradivo za plakat v `images/`. Prej sta bila izvoza v `output/` in `outputs/`. |
| `tmp/` | Poskusi, stare enkratne skripte, dnevniki, slikovni izrezi in velike vmesne primerjave. Izključeno iz Gita in predaje. |

### Izvorna koda in sestavljena aplikacija

`app/source/template.html` je glavna izvorna koda aplikacije, čeprav se imenuje »template«. Skripta `build_site.py` vanjo vstavi razlago strani, register, pisave in sloge ter izdela `app/index.html`. Trajne spremembe strani naredi v `app/source/`, saj ponovna gradnja prepiše `app/index.html`.

`Dockerfile` in `Caddyfile` v `app/` sta del obstoječega načina gostovanja na Railway. Dockerfile v spletni strežnik kopira samo pripravljeno stran, register, `d/` in pisave. `design-library/` je vzporedna referenca; gradnja iz nje prebere pisave.

### Dva registra četrti

- `data/cetrti.json`: vhod za gradnjo; vsebuje ID, ime, portalno oznako, pot `mapa` do izvornega zajema, referenčni datum in nastavitve analiz. Register in `data/meje/` sta bila obnovljena iz zadnjega commita, brez spreminjanja vsebine.
- `app/cetrti.json`: pripravljeni register za spletni prikaz; vsebuje ID, ime, mejo in število paketov besedil `n_tx`. Nastane med gradnjo in ne nadomešča vhodnega registra.

## Podatki: kaj je dejansko ohranjeno

| Četrt | Zapisov v aplikaciji |
|---|---:|
| Vič | 2.975 |
| Center | 16.529 |
| Šiška | 7.331 |
| Golovec | 1.243 |
| Bežigrad | 7.349 |
| Moste | 2.507 |
| Rudnik | 2.774 |
| Jarše | 2.307 |
| Trnovo | 2.637 |
| Rožnik | 2.508 |
| **Skupaj** | **48.160** |

Pri vsaki četrti se število zapisov v paketih besedil ujema s skupnim številom v `STAT.skupaj`. To je vsota po četrtih, ne štetje različnih oseb ali problemov. Obseg vsebinskega označevanja je ožji od celotnega zajema.

Celotni zgodovinski izvorni zajemi v poteh `data/<četrt>_<datum>` so manjkali že pred pospravljanjem in niso bili vključeni v Git. Ohranjeno je:

- **Celoten izvorni Vič:** `outputs/pobude_vic_2026-09-29.zip`, 2.975 pobud, izvirni odzivi portala, izvozi in poročila. Arhiv vsebuje mapo `data/vic_2026-09-29/`. Dokumentacija in kopije skript v ZIP-u so zgodovinski; za trenutno delo uporabi skripte iz korena tega repozitorija.
- **Delni izvorni Golovec:** `outputs/golovec_2026-10-12_prekinjeni_celotni_zajem/`, 822 odzivov v `raw/details/`, seznam 1.243 pobud in geografski podatki. To je prekinjen zajem brez končne validacije, ne popolna zbirka. Datoteka `index.json` je seznam pobud, ne spletna stran.
- **Obdelani podatki vseh četrti:** `app/d/`. Vsebujejo besedila in odgovore, vendar ne vseh prvotnih HTML-odzivov, atributov in dokazil zajema.
- **Analitični vzorci in oznake:** `analysis/`; na primer `vic_pilot/sample_100.json` vsebuje 100 strukturiranih izvornih zapisov Viča.

Nov zajem je ponovljiv z obstoječimi skriptami. Za ponovno izdelavo istih zgodovinskih rezultatov pa potrebuješ iste izvorne posnetke in oznake. Nov prenos portala ustvari nov posnetek, saj se odgovori in seznami sčasoma spreminjajo. Podatkov iz `app/d/` ne predstavljaj kot popolnega izvornega arhiva.

### Kako brati `app/d/`

- `app/d/<četrt>.json`: `meta` opisuje četrt in obdobja; `D.tocke` in `D.stare` vsebujeta točke z ID-jem, naslovom, datumom in razpoložljivimi oznakami; `STAT` statistike; `CLUSTERS` potrjene skupine; `cluster_info` podatke o njihovem pregledu. Seznam točk ni pri vseh četrtih popoln indeks vseh besedil.
- `app/d/<četrt>/tx/<n>.json`: objekti, katerih ključi so ID-ji pobud kot nizi. Vrednost vsebuje `pobuda`, `odgovor`, `odgovor_datum`, `odgovoril`, `lat`, `lon`, `portal`, `priloge` in po potrebi `oznake`. Za vse zapise preberi vse pakete, ne samo točk na zemljevidu.
- Paket posamezne pobude določa `int(id) % n_tx`; `n_tx` preberi iz registra oziroma `meta`, saj se razlikuje po četrtih. Podatke poveži po ID-ju in ohrani podatek o izvorni četrti.
- `portal` in `oznake` sta seznama parov `[ime, vrednost]`. `portal` vsebuje podatke portala, `oznake` pa interpretacije analize. Polja niso pri vseh zapisih enaka. Naslovi so v datoteki četrti, ne v paketih besedil.
- `app/d/vse.json`: skupni prikaz potrjenih skupin problemov po četrtih.

Koordinate besedil so WGS84 (`lat` širina, `lon` dolžina). Točke uporabljajo `la` in `lo`; meje v registru uporabljajo vrstni red Leaflet `[širina, dolžina]`. Izvorni GeoJSON uporablja `[dolžina, širina]`. Datumi so praviloma `YYYY-MM-DD`, manjkajoče vrednosti ostanejo prazne ali `null`.

## Analize in njihove omejitve

| Pot | Kaj bereš oziroma nadaljuješ |
|---|---|
| `analysis/oznacevanje/` | Vič: oznake 544 pobud zadnjih treh let, kalibracija 50 pobud, vhodni paketi, izhodi in pregledovalniki. Pravila: [navodila za označevanje](analysis/oznacevanje/navodila_oznacevanja.md). |
| `analysis/teme/` | Podrobne teme Viča, tematske oznake in zemljevid. Pravila: [navodila za teme](analysis/teme/navodila_teme.md). `karta_template.html` in `o_strani.html` izdelata ločen prikaz `perece_teme_vic.html`; ta ni glavni `app/index.html`. |
| `analysis/cetrti/<četrt>/` | Statistike, razpoložljive oznake vrste in stanja, paketi za označevanje ter skupine ponovitev. Pravila vrste/stanja so v `oznacevanje/navodila_vrsta_stanje.md`, kjer je ta podmapa prisotna. |
| `analysis/cetrti/<četrt>/clusters/` | `selection.json`: potrjene skupine in kontrolne vsote pregledanih zapisov; `review.json`: poročilo o pregledu; `candidate_index.txt`: kratek seznam kandidatov; `seed_type_overrides.json`: popravki izhodiščnih vrst. Kandidat sam po sebi še ni potrjena skupina. |
| `analysis/clusters_100m_2026-10-12/` | Potrjeni izbor skupin Viča in poročilo; glavna gradnja za Vič uporabi ta izbor, kadar nima četrtnega izbora. |
| `analysis/vic_pilot/` | Predhodna raziskava 100 namensko izbranih pobud; ni reprezentativen vzorec. |
| `analysis/zupan_vic/` | Izbor 144 pobud z odgovori, neposredno (138) ali posredno (6) pripisanimi županu, z dokaznimi izseki in HTML-pregledom. |
| `analysis/viri/` | CPS MOL 2025–2032 in Climate City Contract / 2030 Climate Neutrality Action Plan, skupaj z besedilnimi izvlečki. `cps-2017.txt` je samo izvleček starejše strategije; pripadajoči PDF ni ohranjen. Navedke preveri v PDF-ju, kadar je na voljo. |

`pregled_template.html` / `pregled_50.html` in `zadeve_template.html` / `zadeve_vic.html` so pripomočki za pregled analiz, zato ostajajo pri označevanju. Veliki `candidates.json` in pomožni `record_hashes.json` so prestavljeni v `tmp/analysis/cetrti/<četrt>/clusters/`. Ponovna priprava jih znova ustvari pod `analysis/`, vendar sta imeni izključeni iz Gita. Potrjenih izbir, poročil in dokaznih izsekov nismo odstranili.

**Interpretacija:** status »odgovorjena« ne pomeni, da je problem rešen. S0 pomeni brez odgovora; S1–S6 opisujejo zavrnitev, napotitev, različne stopnje zaveze in navedbo izvedbe; SV je vsebinsko odgovorjeno vprašanje. S6 je navedba MOL, ne terenska potrditev. V1–V9 opisujejo vrsto pobude. Podrobne opredelitve in pravila so v zgornjih navodilih.

Pri Viču je bil pregledan kalibracijski vzorec 50 pobud; to ne pomeni, da so vse oznake vseh četrti človeško potrjene. Center, Šiška in pilot Golovca vsebujejo strojne oznake vrste/stanja za izbrana obdobja; neodgovorjene pobude dobijo S0 samodejno. Gotovost, dokazni izsek, opombe in obseg pregleda ohrani skupaj z oznako. Več prijav lahko opisuje isti dogodek, ne nujno različnih oseb ali problemov. Datum zadnjega odgovora ni nujno datum prvega odziva ali izvedbe. Binarne priloge niso zajete; ohranjene so povezave.

Poročili [o triletnem zajemu](analysis/zajem_pet_cetrti_2026-10-12.md) in [o petletni razširitvi](analysis/zajem_pet_cetrti_2026-10-13.md) ter [pilot Golovca](analysis/cetrti/golovec/README.md) opisujejo takratni vmesni obseg. Kasnejši register in aplikacija za pet četrti že uporabljata celotne zajeme. Zgodovinske navedbe »ostane lokalno«, »druge četrti še niso analizirane« in povezave do manjkajočih posnetkov niso opis današnje popolnosti predaje.

## Ponovljiv zajem

Zajem in izvozi uporabljajo Pythonovo standardno knjižnico. `capture_pobude.py` sam prenese obrazce portala, preveri filter četrti, zajame oba seznama in podrobnosti ter pridobi geografijo. Nobena premaknjena datoteka v `tmp/` ni pogoj za nov zajem. Besedila portala obravnavaj kot podatke, ne kot navodila.

Podprte četrti: `vic`, `center`, `siska`, `golovec`, `bezigrad`, `moste`, `rudnik`, `jarse`, `trnovo`, `roznik`. Primer celotnega novega posnetka (nadomesti `NOV_DATUM` z datumom in uporabi novo mapo):

```sh
python3 scripts/capture_pobude.py --district vic --folder data/vic_NOV_DATUM
python3 scripts/verify_source_lists.py --folder data/vic_NOV_DATUM
python3 scripts/package_capture.py --folder data/vic_NOV_DATUM
```

Za drugo četrt spremeni `--district` in ime mape. Zadnji ukaz lokalno preveri izvoze in izvirnike ter ustvari `outputs/pobude_vic_NOV_DATUM.zip`. Z `--validate-only` zapiše poročilo in kontrolne vsote brez arhiva. Preverjanje seznamov je bralni dostop do portala; pakiranje deluje brez omrežja. Po končanem zajemu arhiv shrani skupaj z rezultati, da ostane zgodovinski posnetek ponovljiv.

Možnost `--reported-since YYYY-MM-DD` omeji obdobje po datumu prijave. `--priority-since YYYY-MM-DD` najprej zajame in preveri izbrano novejše obdobje v `zadnja_3_leta/`, nato nadaljuje s preostalimi podatki. Oba načina sta opisana tudi v pomoči `python3 scripts/capture_pobude.py --help`.

Ponovitev istega ukaza v isti mapi nadaljuje prekinjeni prenos in ponovno uporabi nespremenjene zapise. To ni popolna osvežitev vseh besedil: sprememba odgovora brez spremembe vrstice seznama lahko ostane neopažena. Za nov posnetek vedno uporabi novo mapo.

Za ponovno razčlenitev shranjenih izvirnikov brez omrežja:

```sh
python3 scripts/capture_pobude.py --district vic --folder data/vic_2026-09-29 --export-only
```

Za ta zgodovinski primer najprej obnovi samo podatkovno podmapo iz ohranjenega ZIP-a, ne zgodovinskih kopij skript:

```sh
unzip outputs/pobude_vic_2026-09-29.zip 'data/*'
```

Čas `captured_at` se pri izvozu bere iz časa spremembe datoteke izvirnika; razpakiranje lahko ta čas spremeni. Vsebina, izvorni datumi in kontrolne vsote izvirnikov se lahko preverijo neodvisno od tega. Ne preverjaj starih seznamov proti današnjemu portalu kot dokaz, da so bili nespremenjeni ob prvotnem zajemu; uporabi takrat shranjena poročila.

### Datoteke izvornega zajema

| Datoteka | Pomen |
|---|---|
| `capture_config.json` | Identifikator in filter četrti; pri najstarejšem Viču lahko manjka, takrat orodja privzeto uporabijo Vič. |
| `pobude_<četrt>.json`, `.jsonl`, `.sqlite`, `.geojson` | Isti nabor v štirih oblikah. SQLite tabela `initiatives` vsebuje tudi celoten `record_json`. |
| `index.json`, `categories.json`, `geometry.json` | Izvorni seznam pobud, šifrant kategorij in povezava ID-ja z geografijo. |
| `raw/details/<ID>.txt`, `raw/*_list.txt`, `raw/*_page.html`, `raw/geometry_*.json` | Shranjeni odzivi portala pred obdelavo. |
| `capture_report.json` | Obseg, datumi, statusi in napake zajema. |
| `source_list_verification.json` | Primerjava seznamov pred in po zajemu. |
| `validation_report.json`, `checksums.sha256` | Ujemanje izvozov in kontrolne vsote. |
| `capture_scope.json`, `full_source_index.json` | Pri omejenem obdobju opredelitev izbora in celotni seznam za preverjanje. |

V izvornih zapisih `id` povezuje portal, seznam in geografijo (`MOL_VNESENE_POBUDE_FC_ID`); ArcGIS `OBJECTID` je drug ključ. `initiative_text` in `response_text` sta očiščeni besedili; izvorni HTML je ohranjen posebej. `reported_date`, `published_date`, `last_response_date` pomenijo prijavo, objavo in zadnji odgovor; `list_date` je ločen datum seznama. Neznane kategorije ostanejo brez naziva, z ohranjeno šifro. `geometry_wgs84` je geografija vira; `source_x` in `source_y` sta izvorni koordinati, ne nujno dolžina in širina. `raw_detail_path` in `raw_sha256` povezujeta zapis z izvirnikom. Filter portala določa vključitev v četrt; geometrijski pregled točke je ločena analiza.

Znane posebnosti prvotnih zajemov: pri Viču je imelo 459 pobud številčno kategorijo brez znanega naziva; pri Centru 2.991. Nazivov ne dopolnjuj z ugibanjem. Center ID 55625 (»Zahvala in pohvala«) je bil označen kot odgovorjen, a je blok odgovora vseboval samo nedeljivi presledek; praznina je ohranjena. Ta števila opisujejo prvotne posnetke, ne novega zajema.

## Skripte: vhodi in izhodi

Večina skript uporablja samo standardno knjižnico. Številne imajo poti do starega Vičevega posnetka zapisane neposredno; pred prilagoditvijo drugemu posnetku preveri vhode v kodi. Skripte, ki pišejo rezultate, lahko prepišejo obstoječe izvoze; samo pregled aplikacije ničesar ne gradi ali objavlja.

| Skripta v `scripts/` | Namen, vhod → izhod |
|---|---|
| `capture_pobude.py` | Portal in filter četrti → nova mapa z izvirniki, štirimi izvozi in poročilom; `--export-only` uporabi shranjene izvirnike. |
| `verify_source_lists.py` | Shranjeni seznam + nov bralni dostop do portala → poročilo o razlikah in kopiji novih seznamov. |
| `package_capture.py` | Izvozi, izvirniki in preverjanje seznamov → validacija, kontrolne vsote, po izbiri ZIP v `outputs/`. |
| `check_capture_siska.py` | Živi portal → nov testni vzorec 20 odgovorjenih in 10 neodgovorjenih; preveri sezname, razčlenjevanje, geografijo in izvoze. |
| `fetch_district_boundaries.py` | Sloj MOL registra ulic → meje vseh 17 četrti in metapodatki v `data/meje/`; ne prenese drugih slojev ulic, cest in zelenih površin. |
| `check_district.py` | Izvorni Vič + meje → `analysis/oznacevanje/cetrt_po_tocki.json`. |
| `prepare_analysis_sample.py` | Izvorni Vič → namenski vzorec 100 pobud in opis metode v `analysis/vic_pilot/`. |
| `prepare_calibration_50.py` | Izvorni Vič → `kalibracija_50_vir.json`. Ročni predlogi/popravljene oznake so ločen vhod. |
| `build_review_page.py` | Kalibracijski vir, predlog oznak in predloga → `pregled_50.html`; ne potrebuje celotnega zajema. |
| `prepare_label_batches.py` | Izvorni Vič in izbor kalibracije → paketi za označevanje drugih pobud zadnjih treh let. |
| `merge_labels.py` | Izvorni Vič, oznake paketov in pregledana kalibracija → `oznake_544.json` z dodatnimi izračuni. |
| `prepare_vrsta_stanje.py` | Register, zajem četrti in `--years` → paketi odgovorjenih ter samodejni S0 v `analysis/cetrti/<četrt>/oznacevanje/`. |
| `siska_labels.py`, `golovec_labels.py` | Obstoječi paket + odločitve na standardnem vhodu → preverjena datoteka `paket_NN_oznake.json`; način `read` samo prikaže paket. |
| `merge_vrsta_stanje.py` | Paketi z oznakami in samodejni S0 → združene `oznake_vrsta_stanje.json` z izpisom morebitnih težav. |
| `cluster_cases.py` | Izvorni Vič in podrobne oznake → zgodnejši izbor zadev `analysis/oznacevanje/zadeve.json`. |
| `build_cases_page.py` | Zadeve, oznake, izvorni Vič in predloga → `zadeve_vic.html`. |
| `prepare_repeat_candidates.py` | Register, zajem, oznake, `--cutoff` → kandidati primerjav v radiju 100 m, pomožne vsote in indeks. Potrditev skupin je ločen pregled. |
| `check_repeat_clusters.py` | Register, izvorni zajem, oznake in potrjene skupine → preverjanje ID-jev, vsebinskih kontrolnih vsot in prostorskega pravila; ne potrebuje velikih `candidates.json`. |
| `write_vic_clusters_report.py` | Izvorni Vič, oznake in potrjen izbor 100 m → `analysis/clusters_100m_2026-10-12/clusters.md`. |
| `build_theme_map_data.py` | Izvorni Vič, podrobne oznake, izhodi tem in geografski sloji → `teme_oznake.json` in `karta_podatki.json`. |
| `build_stats.py` | Register, zajem četrti in razpoložljive oznake → `analysis/cetrti/<četrt>/statistika.json`. |
| `build_theme_map.py` | Izvorni Vič, tematski podatki/statistika, predloga v `analysis/teme/` in skupni CSS → ločen `perece_teme_vic.html`; uporablja shranjeni `analysis/teme/statistika.json`, ki ga `build_stats.py` ne prepiše. |
| `build_site.py` | Register, vsi registrirani zajemi, statistike, analize, meje, `app/source/` in oblikovne pisave → `app/index.html`, `app/cetrti.json`, `app/d/` in `app/fonts/`. |
| `fetch_tiles.py` | Oznake Viča in strežnik CARTO → izbirni prenos podlage v `analysis/teme/tiles/`; trenutna glavna aplikacija uporablja spletni OpenStreetMap. |
| `deploy_site.sh` | Obnovi tematske podatke, statistike in aplikacijo, nato jo pošlje v že določeno storitev Railway. To je objava, ne ukaz za lokalni ogled. |

Pomočnika za oznake uporabi na primer z `python3 scripts/siska_labels.py read 1`. Za pisanje: `python3 scripts/siska_labels.py write 1 < odlocitve.txt`; vrstica je `ID V1 S5|dobesedni dokaz|neobvezna opomba`. Preverita celoten nabor ID-jev paketa, šifre, dobesednost in dolžino dokaza do 25 besed, nato prepišeta izhod oznak. Neodgovorjene pobude S0 pripravlja ločena skripta.

## Ponovna gradnja obstoječe aplikacije

Gradnja zahteva vse mape, na katere kaže `data/cetrti.json`, ter spremljajoče analize in geografske sloje. V trenutni predaji celotni zgodovinski zajemi drugih četrti niso ohranjeni, zato celotna ponovna gradnja sedanjega posnetka še ni mogoča. To ne preprečuje novega zajema ali uporabe pripravljene aplikacije. Register in meje sami niso nadomestilo za zajeme.

Ko so ustrezni izvorni zajemi na voljo, je običajni vrstni red:

1. Za spremenjen posnetek pripravi oziroma preveri oznake in ponovno preglej skupine. Spremenjeno besedilo razveljavi prejšnjo potrjeno kontrolno vsoto; oznak ne razglasi samodejno za veljavne za nove odgovore.
2. `python3 scripts/build_theme_map_data.py` za Vič.
3. `python3 scripts/build_stats.py --district <četrt>` za vsako četrt registra.
4. `python3 scripts/build_site.py` za sestavo aplikacije brez objave.

Pri novem posnetku spremeni ustrezno pot `mapa` in datume v vhodnem registru; zajem registra ne spremeni samodejno. Ne shranjuj novega zajema pod datumom starega in ne zamenjaj `data/cetrti.json` z različico iz `app/`. Skripta za gradnjo počisti stare generirane podatke, zato jo uporabi šele s popolnimi vhodi. Za čisti ogled uporabi lokalni strežnik na začetku README.

## Preverjeno po pospravljanju

- Vseh 145 prvotnih datotek aplikacije je po premiku `deploy/site/` → `app/` vsebinsko nespremenjenih. Preverjeni so lokalno streženje, podatki četrti in števila zapisov v vseh paketih.
- Iz shranjenih izvirnikov Viča je bilo z aktualno skripto ponovno izdelanih vseh **2.975 zapisov**. Polja se ujemajo s prvotnim izvozom, razen časa `captured_at`, ki je vezan na čas spremembe razpakiranih datotek. Preverjeni so izvozi JSON/JSONL/SQLite/GeoJSON in kontrolne vsote izvirnikov.
- Živi test je uspešno zajel **30 pobud Šiške**, preveril nespremenjenost obeh seznamov med prenosom in vse izvoze. To je omejen preizkus postopka, ne ponovni celotni zajem vseh desetih četrti.

Preizkus lahko ponoviš z novo mapo:

```sh
python3 scripts/check_capture_siska.py --folder tmp/preverjanje_siska_NOV_DATUM
```

## Kaj vključiti v commit

Vključi `app/`, uporabne `analysis/`, `scripts/`, `design-library/`, obnovljeni register in sloje v `data/`, ohranjene arhive in gradivo v `outputs/`, ta README ter `.gitignore`. Velike primerjave so lokalno v `tmp/`; njihovo odstranjevanje iz `analysis/` je namenjena sprememba. Stare poti `deploy/site/` in `analysis/site/` so premaknjene, ne izgubljene.

`.gitignore` izključuje `tmp/`, lokalne nastavitve, skrivnosti, predpomnilnike, nepakirane celotne zajeme `data/<četrt>_*` ter generirana `candidates.json` in `record_hashes.json`. `outputs/` ni več splošno izključen, da je mogoče ohranjene izvorne arhive vključiti v commit. Pri prihodnjih zajemih v Git oziroma predajo vključi njihov preverjeni arhiv iz `outputs/`; sam nastanek lokalne mape `data/<četrt>_*` je še ne shrani v zgodovino.

Commit in objava na Railway sta ločeni dejanji. Ta priprava ni naredila commita, potiska ali objave aplikacije.
