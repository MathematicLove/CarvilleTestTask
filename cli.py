import sys
from decimal import Decimal
from nds import calc, calc_prices_via_mod, calc_prices_binary_search, calc_prices_bruteforce_window

HELP = """\
Упс! Не так, не так... Надо так:
  python cli.py <сНДС> <целое 0...99> [алгоритм]
Пример:
  python cli.py 1.81 20
"""

def main(argv):
    if len(argv) < 3:
        print(HELP)
        return 1

    price = argv[1]
    try:
        # просто проверим, в библиотеке все равно идет через Decimal(str(...))
        Decimal(price)
    except Exception:
        print("Неверное значение цены!!!")
        return 2

    try:
        p = int(argv[2])
    except Exception:
        print("Неверное значение процента НДС :( Нужно целое 0..99!!!")
        return 3

    variant = argv[3] if len(argv) >= 4 else "optimal"
    if variant not in {"optimal","mod","bin","brute"}:
        print("Усп... Я такого варианта не писал: Выберите из: optimal | mod | bin | brute")
        return 4

    if variant == "optimal":
        with_nds, without_nds = calc(price, p)
    elif variant == "mod":
        with_nds, without_nds = calc_prices_via_mod(price, p)
    elif variant == "bin":
        with_nds, without_nds = calc_prices_binary_search(price, p)
    else:
        with_nds, without_nds = calc_prices_bruteforce_window(price, p, window=8)

    print(f"CorrectedPriceWithNDS = {with_nds}")
    print(f"CorrectedPriceWithoutNDS = {without_nds}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
