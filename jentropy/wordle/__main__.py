import logging
import os

import jentropy.wordle as w

LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG').upper()
logging.basicConfig(level=LOGLEVEL)


def gen_pat(pat) -> int:
    s = 0
    for i in range(len(pat)):
        s += pat[i] * (3**i)
    return s


def print_by_pattern(wpar: str, partnum: int) -> None:
    words = wor.words_in_part(wpar, partnum)
    size = len(words)

    print(f'----{wpar}----({partnum})-----')
    print(f'size: {size}')
    for w2 in words:
        p = wor._partnum(wpar, w2)
        if size < 5:
            print(f'{wpar} {w.WordleChrRes.from_int(p)} {w2} ({p})')
        else:
            size -= 1


def basic_test(w1: str) -> None:
    print('--------------------------------')
    entropy = wor.entropy_word(w1)
    print(f'Entropy {w1} = {entropy}')

    partnum = gen_pat([2, 0, 0, 1, 2])  # 3
    print_by_pattern(w1, partnum)

    partnum = gen_pat([1, 1, 0, 1, 0])  # 35
    print_by_pattern(w1, partnum)

    partnum = gen_pat([0, 2, 0, 1, 0])  # 273
    print_by_pattern(w1, partnum)
    print('--------------------------------\n')


def basic_words_test() -> None:
    basic_test('weary')     # 4.90, 3, 35, 273
    basic_test('slate')     # 5.87, ...
    basic_test('tares')     # 6.19, ...


def next_wor(wor: w.Wordle, guess: str, pat: int) -> None:
    wor.next_step(guess, pat)
    s = wor.entropy_series()

    if s is None:
        exit(0)

    print(f'Remain {len(wor.words)} possibilities.')
    print('*******************************')
    print(s.head(3))
    print('*******************************')

    if len(wor.words) < 5:
        print(f'The answer is in {wor.words}')

    print('-------------------------------')


def start_wor(wor: w.Wordle) -> None:
    s = wor.entropy_series_allowed()

    if s is None:
        exit(0)

    print(f'Remain {len(wor.words)} possibilities.')
    print('*******************************')
    print(s.head(3))
    print('*******************************')
    print('-------------------------------')


if __name__ == "__main__":
    # en5-nytimes
    wor = w.Wordle()
    start_wor(wor)
    next_wor(wor, 'slate', gen_pat([1, 0, 1, 0, 0]))
    next_wor(wor, 'rains', gen_pat([0, 1, 0, 0, 2]))
    next_wor(wor, 'kombu', gen_pat([0, 0, 0, 1, 0]))
    # abbas, abyss

    # en5-wordlegame
    # wor = w.Wordle('en5-wordlegame.txt')
    # start_wor(wor)
    # next_wor(wor, 'tares', gen_pat([0, 0, 0, 1, 0]))
    # next_wor(wor, 'doily', gen_pat([0, 0, 1, 2, 0]))
    # next_wor(wor, 'micks', gen_pat([0, 2, 0, 0, 0]))

    # pt5-wordlegame
    # start_wor(wor)
    # wor = w.Wordle('pt5-wordlegame.txt')
    # next_wor(wor, 'eirao', gen_pat([0, 0, 2, 1, 2]))
    # next_wor(wor, 'pcdob', gen_pat([0, 1, 0, 1, 1]))
    # the anaswer is barco
