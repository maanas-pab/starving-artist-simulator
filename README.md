# 🎨 Starving Artist Simulator

A Tamagotchi-style survival game where **you are the artist**.

Each month you must survive:
- 🏠 Pay **$800 rent**
- 🎨 Buy **paint ($50)** to keep creating
- 🖼️ Choose your path: **Commercial art** (sells easy, low prestige)
  vs **Fine art** (hard to sell, high prestige)

Your apartment is your canvas — empty and grey when you're broke,
colorful and gallery-worthy when you make it.

## Play it

**Option A — Web (no setup):** open `web/index.html` in a browser.

**Option B — Python (terminal):**

```bash
python3 simulator.py
```

## Rules

| Action | Cost / Effect |
|---|---|
| Rent (monthly) | −$800 |
| Paint (monthly) | −$50, +paint tubes |
| Make Commercial art | 1 paint → $700–$1100, +1 rep, +2 prestige, +4 morale |
| Make Fine art | 1 paint → 45% chance $1500–$3000, +8 prestige, +5 rep on sale, +10 morale (else −6 morale) |
| Rest (skip painting) | save paint, +12 morale, −1 rep |

Die if money < $0 after rent (evicted) or morale hits 0 (burnout).
Win by surviving 12 months with prestige ≥ 60 **or** money ≥ $5000.

## Strategy

- **Commercial grind** pays the rent reliably but rarely wins on prestige.
- **Fine art rush** can make you rich or famous fast — but dry spells kill.
- A common winning line: commercial for months 1–4, then fine art once
  you have a cash buffer. Never let paint hit 0.

## Apartment tiers

| Paintings / wealth | Look |
|---|---|
| Broke or 0 paintings | `bare` — grey walls, cold floor |
| 1–2 paintings | `sparse` — one plant, thin rug |
| 3+ paintings | `cozy` — warm lamp, plants, shelf |
| Prestige ≥ 40 or $3000+ | `gallery` — your home is the show |

## Tests

```bash
python3 -m unittest discover tests -v
```

## Repo layout

```
simulator.py        # terminal game (pure Python, no deps)
web/
  index.html        # game UI
  styles.css        # apartment + stats styling
  app.js            # game logic + canvas apartment renderer
tests/
  test_simulator.py # balance / engine tests
```

Made with HTML + Python, 3 buttons, and stats bars.
