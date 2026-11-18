# THE WORLD — Tuesday, 17 November 2026

One image summing up the world news of Tuesday 17 November 2026, drawn
as a one-page newspaper front page: masthead with the date, a markets
ticker, a lead story, a dotted world map with numbered story markers,
four more stories, and an IN BRIEF strip.

## Stories in the image

1. **Bridges under fire (lead)** — Ukraine strikes the Crimea bridge
   for a second day, collapsing part of the road span; Russian missiles
   hit Kyiv's North and South bridges, cutting heat, water and power.
2. **Mines in the Gulf** — Tankers hit by mines near the Strait of
   Hormuz; a third U.S. carrier arrives; Iranian drones aimed at a U.S.
   radar base in Bahrain are shot down.
3. **Shenzhen summit** — China confirms the first three-way meeting of
   Xi, Trump and Putin, Thursday in Shenzhen on the APEC sidelines.
4. **Audit fails again** — Ninth straight year without a clean Pentagon
   audit; auditors could not verify accounts covering more than
   $4.8 trillion in assets.
5. **Jets scrambled** — Japan launches fighter jets and protests after
   two suspected Russian aircraft violate its airspace.
6. **In brief** — UK sanctions settlement builders; allies urge Gaza aid
   in. CDC: 13 babies born with measles as U.S. cases hit their highest
   since 1991. SpaceX catches its Starship upper stage after orbit.
   Markets: S&P 500 -1.34%, STOXX 600 -1.75%, Brent $91.67, gold up.

Every story is an event of 17 November 2026, as reported that day.

## How it works

`main.py` (Python 3, standard library only) draws the whole page
procedurally — a hand-built 5x7 bitmap font, a dotted world map from a
coarse land grid, and a small PNG encoder — and writes it to
`/output/entry.png` (`$MAKEFUN_OUTPUT_DIR` outside the grader).
No network, no external assets, no timestamps: running it twice writes
byte-identical output.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Output: a 1024x1024 PNG, about 21 KB.
