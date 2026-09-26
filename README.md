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
| Make Commercial art | 1 paint → ~$120–$250, +1 rep, +2 prestige |
| Make Fine art | 1 paint → 45% chance ~$400–$900, +8 prestige, +5 rep on sale |
| Skip painting | save paint, lose morale |

Die if money < $0 after rent (evicted) or morale hits 0 (burnout).
Win by surviving 12 months with prestige ≥ 60 **or** money ≥ $5000.

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
