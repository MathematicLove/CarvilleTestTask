import unittest, random
from decimal import Decimal
from nds import calc, calc_prices_via_mod, calc_prices_binary_search, calc_prices_bruteforce_window
import math

class TestCalcNDS(unittest.TestCase):
    def test_examples(self):
        w, wo = calc(Decimal("1.81"), 20)
        self.assertEqual((w, wo), (Decimal("1.80"), Decimal("1.50")))
        w, wo = calc(Decimal("1.81"), 18)
        self.assertEqual((w, wo), (Decimal("1.77"), Decimal("1.50")))

    def test_edges(self):
        for s in ["0", "0.01", "1.23", "123456789.99", "1000000000000.12345678901234567890"]:
            w, wo = calc(Decimal(s), 0)
            self.assertEqual(w, Decimal(s).quantize(Decimal("0.00")))
            self.assertEqual(wo, Decimal(s).quantize(Decimal("0.00")))

        w, wo = calc(Decimal("0"), 99)
        self.assertEqual((w, wo), (Decimal("0.00"), Decimal("0.00")))

        w, wo = calc(Decimal("1.00"), 99)
        self.assertEqual((w, wo), (Decimal("1.99"), Decimal("1.00")))

    def test_random_vs_neighbors(self):
        rnd = random.Random(123)
        for _ in range(2000):
            p = rnd.randint(0,99)
            int_part = rnd.randint(0, 10**6)
            frac_part = rnd.randint(0, 10**18)
            price = Decimal(int_part) + Decimal(frac_part) / Decimal(10**rnd.randint(0,18))
            w, wo = calc(price, p)

            # для копеек
            self.assertEqual(w.as_tuple().exponent, -2)
            self.assertEqual(wo.as_tuple().exponent, -2)

            lhs = (wo * Decimal(100 + p)) / Decimal(100)
            self.assertEqual(lhs, w)

            T = price * Decimal(100)
            g = math.gcd(100, 100+p)
            s = (100+p)//g

            Y = int((w * Decimal(100)))
            self.assertEqual(Y % s, 0)
            for neighbor in (Y - s, Y + s):
                if neighbor < 0:
                    continue
                d_neighbor = abs(Decimal(neighbor) - T)
                d_curr = abs(Decimal(Y) - T)
                self.assertTrue(d_neighbor >= d_curr - Decimal("0"))

    def test_variants_agree(self):
        rnd = random.Random(321)
        for _ in range(1000):
            p = rnd.randint(0,99)
            price = Decimal(rnd.randint(0,10**4)) / Decimal(100) + Decimal(rnd.randint(0,10**6)) / Decimal(10**rnd.randint(2,10))
            a = calc(price, p)
            b = calc_prices_via_mod(price, p)
            c = calc_prices_binary_search(price, p)
            d = calc_prices_bruteforce_window(price, p, window=5)
            self.assertEqual(a, b)
            self.assertEqual(a, c)
            self.assertEqual(a, d)

if __name__ == "__main__":
    unittest.main(verbosity=2)
