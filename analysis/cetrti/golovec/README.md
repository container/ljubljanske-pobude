# Golovec – pilot vrste pobud in stanja odgovorov

Obdobje prijave: **12. 10. 2025–12. 10. 2026**, stanje portala ob zajemu 12. 10. 2026. Pilot zajema **111 pobud**: 108 z odgovorom in 3 brez odgovora. Uporabljena je enaka metodologija V1–V9 in S0–S6/SV kot pri Centru, opisana v [navodilih](oznacevanje/navodila_vrsta_stanje.md). Nadaljnje širjenje zajema ne širi obdobja te analize.

| Stanje po odgovoru | Pobud | Delež vseh 111 |
|---|---:|---:|
| S0 – Brez odgovora | 3 | 2.7 % |
| S1 – Zavrnjeno ali odloženo brez roka | 36 | 32.4 % |
| S2 – Napotitev zunaj pristojnosti MOL | 5 | 4.5 % |
| S3 – Odgovor brez zaveze za izvedbo | 26 | 23.4 % |
| S4 – Konkreten ukrep, nedoločena obljuba brez roka | 16 | 14.4 % |
| S5 – Konkretna napoved | 13 | 11.7 % |
| S6 – Izvedba po navedbi MOL | 1 | 0.9 % |
| SV – Vsebinsko odgovorjeno vprašanje | 11 | 9.9 % |

Največ je predlogov novih storitev ali režimov (V6: 39), okvar oziroma poškodb (V1: 16), manjših ureditev (V4: 15) in pobud za nadzor (V3: 14). Pogosti so predlogi glede parkiranja in prometne ureditve. Enota je portalni ID: ponovljena besedila ali pozivi ostanejo ločeni zapisi in ne predstavljajo nujno različnih problemov ali različnih oseb.

**13 konkretnih napovedi in ena navedba izvedbe** niso dokaz 14 rešenih problemov. Edini S6, ID 82754, govori o že sklenjenem dogovoru glede parkiranja zaposlenih vrtca; brezplačnost ni potrjena, zato ima nižjo gotovost. Pri **35 od 108 strojno ocenjenih odgovorov** je gotovost nižja (32,4 %); opomba pri vsakem pojasni dvoumnost. Oznake niso neodvisno človeško pregledane in niso potrjene na terenu. Vsebinsko odgovorjena vprašanja (SV) so ločena od obljubljenih ukrepov.

Mediana od prijave do **zadnjega** objavljenega odgovora je **20,5 dneva** (108 zapisov). To ni nujno čas do prvega odziva ali rešitve. Binarne priloge niso bile analizirane.

Datoteke: [vse oznake](oznake_vrsta_stanje.json), [statistika in preverjanja](pilot_statistika.json), izvorni paketi in dokazni izseki v `oznacevanje/paketi`. Preverjeni so popoln nabor 111 enoličnih ID-jev, datumsko obdobje, dovoljene šifre, statusi S0 ter dobesednost vseh 108 dokaznih izsekov (največ 25 besed).

## Izmerjena poraba pilota

Opazovano obdobje je trajalo **12.3 minute**, vključno s prekinitvijo/nadaljevanjem, orodji in spremljanjem sočasnega zajema. Števci tega pogovora kažejo **65,302 nepomnilniških vhodnih tokenov**, **9,605 izhodnih** in **930,304 ponovno uporabljenih vhodnih tokenov**. Nepomnilniški vhod in izhod skupaj: **74,907**. To ni čista cena označevanja besedil ali neposredna pretvorba v odstotek naročniške kvote. Razmišljanje je že vključeno v izhodne tokene. Podrobnosti: [meritev](pilot_usage.json).

Druge štiri četrti v tem pilotu še niso semantično analizirane. Rezultati ostanejo lokalni, brez objave spletne strani.
