from __future__ import annotations
from decimal import Decimal, getcontext, ROUND_FLOOR
import math
from typing import Tuple

getcontext().prec = 80
Two = Decimal(100) 

def _to_decimal(x) -> Decimal:
    if isinstance(x, Decimal):
        return x
    # str для float не тащим двоичную погрешность
    return Decimal(str(x))


def _validate(proc_nds: int, price_with_nds: Decimal):
    if not (isinstance(proc_nds, int) and 0 <= proc_nds <= 99):
        raise ValueError("должено быть целым в диапазоне 0 ... 99")
    if price_with_nds < 0:
        raise ValueError("Ну вы видели цену < 0 ??")


def calc_prices(input_price_with_nds, proc_nds: int, tie: str = "down") -> Tuple[Decimal, Decimal]:
    P = _to_decimal(input_price_with_nds)
    _validate(proc_nds, P)

    p = int(proc_nds)
    T = P * Decimal(100)
    g = math.gcd(100, 100 + p)
    s = (100 + p) // g  
    sD = Decimal(s)
    k_floor = int((T / sD).to_integral_value(rounding=ROUND_FLOOR))
    y1 = s * k_floor
    y2 = y1 + s

    d1 = abs(T - Decimal(y1))
    d2 = abs(Decimal(y2) - T)

    if d2 < d1 or (d1 == d2 and tie == "up"):
        Y = y2
    else:
        Y = y1

    # гарантированно целое!!! 
    X = (Y * 100) // (100 + p)

    assert (X * (100 + p)) % 100 == 0, "Внутренняя ошибка целостности"

    price_with = (Decimal(Y) / Decimal(100)).quantize(Decimal("0.00"))
    price_without = (Decimal(X) / Decimal(100)).quantize(Decimal("0.00"))
    return price_with, price_without

def calc_prices_via_mod(input_price_with_nds, proc_nds: int, tie: str = "down") -> Tuple[Decimal, Decimal]:
 #  тоже О(1) но вместо floor/ceil используем остаток по модулю шага
    P = _to_decimal(input_price_with_nds)
    _validate(proc_nds, P)
    p = int(proc_nds)

    T = P * Decimal(100)

    g = math.gcd(100, 100 + p)
    s = (100 + p) // g
    sD = Decimal(s)

    r = T % sD 
    y_down = T - r      
    y_up   = y_down + sD

    d_down = abs(T - y_down)
    d_up   = abs(y_up - T)

    if d_up < d_down or (d_up == d_down and tie == "up"):
        Y = int(y_up)
    else:
        Y = int(y_down)

    X = (Y * 100) // (100 + p)
    price_with = (Decimal(Y) / Decimal(100)).quantize(Decimal("0.00"))
    price_without = (Decimal(X) / Decimal(100)).quantize(Decimal("0.00"))
    return price_with, price_without


def calc_prices_binary_search(input_price_with_nds, proc_nds: int, max_iters: int = 64) -> Tuple[Decimal, Decimal]:
    # интересно но медленно - left [tag] right ? p* ++ : p* -- (BSA)
    P = _to_decimal(input_price_with_nds)
    _validate(proc_nds, P)
    p = int(proc_nds)

    T = P * Decimal(100)

    g = math.gcd(100, 100 + p)
    s = (100 + p) // g
    sD = Decimal(s)

    # ищем по k в диапазоне [0 .. ceil(T/s)+1] — точно хватит, чтобы обойти ближайшие
    left = 0
    right = int((T / sD).to_integral_value(rounding=ROUND_FLOOR)) + 2

    # f(k)=k*s-T
    for _ in range(max_iters):
        if right - left <= 1:
            break
        mid = (left + right) // 2
        val = Decimal(mid * s) - T
        if val < 0:
            left = mid
        else:
            right = mid

    # вокруг точки - смены знака
    cand = [max(left-1,0), left, right, right+1]
    bestY = None
    bestD = None
    for k in cand:
        Y = k * s
        d = abs(Decimal(Y) - T)
        if bestD is None or d < bestD or (d == bestD and Y < bestY):
            bestD, bestY = d, Y

    X = (bestY * 100) // (100 + p)
    price_with = (Decimal(bestY) / Decimal(100)).quantize(Decimal("0.00"))
    price_without = (Decimal(X) / Decimal(100)).quantize(Decimal("0.00"))
    return price_with, price_without


def calc_prices_bruteforce_window(input_price_with_nds, proc_nds: int, window: int = 5) -> Tuple[Decimal, Decimal]:
    #МЕДЛЕННО! перебор нескольких ближайших Y вокруг round(T/s)*s. O(window). При window=5 норм.
    P = _to_decimal(input_price_with_nds)
    _validate(proc_nds, P)
    p = int(proc_nds)

    T = P * Decimal(100)
    g = math.gcd(100, 100 + p)
    s = (100 + p) // g

    k0 = int((T / Decimal(s)).to_integral_value(rounding=ROUND_FLOOR))
    bestY = None
    bestD = None
    for dk in range(-window, window+1):
        k = max(k0 + dk, 0)
        Y = k * s
        d = abs(Decimal(Y) - T)
        if bestD is None or d < bestD or (d == bestD and Y < bestY):
            bestD, bestY = d, Y

    X = (bestY * 100) // (100 + p)
    price_with = (Decimal(bestY) / Decimal(100)).quantize(Decimal("0.00"))
    price_without = (Decimal(X) / Decimal(100)).quantize(Decimal("0.00"))
    return price_with, price_without

calc = calc_prices

if __name__ == "__main__":
    examples = [
        (Decimal("1.81"), 20),
        (Decimal("1.81"), 18),
        ("1234567890.12345678901234567890", 7),
        (0, 99),
        (1.00, 0),
        ("1.999", 50),
    ]
    for price, p in examples:
        with_nds, without_nds = calc(price, p)
        print(f"Input={price}  p={p:02d}%  ->  With={with_nds}  Without={without_nds}")
