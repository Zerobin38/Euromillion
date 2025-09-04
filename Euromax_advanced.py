import random, math, numpy as np

def generate_pool(pool_size=50):
    numbers = list(range(1,51))
    stars = list(range(1,13))
    pool = []
    for _ in range(pool_size):
        nums = tuple(sorted(random.sample(numbers,5)))
        ets = tuple(sorted(random.sample(stars,2)))
        pool.append({"nums": nums, "stars": ets})
    return pool

def evaluate_combo(combo, N_other=1_000_000, J=100_000_000):
    # prob of winning jackpot
    total = math.comb(50,5)*math.comb(12,2)
    p = 1/total
    # expected value (rough estimate, ignoring split)
    EV = p * J
    return {"combo": combo, "p_win": p, "EV": EV}

def run_ga(pool, gens=50, N_other=1_000_000, J=100_000_000):
    best = None
    best_ev = -1
    for _ in range(gens):
        c = random.choice(pool)
        ev = evaluate_combo(c, N_other, J)["EV"]
        if ev > best_ev:
            best_ev = ev
            best = c
    return {"best_combo": best, "EV": best_ev}
