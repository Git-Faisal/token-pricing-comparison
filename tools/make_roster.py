"""Verify the driver-roster constraint problem has EXACTLY ONE solution.

The roster task in tasks.py ships this instance. Run this script to check:
it exhaustively enumerates every assignment satisfying the constraints and
asserts there is exactly one.

Instance
--------
Drivers: Salem, Layla, Fahad, Omar, Noura.
Slots: Sunday..Thursday x {day, night} = 10 slots, exactly 2 drivers each.

C1.  Exactly 2 drivers per shift.
C2.  Exact weekly shift counts: Salem 4, Layla 4, Fahad 3, Omar 5, Noura 4.
C3.  Rest rule: a driver who works a night shift cannot work the next
     morning's day shift.
C4.  Every shift needs >=1 refrigerated-certified driver: Salem, Layla, Noura.
C5.  Night shifts require a forklift licence; Fahad has none (no nights).
C6.  Fahad is unavailable on Wednesday.
C7.  Noura and Fahad must never share a shift.
C8.  Nobody works both shifts of the same day.
C9.  Layla cannot work night shifts (evening classes).
C10. Noura must work exactly 2 night shifts.
C11. Salem cannot work the Sunday day shift.
"""

from itertools import combinations

DAYS = ["sun", "mon", "tue", "wed", "thu"]
SLOTS = [f"{d}_{s}" for d in DAYS for s in ("day", "night")]
DRIVERS = ["Salem", "Layla", "Fahad", "Omar", "Noura"]
CERTIFIED = {"Salem", "Layla", "Noura"}
QUOTA = {"Salem": 4, "Layla": 4, "Fahad": 3, "Omar": 5, "Noura": 4}


def slot_options(slot):
    day, kind = slot.split("_")
    opts = []
    for pair in combinations(DRIVERS, 2):
        s = set(pair)
        if not s & CERTIFIED:
            continue                                    # C4
        if kind == "night" and "Fahad" in s:
            continue                                    # C5
        if kind == "night" and "Layla" in s:
            continue                                    # C9
        if day == "wed" and "Fahad" in s:
            continue                                    # C6
        if {"Noura", "Fahad"} <= s:
            continue                                    # C7
        if slot == "sun_day" and "Salem" in s:
            continue                                    # C11
        opts.append(s)
    return opts


OPTIONS = {slot: slot_options(slot) for slot in SLOTS}
nodes = 0
solutions = []


def backtrack(i, assigned, counts, noura_nights):
    global nodes
    if len(solutions) > 5:
        return
    if i == len(SLOTS):
        if (all(counts[d] == QUOTA[d] for d in DRIVERS) and noura_nights == 2):
            solutions.append(dict(assigned))
        return
    slot = SLOTS[i]
    day, kind = slot.split("_")
    day_idx = DAYS.index(day)
    for pair in OPTIONS[slot]:
        nodes += 1
        if kind == "night" and pair & assigned.get(f"{day}_day", set()):
            continue                                    # C8
        if kind == "day" and day_idx > 0:
            if pair & assigned.get(f"{DAYS[day_idx-1]}_night", set()):
                continue                                # C3
        if any(counts[d] + 1 > QUOTA[d] for d in pair):
            continue                                    # C2
        nn = noura_nights + (1 if (kind == "night" and "Noura" in pair) else 0)
        if nn > 2:
            continue                                    # C10
        for d in pair:
            counts[d] += 1
        assigned[slot] = pair
        backtrack(i + 1, assigned, counts, nn)
        del assigned[slot]
        for d in pair:
            counts[d] -= 1


if __name__ == "__main__":
    backtrack(0, {}, {d: 0 for d in DRIVERS}, 0)
    print(f"solutions: {len(solutions)} (search nodes: {nodes})")
    assert len(solutions) == 1, "instance must have exactly one solution!"
    print("\nThe unique roster:")
    for slot in SLOTS:
        print(f"  {slot:<10} {sorted(solutions[0][slot])}")
    print("\nJSON form (grading reference):")
    import json
    print(json.dumps({s: sorted(solutions[0][s]) for s in SLOTS}))
