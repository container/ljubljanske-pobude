# Navodila za označevanje pobud ČS Vič

Cilj analize: najti **dolgo odprte, resne težave, ki zadevajo prebivalce ČS Vič**, posebej varnost, in znake **sistemskega zanemarjanja**. Status »odgovorjena« na portalu ne pove nič o rešitvi.

Vsako pobudo označi samo po besedilu pobude in odgovora. Ne ugibaj; kadar nisi prepričan, nastavi `gotovost: "nizka"` in razlog napiši v `opomba`.

## Polja

### vrsta (natanko ena, glavna)
- `V1` Okvara, poškodba: nekaj je poškodovano, ne deluje (luknja, pokrov jaška, ograja, luč, izbrisana oznaka).
- `V2` Ponavljajoče vzdrževanje: rešitev je pogostost vzdrževanja (obrez rastja, čiščenje, košnja, praznjenje košev, grafiti).
- `V3` Kršitve in nadzor: redarstvo ali inšpekcija (parkiranje, hitrost, divja odlagališča, hrup).
- `V4` Manjša ureditev: klančina, znak, semafor, prehod, stebrički, talne oznake na novo, hitrostna ovira.
- `V5` Večja investicija, prenova: pločnik vzdolž ulice, rekonstrukcija ali preplastitev ceste, nova kolesarska povezava.
- `V6` Nova storitev, predlog: klopi, igrišča, WC, linije LPP, sprememba odloka.
- `V7` Vprašanje, informacija: prijavitelj predvsem nekaj sprašuje (kdaj, kdo, zakaj, lastništvo).
- `V8` Pritožba na delo služb: slaba sanacija, neodziv, nedokončana dela kot glavni poudarek.
- `V9` Zunaj pristojnosti MOL: vsebina je v pristojnosti države ali zasebnika (samo kadar je to bistvo pobude).

### obseg
`tocka`, `odsek` (del ulice ali cela ulica), `soseska`, `vic` (cela četrt), `mol` (celo mesto, sistemsko).

### lokacija
- `ok`: zadeva je na Viču.
- `tocka`: točka je napačna, zadeva pa je na Viču.
- `izven`: iz besedila je razvidno, da zadeva **ni v ČS Vič** (npr. Pot Rdečega križa pri Barju, UE Tobačna, most čez Glinščico pri Biotehniški fakulteti so uporabnik označil kot izven). Vse točke so znotraj meje Viča, zato se odloči po imenih krajev v besedilu. Če nisi prepričan, `ok` z `gotovost: "nizka"`.
- `brez`: pobuda ni vezana na lokacijo (vprašanja za celo mesto).

### koga (ali zadeva prebivalce ČS Vič): `da` / `ne`
- `da`: vse, kar vpliva na življenje v četrti, tudi pločniki, prehodi, kolesarske steze in varnost pešcev **ob vpadnicah**; azilni dom na Viču (tudi varnost `da`).
- `ne`: cestišče in pretočnost vpadnic in tranzitnih cest (npr. preplastitev Tržaške), P+R in storitve predvsem za obiskovalce in tranzit, mestna politična vprašanja brez lokalnega vpliva, osebna vprašanja posameznika.

### varnost: `da` / `ne`
`da`, kadar je ogrožena fizična varnost ljudi (promet, pešci, kolesarji, otroci, padci, vidnost, dostop intervencije).

### izvajalec (kdo mora dejansko ukrepati, ne kdo je odgovoril)
`ceste`, `promet` (signalizacija, prometna ureditev), `razsvetljava`, `zelenje` (drevesa, zelenice; VOKA SNAGA), `cistoca` (čiščenje, odpadki), `redarstvo`, `inspektorat`, `lpt` (JP LPT, parkirišča), `lpp`, `investicije` (projekti, prenove), `nepremicnine` (zemljišča, lastništvo), `okolje`, `sport`, `kultura`, `zascita`, `drzava` (DRSI, DRSV, država), `zasebnik`, `cs` (ČS Vič), `drugo`.

### stanje (glede na objavljeni odgovor; ni dokaz rešitve)
- `S0` Brez odgovora.
- `S1` Zavrnjeno ali odloženo brez roka: »ni predvideno«, »ne načrtujemo«, »ni v kratkoročnem planu«, »po zaključku drugih ureditev bomo preučili«, »ni mogoče«.
- `S2` Zunaj pristojnosti MOL: odgovor napoti na državo ali zasebnika.
- `S3` Odgovor brez zaveze: samo zahvala; »najverjetneje že obravnavana, oddajte znova«; prošnja za fotografijo ali dodatne podatke; **kratek odgovor brez vsebine, kot je »Hvala, preverimo.«; splošne obljube brez konkretnega ukrepa: »preverili bomo in ukrepali skladno s pristojnostmi«, »po potrebi izvedli ukrepe«, »posredovali izvajalcu«**
- `S4` Nedoločena obljuba s konkretnim ukrepom, a brez roka: »nadzor v okviru kadrovskih zmožnosti«, »obrezali bomo ob naslednjem rednem vzdrževanju«, »v planu, brez časovnice«.
- `S5` Konkretna napoved: »naročili smo«, »uvrščeno v plan del«, »bomo dopolnili signalizacijo«, datum ali rok, projekt v teku.
- `S6` Izvedba po navedbi MOL: »opravljeno«, »sanirano«, »odstranjeno dne …«.
- `SV` Vprašanje (V7) je vsebinsko odgovorjeno.

Če odgovor vsebuje več delov (npr. luč naročena, parkiranje nadzor), izberi stanje za **glavni problem pobude** in drugi del omeni v `opomba`.

### relevanca: `visoka` / `srednja` / `nizka`
Kako dobro pobuda ustreza cilju analize. Uporabnik ocenjuje **višje**:
- varnost prebivalcev, posebej otrok, pešcev, kolesarjev;
- površine za otroke in mlade (igrišča, šolske poti, okolica šol, vrtcev in gimnazije);
- lastništvo in prehodnost javnih površin (javna površina postala zasebna, cesta ali parkirišče na zasebni parceli);
- projekte, ki bodo spremenili osrednji prostor četrti, tudi če so mestni;
- staro, dotrajano infrastrukturo sosesk (ulice, pločniki »stari 50 let«);
- dolgotrajne ali ponavljajoče se težave in zavrnjene zahteve za varnost.

Uporabnik ocenjuje **nižje**: tranzit in vpadnice (cestišče), P+R in storitve za obiskovalce, enkratna vprašanja brez posledic za četrt, športne objekte kot storitev (npr. savna), politična vprašanja brez lokalnega vpliva.

### Ostala polja
- `dokaz`: **dobesedni** izsek iz odgovora (največ ~25 besed), na katerem temelji stanje. Pri S0 prazen niz.
- `besedilo_ponovitev`: `da`, če besedilo pobude samo pove, da se problem ponavlja ali vleče (»že leta«, »ponovno«, »spet«, »že od 2013«, sklic na prejšnjo pobudo); sicer `ne`.
- `zadeva`: kratek ključ za združevanje v obliki `"<kraj> | <problem>"`, npr. `"Vrhovnikova (Tržaška–Jamova) | varnost pešcev, ni pločnika"`, `"Jadranska × Jamova | zaraščen semafor"`, `"Nahlikova | parkiranje na pločniku"`. Kraj naj bo ulica ali križišče, kot ga navaja besedilo; problem v nekaj besedah. Uporabljaj dosledna imena ulic v imenovalniku (»Cesta v Gorice«, »Glinška ulica«).
- `tema`: kadar gre za problem, ki se pojavlja po vsem Viču, ena od: `parkiranje`, `hitrost in tranzit`, `pločniki in prehodi`, `kolesarska infrastruktura`, `dotrajane ceste`, `rastje in vidnost`, `čistoča in odpadki`, `razsvetljava`, `igrišča in javni prostor`, `lastništvo zemljišč`, `javni promet`, `drugo`.
- `gotovost`: `visoka` / `nizka`.
- `opomba`: kratko, kaj je pomembno za analizo (npr. odgovor ne naslovi dela pobude, odgovor po dolgem času, navedena nesreča).

## Primeri iz umerjanja (potrdil uporabnik)
- 70927 Vrhovnikova, pločnik in kolesarska: V5, odsek, ok, da, varnost da, investicije, S1 (»v letošnjem letu ni predvidena«), visoka.
- 73605 Jamova 23 vrtec, robnik: V4, tocka, ok, da, varnost da, ceste, stanje po novem pravilu **S3** (»Preverimo.«), visoka.
- 75814 zaraščen semafor Jadranska × Jamova: V2, tocka, ok, da, varnost da, zelenje, S4 (odstopljeno VOKA SNAGA), visoka.
- 68180 nedokončana preplastitev Tržaške: V5, odsek, ok, koga **ne** (vpadnica), ceste, S3 (samo zahvala), nizka.
- 78849 pokrov jaška in meritve: V7, tocka, ok, da, ceste, S3 (»ker je minilo že dalj časa, sporočite ali je še težava«), srednja; opomba: odgovor prepozen.
- 84043 javno parkirišče na zasebni parceli: V7, tocka, ok, koga da, nepremicnine, S0, visoka.
- 77102 center plezalnih športov: V7, mol, brez, da, investicije, S5, **visoka** (preoblikoval bo osrednji prostor četrti).
- 81864 semafor na Poti Rdečega križa: lokacija **izven**.
- 82472 WC na P+R Dolgi most: V6, tocka, ok, koga ne, lpt, S1, nizka.
- 86206 Postojnska, hitrost in tranzit: V3, odsek, ok, da, varnost da, redarstvo, S4, visoka; opomba: umirjanje prometa ni naslovljeno.

## Izhod
JSON seznam, en objekt na pobudo, s polji:
`id, vrsta, obseg, lokacija, koga, varnost, izvajalec, stanje, relevanca, dokaz, besedilo_ponovitev, zadeva, tema, gotovost, opomba`.
Polje `tema` je lahko prazen niz.
