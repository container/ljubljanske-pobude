# CILJ — lokalna oblikovna referenca

Zajeto 1. 10. 2026 z [cilj.org](https://www.cilj.org/). To je knjižnica za skupni pregled pred implementacijo strani pobude.

Odpri **index.html** v brskalniku. Preglednik deluje lokalno, brez namestitve in brez zunanjih zahtev za pisave ali slike. Gumbi in obrazec so demonstracijski vzorci. Stran pobude še ni implementirana.

## Vsebina

- `index.html` in `reference.css`: vizualni pregled barv, tipografije, komponent, ikon in razmikov.
- `tokens.css` in `tokens.json`: normalizirane vrednosti za prihodnjo uporabo.
- `fonts.css` in `assets/fonts/`: izvorne WOFF2 pisave, latin in latin-ext za č, š, ž.
- `assets/icons/`: 17 izvornih SVG ikon Lucide iz izrisanega DOM-a.
- `assets/cilj-logo.png`: izvorni znak, shranjen kot referenca CILJ.
- `source/`: izvorni CSS, prejeti in izrisani HTML, posnetek strani ter manifest z izvornimi URL-ji in kontrolnimi vsotami sredstev.

## Preverjene oblikovne lastnosti

| Vloga | Vrednost |
| --- | --- |
| Glavni poudarek | `#FF6B35` |
| Ozadje | `#FFFFFF` |
| Glavno besedilo | `#252525` (izvorno HSL 14,5 %) |
| Sekundarno ozadje | `#F7F7F7` |
| Sekundarno besedilo | `#8E8E8E` |
| Obrobe | `#EBEBEB` |
| Besedilo na primarnem gumbu | `#FBFBFB` |
| Naslovi | Plus Jakarta Sans, 600 / 700 / 800 |
| Besedilo in UI | DM Sans, 400 / 500 / 600 / 700 |
| H1 na velikem zaslonu | 72 px / 72 px, 800 |
| H2 na velikem zaslonu | 36 px / 40 px, 700 |
| Običajno besedilo | 16 px / 26 px |
| Gumbi / kartice | polmer 10 px / 12 px |
| Ikone | Lucide, mreža 24 × 24, poteza 2, zaobljeni zaključki |
| Ikonska podlaga | 48 × 48 px, polmer 12 px, oranžna pri 15 % |
| Odseki | 64 px navpično na majhnih, 96 px na velikih zaslonih |
| Bralni stolpec / mreža | največ 896 px / 1024 px |

Oranžna ostaja redek, prepoznaven poudarek. Glavni značaj sestavljajo močni naslovi, veliko praznega prostora, umirjeni prehodi, tanke obrobe in preproste linijske ikone. Domača stran je pretežno tipografska; ne temelji na fotografijah.

## Natančnost in izvor

Barve, tipografija in komponente so preverjene z izračunanimi slogi v brskalniku. Mobilne velikosti in prelomne točke so prebrane iz CSS; mobilni izris izvorne strani ni posebej pregledan. Temni tokeni v JSON so zapisani iz CSS in označeni kot vizualno nepreverjeni.

**Pomembna podrobnost:** `:root --primary` na izvorni strani vsebuje sivo HSL vrednost, medtem ko `.bg-primary` in `.text-primary` neposredno določata `rgb(255 107 53)`. Za knjižnico je zato merodajna dejansko izrisana oranžna. Podobno H1 vsebuje razred `leading-[1.05]`, ki ga pri večjih velikostih preglasijo odzivni razredi; preverjeni namizni razmik vrstic je 72 px.

HTML preglednika je nova predstavitev izmerjenih elementov. Njegova navigacija, razpored kataloga in razlagalno besedilo niso kopija izvorne strani. Vzorci so izluščeni oziroma poenostavljeno rekonstruirani; ne predstavljajo popolne komponentne kode CILJ.

Sredstva so arhivirana za oblikovno referenco. Logotip predstavlja CILJ in njegova vključitev v končno identiteto pobude še ni odločena. Izvorni prenosi sami ne predstavljajo dokumentacije licenc.

## Za naslednji pregled

1. Potrditi oranžno in par pisav kot osnovo pobude.
2. Izbrati gostoto vsebine in stopnjo zaobljenosti.
3. Določiti identiteto pobude ter vlogo logotipa CILJ.
4. Pred implementacijo določiti kontrastne različice: svetlo sivo besedilo in belo besedilo na oranžni imata na izvirniku omejen kontrast. Izvorne vrednosti tukaj ostajajo jasno ločene od morebitnih prihodnjih prilagoditev.

## Razširitev za grafikone in zemljevid

Predlagana dodatna paleta (ni povzeta z izvorne strani): šest kategorijskih barv, petstopenjska oranžna lestvica od manj do več ter siva za manjkajoče podatke. Vzorci so v pregledniku; vrednosti v `tokens.css` (`--cilj-chart-*`, `--cilj-map-*`) in `tokens.json` (`dataVisualization`). Kategorije ohranijo iste barve med prikazi in imajo tudi besedilne oznake ali simbole.
