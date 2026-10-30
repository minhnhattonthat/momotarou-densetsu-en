"""Print an emu.py route for the mode-6 keyboard; cursor starts on A.

    python tools/debug/type_route.py RAISEDWITHCARE "57 -;6 circle;100 -" "60 -"
"""
import sys

ROWS = ['ABCDEFGHIJKLMNO', "PQRSTUVWXYZ',-."]


def route(word, head='', tail=''):
    pos = {c: (r, i) for r, row in enumerate(ROWS) for i, c in enumerate(row)}
    cur, steps = (0, 0), [head] if head else []
    for c in word:
        r, col = pos[c]
        dr, dc = r - cur[0], col - cur[1]
        steps += [f"4 {'down' if dr > 0 else 'up'};8 -"] * abs(dr)
        steps += [f"4 {'right' if dc > 0 else 'left'};8 -"] * abs(dc)
        steps.append('4 circle;12 -')
        cur = (r, col)
    if tail:
        steps.append(tail)
    return ';'.join(steps)


if __name__ == '__main__':
    print(route(*sys.argv[1:]))
