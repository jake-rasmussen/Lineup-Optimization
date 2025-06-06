"""
Fast Lineup Optimizer
High-performance lineup optimization using NumPy tensors and Numba JIT compilation.
"""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Dict, List, Tuple

import numba as nb
import numpy as np
import pandas as pd


def load_bdnrp_tensor(csv_path: str | Path, players: List[str]) -> np.ndarray:
    """
    Load BDNRP values from CSV and convert to 4D NumPy tensor.
    
    Args:
        csv_path: Path to CSV file containing BDNRP values
        players: List of player names in order
        
    Returns:
        4D float32 tensor where T[i,j,k,l] = BDNRP(player_i, player_j, player_k, player_l)
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


@nb.njit(fastmath=True)
def _score_lineup(order: np.ndarray, T: np.ndarray) -> float:
    """
    Calculate the total score for a lineup using the BDNRP tensor.
    
    Args:
        order: Array of player indices representing batting order
        T: 4D BDNRP tensor
        
    Returns:
        Total weighted score for the lineup
    """
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
    """
    Find the best lineup from all permutations using parallel processing.
    
    Args:
        perms: Array of all permutations to evaluate
        T: 4D BDNRP tensor
        
    Returns:
        Tuple of (best_index, best_score)
    """
    best_idx = 0
    best_score = -1e30
    for idx in nb.prange(perms.shape[0]):
        sc = _score_lineup(perms[idx], T)
        if sc > best_score:
            best_score = sc
            best_idx = idx
    return best_idx, best_score


def optimize_lineup(players: List[str], 
                   bdnrp_csv: str | Path,
                   return_top_n: int = 15) -> List[Tuple[List[str], float]]:
    """
    Optimize batting lineup using exhaustive search with JIT compilation.
    
    Args:
        players: List of player names
        bdnrp_csv: Path to CSV file containing BDNRP values
        return_top_n: Number of top lineups to return
        
    Returns:
        List of tuples containing (lineup_names, score) sorted by score descending
    """
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


def get_lineup_score(players: List[str], 
                    lineup_order: List[str], 
                    bdnrp_csv: str | Path) -> float:
    """
    Calculate the score for a specific lineup order.
    
    Args:
        players: List of all available players
        lineup_order: Specific batting order to evaluate
        bdnrp_csv: Path to CSV file containing BDNRP values
        
    Returns:
        Score for the given lineup
        
    Raises:
        ValueError: If lineup_order contains players not in players list
    """
    if not all(player in players for player in lineup_order):
        raise ValueError("All players in lineup_order must be in players list")
    
    T = load_bdnrp_tensor(bdnrp_csv, players)
    player_to_idx = {player: idx for idx, player in enumerate(players)}
    order_indices = np.array([player_to_idx[player] for player in lineup_order], dtype=np.int8)
    
    return float(_score_lineup(order_indices, T))


def compare_lineups(players: List[str], 
                   lineups: List[List[str]], 
                   bdnrp_csv: str | Path) -> List[Tuple[List[str], float]]:
    """
    Compare multiple specific lineups and return them sorted by score.
    
    Args:
        players: List of all available players
        lineups: List of batting orders to compare
        bdnrp_csv: Path to CSV file containing BDNRP values
        
    Returns:
        List of tuples containing (lineup, score) sorted by score descending
    """
    T = load_bdnrp_tensor(bdnrp_csv, players)
    player_to_idx = {player: idx for idx, player in enumerate(players)}
    
    results = []
    for lineup in lineups:
        if not all(player in players for player in lineup):
            raise ValueError(f"Lineup contains players not in available players list: {lineup}")
        
        order_indices = np.array([player_to_idx[player] for player in lineup], dtype=np.int8)
        score = float(_score_lineup(order_indices, T))
        results.append((lineup, score))
    
    return sorted(results, key=lambda x: x[1], reverse=True)