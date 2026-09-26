"""Starving Artist Simulator — terminal edition.

Pure Python, no dependencies. The web version (web/app.js) mirrors
these exact rules so both stay in sync.

Loop per month:
  1. Pay $800 rent + $50 paint (auto if affordable, else choices matter)
  2. Player picks: [1] Commercial  [2] Fine art  [3] Skip / rest
  3. Resolve sales, morale, prestige, random events
  4. Check win / lose
"""

from __future__ import annotations

import random

RENT = 800
PAINT_COST = 50
START_MONEY = 1200
START_PAINT = 3
START_MORALE = 70
WIN_MONTHS = 12

COMMERCIAL_PRICE = (120, 250)
FINE_PRICE = (400, 900)
FINE_SALE_CHANCE = 0.45


class ArtistState:
    """Mutable game state. Kept simple so tests can drive it deterministically."""

    def __init__(
        self,
        money: int = START_MONEY,
        paint: int = START_PAINT,
        morale: int = START_MORALE,
        prestige: int = 0,
        reputation: int = 0,
        month: int = 1,
        paintings: int = 0,
        rng: random.Random | None = None,
    ) -> None:
        self.money = money
        self.paint = paint
        self.morale = morale
        self.prestige = prestige
        self.reputation = reputation
        self.month = month
        self.paintings = paintings
        self.over: str | None = None  # None | "evicted" | "burnout" | "won"
        self.log: list[str] = []
        self.rng = rng or random.Random()

    # -- helpers ---------------------------------------------------------
    def snapshot(self) -> dict:
        return {
            "money": self.money,
            "paint": self.paint,
            "morale": self.morale,
            "prestige": self.prestige,
            "reputation": self.reputation,
            "month": self.month,
            "paintings": self.paintings,
            "over": self.over,
        }

    def alive(self) -> bool:
        return self.over is None

    def _say(self, msg: str) -> None:
        self.log.append(msg)


def pay_monthly_costs(state: ArtistState) -> None:
    """Charge rent + paint at the start of the month."""
    state.money -= RENT
    state._say(f"🏠 Paid ${RENT} rent.")
    if state.money < 0:
        state.over = "evicted"
        state._say("💀 Evicted! You couldn't pay rent.")
        return
    if state.money >= PAINT_COST:
        state.money -= PAINT_COST
        state.paint += 1
        state._say(f"🎨 Bought paint (−${PAINT_COST}). Tubes: {state.paint}.")
    else:
        state._say("🎨 Couldn't afford paint this month.")
        state.morale -= 8


def make_commercial(state: ArtistState) -> int:
    """Commercial art: always sells, low prestige. Returns earnings."""
    if state.paint <= 0:
        state.morale -= 10
        state._say("No paint! You stare at a blank canvas. Morale −10.")
        return 0
    state.paint -= 1
    earned = state.rng.randint(*COMMERCIAL_PRICE)
    state.money += earned
    state.paintings += 1
    state.prestige += 2
    state.reputation += 1
    state.morale = min(100, state.morale + 4)
    state._say(f"🖼️ Sold a commercial piece for ${earned}. (+2 prestige)")
    return earned


def make_fine_art(state: ArtistState) -> int:
    """Fine art: 45% sale chance, high prestige. Returns earnings."""
    if state.paint <= 0:
        state.morale -= 10
        state._say("No paint! You stare at a blank canvas. Morale −10.")
        return 0
    state.paint -= 1
    state.paintings += 1
    state.prestige += 8
    if state.rng.random() < FINE_SALE_CHANCE:
        earned = state.rng.randint(*FINE_PRICE)
        state.money += earned
        state.reputation += 5
        state.morale = min(100, state.morale + 10)
        state._say(f"🌟 A collector bought your fine art for ${earned}! (+8 prestige)")
        return earned
    state.morale -= 6
    state.reputation += 1
    state._say("🌧️ Gallery loved it, nobody bought it. (+8 prestige, morale −6)")
    return 0


def rest(state: ArtistState) -> None:
    """Skip painting: save paint, recover morale, lose a little rep."""
    state.morale = min(100, state.morale + 12)
    state.reputation = max(0, state.reputation - 1)
    state._say("😴 Rested. Morale +12, saved your paint.")


def maybe_event(state: ArtistState) -> None:
    """One small random event per month (~35% chance)."""
    roll = state.rng.random()
    if roll > 0.35:
        return
    events = [
        ("mural", "A café paid you $150 for a chalk mural!", 150, 0, 0),
        ("review", "A blog reviewed you! +4 prestige.", 0, 6, 4),
        ("leak", "Roof leak! Repairs cost $120.", -120, -4, 0),
        ("friend", "A friend brings groceries. Morale +8.", 0, 8, 0),
    ]
    key, msg, money, morale, prestige = state.rng.choice(events)
    _ = key
    state.money += money
    state.morale = max(0, min(100, state.morale + morale))
    state.prestige = max(0, state.prestige + prestige)
    state._say(f"✨ Event: {msg}")


def end_month(state: ArtistState) -> None:
    """Advance the clock and check endings."""
    if state.morale <= 0:
        state.over = "burnout"
        state._say("💀 Burnout! You put down the brush.")
        return
    if state.money < 0:
        state.over = "evicted"
        return
    if state.month >= WIN_MONTHS and (state.prestige >= 60 or state.money >= 5000):
        state.over = "won"
        state._say("🏆 You made it as an artist!")
        return
    if state.month >= WIN_MONTHS:
        # Survived the year but no breakout -> gentle ending, not death.
        state.over = "won" if state.money >= 0 else "evicted"
        state._say(
            "📆 A year has passed. You survived — "
            + ("legend in the making!" if state.over == "won" else "")
        )
        return
    state.month += 1
    state.morale = max(0, state.morale - 2)  # city wears on you


def apartment_mood(state: ArtistState) -> str:
    """Text portrait of the apartment, mirrors the web canvas tiers."""
    if state.money < 200 or state.paintings == 0:
        return "bare"
    if state.paintings < 3:
        return "sparse"
    if state.prestige >= 40 or state.money >= 3000:
        return "gallery"
    return "cozy"


def render_apartment(state: ArtistState) -> str:
    """ASCII apartment — empty if broke, colorful if successful."""
    mood = apartment_mood(state)
    paintings_on_wall = min(state.paintings, 6)
    wall = ""
    for i in range(6):
        wall += "[##]" if i < paintings_on_wall else "[  ]"
    if mood == "bare":
        return (
            "+----------------------+\n"
            "|      (empty)         |\n"
            f"| {wall} |\n"
            "|   cold floor...      |\n"
            "+----------------------+"
        )
    if mood == "sparse":
        return (
            "+----------------------+\n"
            "|   * one plant *      |\n"
            f"| {wall} |\n"
            "|   a rug, thin...     |\n"
            "+----------------------+"
        )
    if mood == "cozy":
        return (
            "+----------------------+\n"
            "|  ~ warm lamp glow ~  |\n"
            f"| {wall} |\n"
            "|  plants + full shelf |\n"
            "+----------------------+"
        )
    return (
        "+----------------------+\n"
        "|  *** MINI GALLERY *** |\n"
        f"| {wall} |\n"
        "|  wine, plants, prints! |\n"
        "+----------------------+"
    )


# -- CLI ---------------------------------------------------------------
def play_cli(seed: int | None = None) -> None:
    rng = random.Random(seed)
    state = ArtistState(rng=rng)
    print("🎨 STARVING ARTIST SIMULATOR")
    print("Survive 12 months. Rent $800/mo, paint $50/mo.")
    print("Commercial = safe cash. Fine art = prestige gamble.\n")

    while state.alive():
        print(f"\n—— Month {state.month}/12 ——")
        print(
            f"💰 ${state.money} | 🎨x{state.paint} | "
            f"😊 {state.morale} | ⭐ {state.prestige} | 📣 {state.reputation}"
        )
        print(render_apartment(state))
        pay_monthly_costs(state)
        if not state.alive():
            break
        print(f"After bills: 💰 ${state.money} | 🎨x{state.paint}")
        choice = input("[1] Commercial  [2] Fine art  [3] Rest > ").strip()
        if choice == "1":
            make_commercial(state)
        elif choice == "2":
            make_fine_art(state)
        else:
            rest(state)
        maybe_event(state)
        for line in state.log[-4:]:
            print("  " + line)
        state.log.clear()
        end_month(state)

    print(f"\nGame over: {state.over}! "
          f"Money ${state.money}, prestige {state.prestige}, "
          f"paintings {state.paintings}.")


if __name__ == "__main__":
    play_cli()
