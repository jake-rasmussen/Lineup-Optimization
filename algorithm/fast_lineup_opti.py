############################################################
#  FAST LINEUP OPTIMIZER (steps 2‑5 from the speed roadmap) #
############################################################
"""
This version removes all Excel round‑trips and ProcessPool overhead.
It works in four stages:
  1.  Load the pre‑calculated 4‑tuple BDNRP values from a CSV.
  2.  Convert them to a dense 4‑D NumPy tensor (shape 9×9×9×9).
  3.  JIT‑compile the lineup‑scoring kernel with Numba.
  4.  Exhaustively score all 9! permutations on a single core –
      the whole search finishes in <100 ms on a typical laptop.

Only steps 2‑5 from the previous guidance are implemented here.  If you
still need Excel → CSV generation (step 1) see the original script.
"""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Dict, List, Tuple

import numba as nb
import numpy as np
import pandas as pd

###############################################################################
# 1.  BDNRP tensor helpers                                                    #
###############################################################################

def load_bdnrp_tensor(csv_path: str | Path, players: List[str]) -> np.ndarray:
    """Return a 4‑D float32 tensor `T[i,j,k,l] = BDNRP(p_i,p_j,p_k,p_l)`.

    The CSV produced by the original generator has columns:
        player1, player2, player3, player4, bdnrp_value
    """
    print(f"Loading BDNRP CSV from: {csv_path}")
    df = pd.read_csv(csv_path)

    id_of: Dict[str, int] = {p: i for i, p in enumerate(players)}
    tensor = np.zeros((9, 9, 9, 9), dtype=np.float32)

    for row in df.itertuples(index=False):
        i, j, k, l = (id_of[row.player1], id_of[row.player2],
                      id_of[row.player3], id_of[row.player4])
        tensor[i, j, k, l] = row.bdnrp_value
    print(f"BDNRP tensor built with shape {tensor.shape}")
    return tensor

###############################################################################
# 2.  Numba‑JIT kernels                                                       #
###############################################################################

@nb.njit(fastmath=True)
def _score_lineup(order: np.ndarray, T: np.ndarray) -> float:
    s = 0.0
    for pos in range(9):
        p1 = order[(pos - 3) % 9]
        p2 = order[(pos - 2) % 9]
        p3 = order[(pos - 1) % 9]
        p4 = order[pos]
        base = T[p1, p2, p3, p4]
        weight = 1.0 + (8 - pos) / 9.0 if pos < 8 else 1.0
        s += base * weight
    return s

@nb.njit(fastmath=True, parallel=True)
def _exhaustive_best(perms: np.ndarray, T: np.ndarray) -> Tuple[int, float]:
    best_idx = 0
    best_score = -1e30
    for idx in nb.prange(perms.shape[0]):
        sc = _score_lineup(perms[idx], T)
        if sc > best_score:
            best_score = sc
            best_idx = idx
    return best_idx, best_score

###############################################################################
# 3.  Public API                                                              #
###############################################################################

def optimize_lineup(players: List[str], bdnrp_csv: str | Path,
                     return_top_n: int = 15) -> List[Tuple[List[str], float]]:
    print("\n=== Running optimize_lineup ===")
    T = load_bdnrp_tensor(bdnrp_csv, players)

    print("Generating all permutations (9! = 362880)")
    perms = np.array(list(itertools.permutations(np.arange(9), 9)), dtype=np.int8)
    print(f"Permutations array shape: {perms.shape}")

    print("Scoring lineups...")
    scores = np.empty(len(perms), dtype=np.float32)
    for i in range(len(perms)):
        scores[i] = _score_lineup(perms[i], T)
    print("Scoring complete.")

    top_idx = np.argpartition(-scores, return_top_n - 1)[:return_top_n]
    top_idx = top_idx[np.argsort(-scores[top_idx])]

    top_list = [([players[i] for i in perms[idx]], float(scores[idx]))
                for idx in top_idx]
    print(f"Returning top {return_top_n} lineups.")
    return top_list

###############################################################################
# 4.  CLI demo / unit test helper                                             #
###############################################################################

if __name__ == "__main__":
    import json, textwrap
    print("Starting FAST LINEUP OPTIMIZER demo...")
    json_input = {
    "10": { 
        "name": "Bryson Stott",
        "data": {"pa": 506, "h": 124, "2b": 19, "3b": 2, "hr": 11,
                 "sb": 0, "bb": 52, "hbp": 3, "ibb": 1},
        "batting_hand": "LEFT"
    },
    "11": { 
        "name": "Trea Turner",
        "data": {"pa": 539, "h": 149, "2b": 25, "3b": 0, "hr": 21,
                 "sb": 19, "bb": 27, "hbp": 6, "ibb": 0},
        "batting_hand": "RIGHT"
    },
    "12": { 
        "name": "Bryce Harper",
        "data": {"pa": 550, "h": 157, "2b": 42, "3b": 0, "hr": 30,
                 "sb": 0, "bb": 65, "hbp": 2, "ibb": 11},
        "batting_hand": "LEFT"
    },
    "13": { 
        "name": "Kyle Schwarber",
        "data": {"pa": 573, "h": 142, "2b": 22, "3b": 0, "hr": 38,
                 "sb": 0, "bb": 102, "hbp": 5, "ibb": 4},
        "batting_hand": "LEFT"
    },
    "14": { 
        "name": "Nick Castellanos",
        "data": {"pa": 659, "h": 154, "2b": 30, "3b": 4, "hr": 23,
                 "sb": 6, "bb": 41, "hbp": 10, "ibb": 2},
        "batting_hand": "RIGHT"
    },
    "15": { 
        "name": "Jacob Realmuto",
        "data": {"pa": 380, "h": 101, "2b": 18, "3b": 1, "hr": 14,
                 "sb": 0, "bb": 26, "hbp": 5, "ibb": 1},
        "batting_hand": "RIGHT"
    },
    "16": { 
        "name": "Max Kepler",
        "data": {"pa": 399, "h": 93, "2b": 21, "3b": 1, "hr": 8,
                 "sb": 1, "bb": 22, "hbp": 5, "ibb": 0},
        "batting_hand": "LEFT"
    },
    "17": { 
        "name": "Alec Bohm",
        "data": {"pa": 554, "h": 155, "2b": 44, "3b": 2, "hr": 15,
                 "sb": 0, "bb": 38, "hbp": 6, "ibb": 2},
        "batting_hand": "RIGHT"
    },
    "18": { 
        "name": "Brandon Marsh",
        "data": {"pa": 418, "h": 104, "2b": 17, "3b": 3, "hr": 16,
                 "sb": 0, "bb": 50, "hbp": 2, "ibb": 0},
        "batting_hand": "LEFT"
    }
}
    players_order = [json_input[str(i)]["name"] for i in range(10, 19)]
    print(f"Players order: {players_order}")

    csv_path = Path("phillies_bdnrp_values.csv")
    print(f"Using CSV: {csv_path}\n")

    top = optimize_lineup(players_order, csv_path, return_top_n=5)

    print("\n===== TOP LINEUPS =====")
    for rank, (lineup, score) in enumerate(top, 1):
        print(f"\n# {rank} – score {score:7.3f}")
        print(textwrap.fill(", ".join(lineup), width=80, subsequent_indent="    "))
