import json
import os
import pandas as pd
import numpy as np
import time
import win32com.client as win32
from itertools import permutations
from concurrent.futures import ProcessPoolExecutor


# Step 4: Move LineupOptimizer class outside of the parse_and_optimize_lineup function
class LineupOptimizer:
    def __init__(self, bdnrp_data, players, constraints=None, player_handedness=None, handedness_constraint=None):
        """Initialize the lineup optimizer with BDNRP data and player list."""
        self.bdnrp_data = bdnrp_data
        self.players = players
        self.constraints = constraints if constraints else {player: 10 for player in players}
        self.player_handedness = player_handedness if player_handedness else {player: "R" for player in players}
        self.handedness_constraint = handedness_constraint or {}
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
            if position >= 1 and position <= 9:  # This is a fixed position constraint
                if position in used_positions:
                    raise ValueError(f"Position {position} is assigned to multiple players: {used_positions[position]} and {player}")
                used_positions[position] = player
   
    def _create_bdnrp_lookup(self):
        """Create an efficient lookup structure for BDNRP values."""
        lookup = {}
        for _, row in self.bdnrp_data.iterrows():
            key = (row['player1'], row['player2'], row['player3'], row['player4'])
            lookup[key] = row['bdnrp_value']
        return lookup
   
    def _get_bdnrp(self, p1, p2, p3, p4):
        """Get the BDNRP value for a specific 4-tuple."""
        key = (p1, p2, p3, p4)
        return self.bdnrp_lookup.get(key, 0.0)
   
    def _check_handedness_constraint(self, lineup):
        """Check if a lineup satisfies the handedness constraint."""
        if not self.handedness_constraint:
            return True  # No constraint, always satisfied
       
        max_consecutive_right = self.handedness_constraint.get('max_consecutive_right')
        max_consecutive_left = self.handedness_constraint.get('max_consecutive_left')
       
        if not max_consecutive_right and not max_consecutive_left:
            return True  # No specific constraints set
       
        # Check for consecutive right-handed batters
        if max_consecutive_right:
            consecutive_right = 0
            for player in lineup:
                if self.player_handedness.get(player) == "R":
                    consecutive_right += 1
                    if consecutive_right > max_consecutive_right:
                        return False
                else:
                    consecutive_right = 0
           
            # Need to check for wraparound (last batter to first batter)
            if max_consecutive_right < 9:  # Only check if constraint is less than full lineup
                # Count consecutive right-handed batters across the end/start boundary
                boundary_consecutive = 0
                # Start from the end of the lineup and go backward
                for i in range(len(lineup) - 1, -1, -1):
                    if self.player_handedness.get(lineup[i]) == "R":
                        boundary_consecutive += 1
                    else:
                        break
               
                # Continue from the start of the lineup
                for i in range(len(lineup)):
                    if self.player_handedness.get(lineup[i]) == "R":
                        boundary_consecutive += 1
                        if boundary_consecutive > max_consecutive_right:
                            return False
                    else:
                        break
       
        # Check for consecutive left-handed batters (same logic as above)
        if max_consecutive_left:
            consecutive_left = 0
            for player in lineup:
                if self.player_handedness.get(player) == "L":
                    consecutive_left += 1
                    if consecutive_left > max_consecutive_left:
                        return False
                else:
                    consecutive_left = 0
           
            # Check for wraparound
            if max_consecutive_left < 9:
                boundary_consecutive = 0
                for i in range(len(lineup) - 1, -1, -1):
                    if self.player_handedness.get(lineup[i]) == "L":
                        boundary_consecutive += 1
                    else:
                        break
               
                for i in range(len(lineup)):
                    if self.player_handedness.get(lineup[i]) == "L":
                        boundary_consecutive += 1
                        if boundary_consecutive > max_consecutive_left:
                            return False
                    else:
                        break
       
        return True
   
    def evaluate_lineup(self, lineup):
        """Calculate the expected run production for a given lineup."""
        # Check if lineup satisfies position constraints
        for i, player in enumerate(lineup):
            position = i + 1  # Convert to 1-based position
            constraint = self.constraints.get(player, 10)
            if constraint >= 1 and constraint <= 9 and constraint != position:
                # This player has a constraint that isn't satisfied
                return float('-inf')
       
        # Check handedness constraint
        if not self._check_handedness_constraint(lineup):
            return float('-inf')
       
        total_score = 0.0
        # For each position in the lineup, consider it as the fourth position in a 4-tuple
        for i in range(9):
            # Get the three preceding batters (wrap around if necessary)
            p1 = lineup[(i-3) % 9]
            p2 = lineup[(i-2) % 9]
            p3 = lineup[(i-1) % 9]
            p4 = lineup[i]
           
            # Calculate the basic BDNRP contribution
            position_score = self._get_bdnrp(p1, p2, p3, p4)
           
            # Factor in the probability of an extra at-bat based on lineup position
            extra_ab_probability = (8 - i) / 9 if i < 8 else 0
            position_weight = 1.0 + extra_ab_probability
           
            # Apply the position weight to the BDNRP value
            total_score += position_score * position_weight
       
        return total_score

    # Define process_batch as a static method to avoid pickling issues
    @staticmethod
    def _process_batch_static(batch, lookup_data, constraints, player_handedness, handedness_constraint):
        """Process a batch of lineups and return the best one."""
        # Create a temporary optimizer instance for this batch
        temp_optimizer = LineupOptimizer(
            lookup_data,
            list(set([player for lineup in batch for player in lineup])),
            constraints,
            player_handedness,
            handedness_constraint
        )
       
        best_in_batch = None
        best_score_in_batch = float('-inf')
       
        for lineup in batch:
            score = temp_optimizer.evaluate_lineup(lineup)
            if score > best_score_in_batch:
                best_score_in_batch = score
                best_in_batch = lineup
       
        return best_in_batch, best_score_in_batch
   
    def _process_batch(self, batch):
        """Create data for static batch processing method"""
        return LineupOptimizer._process_batch_static(
            batch,
            self.bdnrp_data,
            self.constraints,
            self.player_handedness,
            self.handedness_constraint
        )
   
    def _generate_valid_lineups(self):
        """Generate only lineups that satisfy fixed position constraints."""
        # Sort players into fixed and flexible groups
        fixed_players = {}
        flexible_players = []
       
        for player in self.players:
            constraint = self.constraints.get(player, 10)
            if constraint >= 1 and constraint <= 9:
                fixed_players[constraint] = player
            else:
                flexible_players.append(player)
       
        # Create a template lineup with fixed players in place
        template = [None] * 9
        for position, player in fixed_players.items():
            template[position - 1] = player
       
        # Generate permutations of the flexible players
        for flex_permutation in permutations(flexible_players):
            # Fill in the template
            result = list(template)
            flex_idx = 0
           
            for i in range(9):
                if result[i] is None:
                    result[i] = flex_permutation[flex_idx]
                    flex_idx += 1
           
            yield result
   
    def optimize(self, method='exhaustive', batch_size=10000):
        """Find the optimal lineup based on BDNRP values."""
        start_time = time.time()
        self.evaluated_lineups = 0
       
        if method == 'exhaustive':
            return self._optimize_exhaustive(batch_size)
        else:
            raise ValueError(f"Method {method} is not supported in this function.")
   
    def _optimize_exhaustive(self, batch_size=10000):
        """Exhaustively evaluate all possible lineups that satisfy constraints."""
        start_time = time.time()
       
        # Check if we have fixed position constraints
        has_constraints = any(pos >= 1 and pos <= 9 for pos in self.constraints.values())
       
        if has_constraints:
            # Generate only valid lineups that satisfy constraints
            all_lineups = list(self._generate_valid_lineups())
        else:
            # No constraints, generate all permutations
            all_lineups = list(permutations(self.players, 9))
       
        total_lineups = len(all_lineups)
        print(f"Evaluating {total_lineups:,} possible lineups...")
       
        # Process lineups in batches (serially to avoid multiprocessing issues)
        best_lineup = None
        best_score = float('-inf')
       
        for i in range(0, total_lineups, batch_size):
            batch = all_lineups[i:i+batch_size]
            lineup, score = self._process_batch(batch)
           
            if score > best_score:
                best_score = score
                best_lineup = lineup
           
            # Update progress
            self.evaluated_lineups += len(batch)
            if (i + batch_size) % (batch_size * 10) == 0 or i + batch_size >= total_lineups:
                progress = min(100, (i + batch_size) / total_lineups * 100)
                elapsed = time.time() - start_time
                print(f"Progress: {progress:.1f}% ({self.evaluated_lineups:,}/{total_lineups:,}) - Elapsed: {elapsed:.1f}s")
       
        self.best_lineup = best_lineup
        self.best_score = best_score
       
        print(f"Optimization complete. Evaluated {self.evaluated_lineups:,} lineups in {time.time() - start_time:.1f}s")
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
       
        return pd.DataFrame(stats)


def setup_excel(file_path):
    """Connect to Excel and open the workbook."""
    excel = win32.Dispatch('Excel.Application')
    excel.Visible = False  # Run Excel in the background
    workbook = excel.Workbooks.Open(file_path)
    sheet = workbook.Sheets("4 Tuple Values 0 Outs")
    return excel, workbook, sheet


def get_bdnrp_from_excel(sheet, p1, p2, p3, p4, player_stats):
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
   
    # Allow time for Excel to recalculate
    time.sleep(0.1)
   
    # Get the calculated BDNRP value
    bdnrp = sheet.Range("H103").Value
    return bdnrp


def generate_bdnrp_data(players, player_stats, excel_file_path, output_csv=None):
    """Generate BDNRP data for all player combinations using Excel."""
    # Check if we already have cached BDNRP data
    if output_csv and os.path.exists(output_csv):
        print(f"Loading pre-calculated BDNRP data from {output_csv}")
        return pd.read_csv(output_csv)
   
    excel, workbook, sheet = setup_excel(excel_file_path)
    try:
        bdnrp_tuples = []
        total_combinations = 0
       
        # Count total valid combinations for progress tracking
        for p1 in players:
            for p2 in players:
                for p3 in players:
                    for p4 in players:
                        if len({p1, p2, p3, p4}) == 4:  # All players must be different
                            total_combinations += 1
       
        # Process each combination
        processed = 0
        print(f"Generating BDNRP data for {total_combinations} combinations...")
       
        for p1 in players:
            for p2 in players:
                for p3 in players:
                    for p4 in players:
                        if len({p1, p2, p3, p4}) == 4:  # All players must be different
                            # Get BDNRP for this combination with all player stats
                            bdnrp = get_bdnrp_from_excel(sheet, p1, p2, p3, p4, player_stats)
                           
                            bdnrp_tuples.append({
                                'player1': p1,
                                'player2': p2,
                                'player3': p3,
                                'player4': p4,
                                'bdnrp_value': bdnrp
                            })
                           
                            # Update progress
                            processed += 1
                            if processed % 50 == 0 or processed == total_combinations:
                                progress = (processed / total_combinations) * 100
                                print(f"Progress: {progress:.1f}% ({processed}/{total_combinations})")
       
        # Create the DataFrame
        bdnrp_data = pd.DataFrame(bdnrp_tuples)
       
        # Save to CSV if requested
        if output_csv:
            bdnrp_data.to_csv(output_csv, index=False)
            print(f"BDNRP data saved to {output_csv}")
       
        return bdnrp_data
   
    finally:
        # Clean up Excel resources
        workbook.Close(SaveChanges=False)
        excel.Quit()


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
              and 'expected runs' key with the expected runs per game
    """
    # Extract handedness constraints directly from the JSON input
    handedness_constraint = {}
    if "max_consecutive_right" in json_input:
        handedness_constraint["max_consecutive_right"] = json_input["max_consecutive_right"]
    if "max_consecutive_left" in json_input:
        handedness_constraint["max_consecutive_left"] = json_input["max_consecutive_left"]
   
    # Print handedness constraints if they exist
    if handedness_constraint:
        print("Handedness constraints applied:")
        if "max_consecutive_right" in handedness_constraint:
            print(f" - Maximum consecutive right-handed batters: {handedness_constraint['max_consecutive_right']}")
        if "max_consecutive_left" in handedness_constraint:
            print(f" - Maximum consecutive left-handed batters: {handedness_constraint['max_consecutive_left']}")
   
    # Step 1: Extract player information from JSON
    players = []
    player_stats = {}
    constraints = {}
    player_handedness = {}  # dictionary to store player batting hand (R/L/S)
   
    # Fixed positions (1-9)
    for pos in range(1, 10):
        pos_key = str(pos)
        if (pos_key in json_input and json_input[pos_key] is not None and
            json_input[pos_key]["name"] != "" and json_input[pos_key]["data"] is not None):
            player_data = json_input[pos_key]
            player_name = player_data["name"]
            players.append(player_name)
            player_stats[player_name] = player_data["data"]
            constraints[player_name] = pos
            player_handedness[player_name] = player_data.get("batting_hand", "R")  # Default to right-handed if not specified
   
    # Flexible positions (10-18)
    for pos in range(10, 19):
        pos_key = str(pos)
        if (pos_key in json_input and json_input[pos_key] is not None and
            json_input[pos_key]["name"] != "" and json_input[pos_key]["data"] is not None):
            player_data = json_input[pos_key]
            player_name = player_data["name"]
            players.append(player_name)
            player_stats[player_name] = player_data["data"]
            constraints[player_name] = pos  # Value will be 10+ indicating no constraint
            player_handedness[player_name] = player_data.get("batting_hand", "R")  # Default to right-handed if not specified
   
    # Print player handedness information
    print("\nPlayer batting hands:")
    for player, hand in player_handedness.items():
        print(f" - {player}: {hand}")
   
    # Ensure we have exactly 9 players
    if len(players) != 9:
        raise ValueError(f"Expected 9 players, but found {len(players)}. Please ensure you provide exactly 9 unique players.")
   
    # Step 2: Generate BDNRP data
    print("\nStep 1: Generating BDNRP data...")
    bdnrp_csv = "bdnrp_values.csv"  # Cache file for BDNRP values
    bdnrp_data = generate_bdnrp_data(players, player_stats, excel_file_path, output_csv=bdnrp_csv)
   
    # Step 3: Initialize and run the lineup optimizer
    print("\nStep 2: Initializing lineup optimizer...")
    optimizer = LineupOptimizer(bdnrp_data, players, constraints, player_handedness, handedness_constraint)
   
    print("\nStep 3: Running lineup optimization...")
    best_lineup, best_score = optimizer.optimize(method=method, batch_size=10)  # Use smaller batch size to avoid memory issues
   
    # Step 4: Calculate the unweighted expected run production
    lineup_stats = optimizer.get_lineup_stats()
    base_score = lineup_stats['base_bdnrp'].sum()
   
    # Step 5: Format the result as a JSON object
    result = {}
   
    # Add each player to their position
    for i, player in enumerate(best_lineup):
        position = i + 1
        result[str(position)] = player
   
    # Add the expected runs score (multiplied by 9 innings)
    result["expected runs"] = round(base_score * 9, 4)
   
    print("\n===== OPTIMIZATION RESULTS =====")
    print(f"Best lineup: {best_lineup}")
    print(f"Expected run production per inning: {base_score:.4f}")
    print(f"Expected run production per game: {base_score * 9:.4f}")
   
    return result


# This is the proper way to use multiprocessing in Python
if __name__ == "__main__":
    # Your test_input dictionary and main execution code here
    test_input = {
        "json_input": {
            "1": {"name": "", "data": None, "batting_hand": "R"},
            "2": {"name": "", "data": None, "batting_hand": "R"},
            "3": {
                "name": "Bryce Harper",
                "data": {"pa": 550, "h": 157, "2b": 42, "3b": 0, "hr": 30, "sb": 0, "bb": 65, "hbp": 2, "ibb": 11},
                "batting_hand": "LEFT"
            },
            "4": {
                "name": "Alec Bohm",
                "data": {"pa": 554, "h": 155, "2b": 44, "3b": 2, "hr": 15, "sb": 0, "bb": 38, "hbp": 6, "ibb": 2},
                "batting_hand": "RIGHT"
            },
            # ... rest of the players
            # Add all other players from your original code here
            "5": {"name": "", "data": None, "batting_hand": "R"},
            "6": {"name": "", "data": None, "batting_hand": "R"},
            "7": {"name": "", "data": None, "batting_hand": "R"},
            "8": {"name": "", "data": None, "batting_hand": "R"},
            "9": {"name": "", "data": None, "batting_hand": "R"},
            "10": {
                "name": "Jacob Realmuto",
                "data": {"pa": 380, "h": 101, "2b": 18, "3b": 1, "hr": 14, "sb": 0, "bb": 26, "hbp": 5, "ibb": 1},
                "batting_hand": "RIGHT"
            },
            "11": {
                "name": "Brandon Marsh",
                "data": {"pa": 418, "h": 104, "2b": 17, "3b": 3, "hr": 16, "sb": 0, "bb": 50, "hbp": 2, "ibb": 0},
                "batting_hand": "LEFT"
            },
            "12": {
                "name": "Kyle Schwarber",
                "data": {"pa": 573, "h": 142, "2b": 22, "3b": 0, "hr": 38, "sb": 0, "bb": 102, "hbp": 5, "ibb": 4},
                "batting_hand": "LEFT"
            },
            "13": {
                "name": "Bryson Stott",
                "data": {"pa": 506, "h": 124, "2b": 19, "3b": 2, "hr": 11, "sb": 0, "bb": 52, "hbp": 3, "ibb": 1},
                "batting_hand": "LEFT"
            },
            "14": {
                "name": "Johan Rojas",
                "data": {"pa": 338, "h": 82, "2b": 12, "3b": 3, "hr": 3, "sb": 0, "bb": 13, "hbp": 4, "ibb": 0},
                "batting_hand": "RIGHT"
            },
            "15": {
                "name": "Edmundo Sosa",
                "data": {"pa": 249, "h": 64, "2b": 12, "3b": 4, "hr": 7, "sb": 0, "bb": 13, "hbp": 8, "ibb": 0},
                "batting_hand": "RIGHT"
            },
            "16": {
                "name": "Kody Clemens",
                "data": {"pa": 114, "h": 25, "2b": 9, "3b": 1, "hr": 5, "sb": 0, "bb": 5, "hbp": 1, "ibb": 0},
                "batting_hand": "LEFT"
            }
        },
        "excel_file_path": r"C:\Users\buman\OneDrive\Desktop\Lineup_Optimization\Copy_Of_Lineup_Optimization.xlsx",
        "method": "exhaustive",
        "max_iterations": 1000
    }
   
    result = parse_and_optimize_lineup(
        json_input=test_input["json_input"],
        excel_file_path=test_input["excel_file_path"],
        method=test_input["method"],
        max_iterations=test_input["max_iterations"]
    )
   
    print(result)