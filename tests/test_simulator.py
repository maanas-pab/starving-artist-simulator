"""Balance + engine tests. Run with: python3 -m unittest discover tests -v"""

import random
import unittest

from simulator import (
    ArtistState,
    apartment_mood,
    end_month,
    make_commercial,
    make_fine_art,
    pay_monthly_costs,
    rest,
)


class TestEconomy(unittest.TestCase):
    def test_rent_and_paint_charged(self):
        s = ArtistState(money=1200, paint=3)
        pay_monthly_costs(s)
        self.assertEqual(s.money, 1200 - 800 - 50)
        self.assertEqual(s.paint, 4)
        self.assertIsNone(s.over)

    def test_eviction_when_broke(self):
        s = ArtistState(money=500, paint=1)
        pay_monthly_costs(s)
        self.assertEqual(s.over, "evicted")

    def test_commercial_always_pays(self):
        s = ArtistState(money=350, paint=2, rng=random.Random(0))
        earned = make_commercial(s)
        self.assertGreaterEqual(earned, 700)
        self.assertLessEqual(earned, 1100)
        self.assertEqual(s.paint, 1)
        self.assertEqual(s.prestige, 2)

    def test_fine_art_gamble(self):
        # Seed 1: known sale outcome path — just assert bounds + prestige.
        s = ArtistState(money=350, paint=2, rng=random.Random(1))
        earned = make_fine_art(s)
        self.assertEqual(s.prestige, 8)
        self.assertTrue(earned == 0 or 1500 <= earned <= 3000)

    def test_no_paint_hurts_morale(self):
        s = ArtistState(paint=0, morale=50)
        make_commercial(s)
        self.assertEqual(s.morale, 40)

    def test_rest_recovers(self):
        s = ArtistState(morale=50, reputation=5)
        rest(s)
        self.assertEqual(s.morale, 62)
        self.assertEqual(s.reputation, 4)

    def test_burnout(self):
        s = ArtistState(morale=0)
        end_month(s)
        self.assertEqual(s.over, "burnout")

    def test_apartment_moods(self):
        self.assertEqual(apartment_mood(ArtistState(money=100)), "bare")
        self.assertEqual(
            apartment_mood(ArtistState(money=1000, paintings=1)), "sparse"
        )
        self.assertEqual(
            apartment_mood(ArtistState(money=1000, paintings=5)), "cozy"
        )
        self.assertEqual(
            apartment_mood(ArtistState(money=1000, paintings=5, prestige=50)),
            "gallery",
        )

    def test_commercial_grind_can_survive_early_game(self):
        """Sanity: painting commercial every month shouldn't insta-die."""
        s = ArtistState(rng=random.Random(42))
        for _ in range(3):
            pay_monthly_costs(s)
            self.assertIsNone(s.over)
            make_commercial(s)
            end_month(s)
        self.assertIsNone(s.over)


if __name__ == "__main__":
    unittest.main()
