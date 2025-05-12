import json
import os
import pandas as pd
import numpy as np
import time
import win32com.client as win32
from itertools import permutations
from concurrent.futures import ProcessPoolExecutor
import logging

# ------------------------------
# Excel helper functions (module level)
# ------------------------------

def setup_excel(file_path):
    """Connect to Excel and open the workbook."""
    excel = win32.Dispatch('Excel.Application')
    excel.Visible = False  # Run Excel in the background
    workbook = excel.Workbooks.Open(file_path)
    sheet = workbook.Sheets("4 Tuple Values 0 Outs")
    return excel, workbook, sheet

def get_bdnrp_from_excel(sheet, player_stats, p1, p2, p3, p4):
    """Get BDNRP for a specific 4-tuple, setting all player stats in Excel."""
    # Player 1 stats (row 4)
    stats1 = player_stats[p1]
    sheet.Range("D4").Value = p1
    sheet.Range("H4").Value = stats1["pa"]
    sheet.Range("K4").Value = stats1["h"]
    sheet.Range("L4").Value = stats1["2b"]
    sheet.Range("M4").Value = stats1["3b"]
    sheet.Range("N4").Value = stats1["hr"]
    sheet.Range("P4").Value = stats1["sb"]
    sheet.Range("R4").Value = stats1["bb"]
    sheet.Range("AA4").Value = stats1["hbp"]
    sheet.Range("AD4").Value = stats1["ibb"]

    # Player 2 stats (row 11)
    stats2 = player_stats[p2]
    sheet.Range("D11").Value = p2
    sheet.Range("H11").Value = stats2["pa"]
    sheet.Range("K11").Value = stats2["h"]
    sheet.Range("L11").Value = stats2["2b"]
    sheet.Range("M11").Value = stats2["3b"]
    sheet.Range("N11").Value = stats2["hr"]
    sheet.Range("P11").Value = stats2["sb"]
    sheet.Range("R11").Value = stats2["bb"]
    sheet.Range("AA11").Value = stats2["hbp"]
    sheet.Range("AD11").Value = stats2["ibb"]

    # Player 3 stats (row 18)
    stats3 = player_stats[p3]
    sheet.Range("D18").Value = p3
    sheet.Range("H18").Value = stats3["pa"]
    sheet.Range("K18").Value = stats3["h"]
    sheet.Range("L18").Value = stats3["2b"]
    sheet.Range("M18").Value = stats3["3b"]
    sheet.Range("N18").Value = stats3["hr"]
    sheet.Range("P18").Value = stats3["sb"]
    sheet.Range("R18").Value = stats3["bb"]
    sheet.Range("AA18").Value = stats3["hbp"]
    sheet.Range("AD18").Value = stats3["ibb"]

    # Player 4 stats (row 27)
    stats4 = player_stats[p4]
    sheet.Range("D27").Value = p4
    sheet.Range("H27").Value = stats4["pa"]
    sheet.Range("K27").Value = stats4["h"]
    sheet.Range("L27").Value = stats4["2b"]
    sheet.Range("M27").Value = stats4["3b"]
    sheet.Range("N27").Value = stats4["hr"]
    sheet.Range("P27").Value = stats4["sb"]
    sheet.Range("R27").Value = stats4["bb"]
    sheet.Range("AA27").Value = stats4["hbp"]
    sheet.Range("AD27").Value = stats4["ibb"]

    # Allow time for Excel to recalculate (increased delay for testing)
    time.sleep(0.5)
    # Get the calculated BDNRP value
    bdnrp = sheet.Range("H103").Value
    print(f"DEBUG: Computed BDNRP for tuple ({p1}, {p2}, {p3}, {p4}): {bdnrp}")
    return bdnrp

def generate_bdnrp_data(excel_file_path, players, player_stats, output_csv=None):
    """Generate BDNRP data for all player combinations using Excel."""
    if output_csv and os.path.exists(output_csv):
        print(f"DEBUG: Loading pre-calculated BDNRP data from {output_csv}")
        df = pd.read_csv(output_csv)
        print(f"DEBUG: Loaded BDNRP data shape: {df.shape}")
        print(df.head())
        return df
    
    excel, workbook, sheet = setup_excel(excel_file_path)
    
    try:
        bdnrp_tuples = []
        total_combinations = 0
        
        # Count total valid combinations for progress tracking
        for p1 in players:
            for p2 in players:
                for p3 in players:
                    for p4 in players:
                        if len({p1, p2, p3, p4}) == 4:
                            total_combinations += 1
        
        processed = 0
        print(f"DEBUG: Generating BDNRP data for {total_combinations} combinations...")
        
        for p1 in players:
            for p2 in players:
                for p3 in players:
                    for p4 in players:
                        if len({p1, p2, p3, p4}) == 4:
                            bdnrp = get_bdnrp_from_excel(sheet, player_stats, p1, p2, p3, p4)
                            bdnrp_tuples.append({
                                'player1': p1,
                                'player2': p2,
                                'player3': p3, 
                                'player4': p4,
                                'bdnrp_value': bdnrp
                            })
                            processed += 1
                            if processed % 50 == 0 or processed == total_combinations:
                                progress = (processed / total_combinations) * 100
                                print(f"DEBUG: Progress: {progress:.1f}% ({processed}/{total_combinations})")
        
        bdnrp_data = pd.DataFrame(bdnrp_tuples)
        
        if output_csv:
            bdnrp_data.to_csv(output_csv, index=False)
            print(f"DEBUG: BDNRP data saved to {output_csv}")
        
        return bdnrp_data
    finally:
        workbook.Close(SaveChanges=False)
        excel.Quit()

# ------------------------------
# LineupOptimizer class defined at module level
# ------------------------------

class LineupOptimizer:
    def __init__(self, bdnrp_data, players, constraints=None):
        """Initialize the lineup optimizer with BDNRP data and player list."""
        self.bdnrp_data = bdnrp_data
        self.players = players
        self.constraints = constraints if constraints else {player: 10 for player in players}
        self.best_lineup = None
        self.best_score = float('-inf')
        self.evaluated_lineups = 0
        
        # Validate constraints
        self._validate_constraints()
        
        # Create a lookup dictionary for quick access to BDNRP values
        self.bdnrp_lookup = self._create_bdnrp_lookup()
    
    def _validate_constraints(self):
        """Validate that constraints don't conflict with each other."""
        used_positions = {}
        for player, position in self.constraints.items():
            if position >= 1 and position <= 9:
                if position in used_positions:
                    raise ValueError(f"Position {position} is assigned to multiple players: {used_positions[position]} and {player}")
                used_positions[position] = player
    
    def _create_bdnrp_lookup(self):
        """Create an efficient lookup structure for BDNRP values."""
        lookup = {}
        for _, row in self.bdnrp_data.iterrows():
            key = (row['player1'], row['player2'], row['player3'], row['player4'])
            lookup[key] = row['bdnrp_value']
        print("DEBUG: BDNRP lookup created with", len(lookup), "entries.")
        return lookup
    
    def _get_bdnrp(self, p1, p2, p3, p4):
        """Get the BDNRP value for a specific 4-tuple."""
        key = (p1, p2, p3, p4)
        return self.bdnrp_lookup.get(key, 0.0)
    
    def evaluate_lineup(self, lineup):
        """Calculate the expected run production for a given lineup."""
        for i, player in enumerate(lineup):
            position = i + 1
            constraint = self.constraints.get(player, 10)
            if constraint >= 1 and constraint <= 9 and constraint != position:
                return float('-inf')
        
        total_score = 0.0
        for i in range(9):
            p1 = lineup[(i-3) % 9]
            p2 = lineup[(i-2) % 9]
            p3 = lineup[(i-1) % 9]
            p4 = lineup[i]
            position_score = self._get_bdnrp(p1, p2, p3, p4)
            extra_ab_probability = (8 - i) / 9 if i < 8 else 0
            position_weight = 1.0 + extra_ab_probability
            total_score += position_score * position_weight
        print(f"DEBUG: Lineup {lineup} scored {total_score}")
        return total_score
    
    def _process_batch(self, batch):
        """Process a batch of lineups and return the best one."""
        best_in_batch = None
        best_score_in_batch = float('-inf')
        for lineup in batch:
            score = self.evaluate_lineup(lineup)
            if score > best_score_in_batch:
                best_score_in_batch = score
                best_in_batch = lineup
        return best_in_batch, best_score_in_batch
    
    def _generate_valid_lineups(self):
        """Generate only lineups that satisfy fixed position constraints."""
        fixed_players = {}
        flexible_players = []
        for player in self.players:
            constraint = self.constraints.get(player, 10)
            if constraint >= 1 and constraint <= 9:
                fixed_players[constraint] = player
            else:
                flexible_players.append(player)
        template = [None] * 9
        for position, player in fixed_players.items():
            template[position - 1] = player
        generated = 0
        for flex_permutation in permutations(flexible_players):
            result_lineup = list(template)
            flex_idx = 0
            for i in range(9):
                if result_lineup[i] is None:
                    result_lineup[i] = flex_permutation[flex_idx]
                    flex_idx += 1
            generated += 1
            if generated % 100 == 0:
                print(f"DEBUG: Generated {generated} valid lineups so far...")
            yield result_lineup
    
    def optimize(self, method='exhaustive', batch_size=10000):
        """Find the optimal lineup based on BDNRP values."""
        start_time = time.time()
        self.evaluated_lineups = 0
        
        if method == 'exhaustive':
            best_lineup, best_score = self._optimize_exhaustive(batch_size)
        else:
            raise ValueError(f"Method {method} is not supported in this function.")
        return best_lineup, best_score
    
    def _optimize_exhaustive(self, batch_size=10000):
        """Exhaustively evaluate all possible lineups that satisfy constraints."""
        start_time = time.time()
        has_constraints = any(pos >= 1 and pos <= 9 for pos in self.constraints.values())
        if has_constraints:
            all_lineups = list(self._generate_valid_lineups())
        else:
            from itertools import permutations
            all_lineups = list(permutations(self.players, 9))
        total_lineups = len(all_lineups)
        print(f"DEBUG: Evaluating {total_lineups:,} possible lineups...")
        
        with ProcessPoolExecutor() as executor:
            batch_results = []
            for i in range(0, total_lineups, batch_size):
                batch = all_lineups[i:i+batch_size]
                batch_results.append(executor.submit(self._process_batch, batch))
                self.evaluated_lineups += len(batch)
                if (i + batch_size) % (batch_size * 10) == 0 or i + batch_size >= total_lineups:
                    progress = min(100, (i + batch_size) / total_lineups * 100)
                    elapsed = time.time() - start_time
                    print(f"DEBUG: Progress: {progress:.1f}% ({self.evaluated_lineups:,}/{total_lineups:,}) - Elapsed: {elapsed:.1f}s")
            
            for future in batch_results:
                lineup, score = future.result()
                if score > self.best_score:
                    self.best_score = score
                    self.best_lineup = lineup
        
        elapsed_total = time.time() - start_time
        print(f"DEBUG: Optimization complete. Evaluated {self.evaluated_lineups:,} lineups in {elapsed_total:.1f}s")
        return self.best_lineup, self.best_score
    
    def get_lineup_stats(self, lineup=None):
        """Get detailed statistics for a lineup."""
        if lineup is None:
            if self.best_lineup is None:
                raise ValueError("No lineup available. Run optimize() first.")
            lineup = self.best_lineup
        stats = []
        for i in range(9):
            p1 = lineup[(i-3) % 9]
            p2 = lineup[(i-2) % 9]
            p3 = lineup[(i-1) % 9]
            p4 = lineup[i]
            base_bdnrp = self._get_bdnrp(p1, p2, p3, p4)
            extra_ab_probability = (8 - i) / 9 if i < 8 else 0
            position_weight = 1.0 + extra_ab_probability
            weighted_bdnrp = base_bdnrp * position_weight
            stats.append({
                'position': i+1,
                'player': p4,
                'prev_three': [p1, p2, p3],
                'base_bdnrp': base_bdnrp,
                'weighted_bdnrp': weighted_bdnrp
            })
        df_stats = pd.DataFrame(stats)
        print("DEBUG: Lineup statistics:")
        print(df_stats)
        return df_stats

# ------------------------------
# Main function: parse_and_optimize_lineup
# ------------------------------

def parse_and_optimize_lineup(json_input, excel_file_path, method='exhaustive', max_iterations=1000):
    """
    Parse JSON input containing player data and constraints, optimize the lineup,
    and return the result as a JSON object.
    
    Args:
        json_input (dict): JSON object with positions 1-18 as keys and player objects as values.
                          Each player object contains stats (pa, h, 2b, 3b, hr, sb, bb, hbp, ibb)
        excel_file_path (str): Path to the Excel file for BDNRP calculations
        method (str): Optimization method - 'exhaustive', 'genetic', or 'simulated_annealing'
        max_iterations (int): Maximum iterations for non-exhaustive methods
        
    Returns:
        dict: JSON object with positions 1-9 as keys, player names as values,
              and 'expectedRuns' key with the expected runs per game
    """
    # Separate entries into fixed (keys 1-9 with non-empty name) and flexible (keys >=10 with non-empty name)
    fixed = []
    flexible = []
    for pos in range(1, 19):
        pos_key = str(pos)
        if pos_key in json_input and json_input[pos_key] is not None:
            entry = json_input[pos_key]
            if entry["name"].strip() != "":
                if pos <= 9:
                    fixed.append(entry)
                else:
                    flexible.append(entry)
    print(f"DEBUG: Fixed count: {len(fixed)}; Flexible count: {len(flexible)}")

    # If fixed entries are fewer than 9, fill them from flexible.
    filled_fixed = fixed.copy()
    flexible_index = 0
    while len(filled_fixed) < 9 and flexible_index < len(flexible):
        filled_fixed.append(flexible[flexible_index])
        flexible_index += 1

    if len(filled_fixed) != 9:
        raise ValueError(f"Expected 9 players, but found {len(filled_fixed)} after filling. Please ensure you provide enough players.")

    # Build players list, player_stats mapping, and constraints.
    players = []           # List of player names (for fixed lineup, order matters)
    player_stats = {}      # Map from player name to their data
    constraints = {}       # Map from player name to fixed position (1-9)

    # Use the filled_fixed entries for fixed positions.
    for i, entry in enumerate(filled_fixed):
        pos = i + 1
        players.append(entry["name"])
        player_stats[entry["name"]] = entry["data"]
        constraints[entry["name"]] = pos

    # Add remaining flexible entries (if any) as additional players with no fixed constraint.
    for entry in flexible[flexible_index:]:
        players.append(entry["name"])
        player_stats[entry["name"]] = entry["data"]
        constraints[entry["name"]] = 10  # 10 indicates no fixed constraint

    print(f"DEBUG: Final players list (fixed first): {players}")

    # Ensure we have exactly 9 players for optimization (the fixed lineup).
    if len(players) < 9:
        raise ValueError(f"Expected at least 9 players, but found {len(players)}.")

    # Use only the first 9 players as the fixed lineup.
    fixed_players = players[:9]
    fixed_constraints = {name: constraints[name] for name in fixed_players}
    # For BDNRP generation and optimization, use fixed_players and their stats.
    bdnrp_players = fixed_players
    bdnrp_player_stats = {name: player_stats[name] for name in bdnrp_players}

    print("Step 1: Generating BDNRP data...")
    bdnrp_csv = "bdnrp_values.csv"  # Cache file for BDNRP values

    # Delete the cache file if it exists
    if os.path.exists(bdnrp_csv):
        os.remove(bdnrp_csv)
        print(f"DEBUG: Deleted existing cache file: {bdnrp_csv}")

    bdnrp_data = generate_bdnrp_data(excel_file_path, bdnrp_players, bdnrp_player_stats, output_csv=bdnrp_csv)

    print("\nStep 2: Initializing lineup optimizer...")
    optimizer = LineupOptimizer(bdnrp_data, bdnrp_players, fixed_constraints)

    print("\nStep 3: Running lineup optimization...")
    best_lineup, best_score = optimizer.optimize(method=method)

    # Step 4: Calculate lineup statistics and expected run production.
    lineup_stats = optimizer.get_lineup_stats()
    base_score = lineup_stats['base_bdnrp'].sum()

    # Format the result as a JSON object.
    result = {}
    for i, player in enumerate(best_lineup):
        position = i + 1
        result[str(position)] = player
    result["expectedRuns"] = round(base_score * 9, 4)

    print("\n===== OPTIMIZATION RESULTS =====")
    print(f"Best lineup: {best_lineup}")
    print(f"Expected run production per inning: {base_score:.4f}")
    print(f"Expected run production per game: {base_score * 9:.4f}")

    return result
