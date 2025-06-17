"""
lineup_calculator.py

Fast Lineup Calculator with Handedness and Positional Constraints
High-performance lineup optimization using NumPy tensors and Numba JIT compilation.
"""

from __future__ import annotations

import itertools
from pathlib import Path
from typing import Dict, List, Tuple, Optional

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


def check_handedness_constraints(lineup_indices: np.ndarray, 
                               player_handedness: List[str],
                               max_consecutive_left: int,
                               max_consecutive_right: int) -> bool:
    """
    Check if a lineup violates handedness constraints.
    
    Args:
        lineup_indices: Array of player indices in batting order
        player_handedness: List of handedness for each player ('LEFT', 'RIGHT', 'SWITCH')
        max_consecutive_left: Maximum consecutive left-handed batters (0 = no constraint)
        max_consecutive_right: Maximum consecutive right-handed batters (0 = no constraint)
        
    Returns:
        True if lineup satisfies constraints, False otherwise
    """
    if max_consecutive_left == 0 and max_consecutive_right == 0:
        return True
    
    # Create circular lineup to check wraparound
    extended_lineup = list(lineup_indices) + list(lineup_indices)
    
    consecutive_left = 0
    consecutive_right = 0
    max_left_found = 0
    max_right_found = 0
    
    for i in range(18):  # Check twice around to catch wraparound
        player_idx = extended_lineup[i]
        handedness = player_handedness[player_idx]
        
        if handedness == 'LEFT':
            consecutive_left += 1
            consecutive_right = 0
            max_left_found = max(max_left_found, consecutive_left)
        elif handedness == 'RIGHT':
            consecutive_right += 1
            consecutive_left = 0
            max_right_found = max(max_right_found, consecutive_right)
        else:  # SWITCH hitters break consecutive streaks
            consecutive_left = 0
            consecutive_right = 0
    
    # Check constraints (0 means no constraint)
    if max_consecutive_left > 0 and max_left_found > max_consecutive_left:
        return False
    if max_consecutive_right > 0 and max_right_found > max_consecutive_right:
        return False
    
    return True


def create_constrained_lineups(constrained_positions: Dict[int, int],
                              unconstrained_players: List[int],
                              available_positions: List[int]) -> List[np.ndarray]:
    """
    Generate all valid lineups considering positional constraints.
    
    Args:
        constrained_positions: Dict mapping batting position (0-8) to player index
        unconstrained_players: List of player indices that can be moved
        available_positions: List of batting positions (0-8) available for unconstrained players
        
    Returns:
        List of complete lineup arrays
    """
    if len(unconstrained_players) != len(available_positions):
        raise ValueError(f"Mismatch: {len(unconstrained_players)} unconstrained players but {len(available_positions)} available positions")
    
    # Generate all permutations of unconstrained players in available positions
    unconstrained_perms = list(itertools.permutations(unconstrained_players))
    
    lineups = []
    for perm in unconstrained_perms:
        # Create complete lineup
        lineup = np.full(9, -1, dtype=np.int8)
        
        # Place constrained players
        for pos, player_idx in constrained_positions.items():
            lineup[pos] = player_idx
        
        # Place unconstrained players
        for i, player_idx in enumerate(perm):
            lineup[available_positions[i]] = player_idx
        
        lineups.append(lineup)
    
    return lineups


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
                   return_top_n: int = 15,
                   player_handedness: Optional[List[str]] = None,
                   max_consecutive_left: int = 0,
                   max_consecutive_right: int = 0,
                   constrained_positions: Optional[Dict[int, int]] = None,
                   unconstrained_players: Optional[List[int]] = None,
                   available_positions: Optional[List[int]] = None) -> List[Tuple[List[str], float]]:
    """
    Optimize batting lineup using exhaustive search with positional and handedness constraints.
    
    Args:
        players: List of player names
        bdnrp_csv: Path to CSV file containing BDNRP values
        return_top_n: Number of top lineups to return
        player_handedness: List of handedness for each player ('LEFT', 'RIGHT', 'SWITCH')
        max_consecutive_left: Maximum consecutive left-handed batters (0 = no constraint)
        max_consecutive_right: Maximum consecutive right-handed batters (0 = no constraint)
        constrained_positions: Dict mapping batting position (0-8) to player index
        unconstrained_players: List of player indices that can be moved
        available_positions: List of batting positions (0-8) available for optimization
        
    Returns:
        List of tuples containing (lineup_names, score) sorted by score descending
    """
    print("\n=== Running optimize_lineup ===")
    T = load_bdnrp_tensor(bdnrp_csv, players)

    # Handle positional constraints
    if constrained_positions is not None and unconstrained_players is not None and available_positions is not None:
        print(f"Positional constraints: {len(constrained_positions)} fixed positions, {len(unconstrained_players)} players to optimize")
        print(f"Fixed positions: {list(constrained_positions.keys())}")
        print(f"Available positions for optimization: {available_positions}")
        
        # Generate constrained lineups
        all_lineups = create_constrained_lineups(constrained_positions, unconstrained_players, available_positions)
        total_lineups = len(all_lineups)
        print(f"Generated {total_lineups} constrained lineups")
    else:
        print("Generating all permutations (9! = 362880)")
        all_lineups = [np.array(perm, dtype=np.int8) for perm in itertools.permutations(np.arange(9), 9)]
        total_lineups = len(all_lineups)
        print(f"Generated {total_lineups} unconstrained lineups")
    
    # Filter lineups based on handedness constraints
    if (player_handedness and 
        (max_consecutive_left > 0 or max_consecutive_right > 0)):
        print(f"Applying handedness constraints: max_left={max_consecutive_left}, max_right={max_consecutive_right}")
        valid_lineups = []
        for lineup in all_lineups:
            if check_handedness_constraints(lineup, player_handedness, 
                                          max_consecutive_left, max_consecutive_right):
                valid_lineups.append(lineup)
        all_lineups = valid_lineups
        print(f"Valid lineups after handedness filtering: {len(all_lineups)}")
    else:
        print(f"No handedness constraints applied")
    
    if len(all_lineups) == 0:
        raise ValueError("No valid lineups found with the given constraints")

    # Convert to numpy array for scoring
    perms = np.array(all_lineups, dtype=np.int8)
    print(f"Final permutations array shape: {perms.shape}")

    print("Scoring lineups...")
    scores = np.empty(len(perms), dtype=np.float32)
    for i in range(len(perms)):
        scores[i] = _score_lineup(perms[i], T)
    print("Scoring complete.")

    top_idx = np.argpartition(-scores, min(return_top_n - 1, len(scores) - 1))[:return_top_n]
    top_idx = top_idx[np.argsort(-scores[top_idx])]

    top_list = [([players[i] for i in perms[idx]], float(scores[idx]))
                for idx in top_idx]
    print(f"Returning top {min(return_top_n, len(top_list))} lineups.")
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