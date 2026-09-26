"""Auto-play demo: mixed strategy (commercial until buffer, then fine art).

Run: python3 demo.py
"""

import random

from simulator import (
    ArtistState,
    end_month,
    make_commercial,
    make_fine_art,
    maybe_event,
    pay_monthly_costs,
    render_apartment,
)


def autoplay(seed: int = 7) -> ArtistState:
    state = ArtistState(rng=random.Random(seed))
    while state.alive():
        pay_monthly_costs(state)
        if not state.alive():
            break
        if state.money < 1500:
            make_commercial(state)
        else:
            make_fine_art(state)
        maybe_event(state)
        end_month(state)
    return state


if __name__ == "__main__":
    final = autoplay()
    print(render_apartment(final))
    print(f"\nResult: {final.over}")
    print(f"Money ${final.money} | Prestige {final.prestige} | "
          f"Paintings {final.paintings} | Morale {final.morale}")
