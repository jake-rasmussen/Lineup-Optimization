import json
import os
import pandas as pd
import numpy as np
import time
import win32com.client as win32
from itertools import permutations
from concurrent.futures import ProcessPoolExecutor
import heapq  # For tracking top N lineups


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
        
        # New attributes for tracking top lineups
        self.top_lineups = []  # Will store (score, lineup) tuples
        self.top_n = 15  # Number of top lineup cycles to consider
        
        # Validate constraints
        self._validate_constraints()
        
        # Create a lookup dictionary for quick access to BDNRP values
        self.bdnrp_lookup = self._create_bdnrp_lookup()
        
        # Store leadoff and second at-bat BRP values
        self.leadoff_brp = {}  # Will be populated if available
        self.second_ab_brp = {}  # Will be populated if available
    
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
    
    def set_leadoff_brp_data(self, leadoff_data):
        """Set the leadoff BRP data for players."""
        self.leadoff_brp = leadoff_data
    
    def set_second_ab_brp_data(self, second_ab_data):
        """Set the second at-bat BRP data for players."""
        self.second_ab_brp = second_ab_data
    
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

    def evaluate_lineup_with_leadoff(self, lineup, leadoff_index):
        """
        Evaluate a lineup with a specific player leading off.
        Adjusts the lineup by making the player at leadoff_index the first batter.
        
        Args:
            lineup: The original lineup
            leadoff_index: The index (0-8) of the player who should lead off
        
        Returns:
            score: The adjusted score with leadoff considerations
        """
        # Create a new lineup with the specified leadoff index
        adjusted_lineup = lineup[leadoff_index:] + lineup[:leadoff_index]
        
        # Calculate the basic score for the reordered lineup (without special leadoff considerations)
        total_score = 0.0
        
        # For each position in the lineup, apply at-bat probability weights
        for i in range(9):
            # Get the three preceding batters (wrap around if necessary)
            p1 = adjusted_lineup[(i-3) % 9]
            p2 = adjusted_lineup[(i-2) % 9]
            p3 = adjusted_lineup[(i-1) % 9]
            p4 = adjusted_lineup[i]
            
            # Calculate the basic BDNRP contribution
            position_score = self._get_bdnrp(p1, p2, p3, p4)
            
            # Apply the improved at-bat probability weights
            # First batter gets 1 + 7/8 = 1.875, last batter gets 1.0
            extra_ab_probability = (7 - i) / 8 if i < 8 else 0
            position_weight = 1.0 + extra_ab_probability
            
            # Apply the position weight to the BDNRP value
            total_score += position_score * position_weight
        
        # Apply the leadoff and second at-bat adjustments
        if self.leadoff_brp and self.second_ab_brp:
            leadoff_player = adjusted_lineup[0]
            second_player = adjusted_lineup[1]
            
            # Apply the leadoff penalty - there are no baserunners for the first batter
            # This replaces the score for the first batter's first at-bat
            if leadoff_player in self.leadoff_brp:
                # Remove the regular BDNRP for this position (estimated as 1/5 of position's total BDNRP)
                p1 = adjusted_lineup[-3]
                p2 = adjusted_lineup[-2]
                p3 = adjusted_lineup[-1]
                regular_first_ab = self._get_bdnrp(p1, p2, p3, leadoff_player) / 5
                
                # Add the special leadoff BRP
                total_score = total_score - regular_first_ab + self.leadoff_brp[leadoff_player]
            
            # Apply the second batter adjustment - there's at most one baserunner
            if second_player in self.second_ab_brp:
                # Remove the regular BDNRP for this position (estimated as 1/5 of position's total BDNRP)
                p1 = adjusted_lineup[-2]
                p2 = adjusted_lineup[-1]
                p3 = adjusted_lineup[0]
                regular_second_ab = self._get_bdnrp(p1, p2, p3, second_player) / 5
                
                # Add the special second at-bat BRP
                total_score = total_score - regular_second_ab + self.second_ab_brp[second_player]
        
        return total_score

    # Define process_batch as a static method to avoid pickling issues
    @staticmethod
    def _process_batch_static(batch, lookup_data, constraints, player_handedness, handedness_constraint, top_n=15):
        """
        Process a batch of lineups and return the top N performers.
        
        Args:
            batch: List of lineup permutations to evaluate
            lookup_data: BDNRP lookup data
            constraints: Lineup position constraints
            player_handedness: Handedness of each player
            handedness_constraint: Constraints on consecutive same-handed batters
            top_n: Number of top lineups to return
            
        Returns:
            list of (score, lineup) tuples for the top N lineups
        """
        # Create a temporary optimizer instance for this batch
        temp_optimizer = LineupOptimizer(
            lookup_data,
            list(set([player for lineup in batch for player in lineup])),
            constraints,
            player_handedness,
            handedness_constraint
        )
        
        # Use a min heap to track the top N lineups
        top_lineups = []
        
        for lineup in batch:
            score = temp_optimizer.evaluate_lineup(lineup)
            
            # Only consider valid lineups (score > -inf)
            if score > float('-inf'):
                if len(top_lineups) < top_n:
                    # Heap uses min as the comparison, so we use negative score
                    heapq.heappush(top_lineups, (score, lineup))
                else:
                    # Replace the lowest score if this one is better
                    if score > top_lineups[0][0]:
                        heapq.heappushpop(top_lineups, (score, lineup))
        
        # Sort by score in descending order before returning
        return sorted(top_lineups, reverse=True)
    
    def _process_batch(self, batch):
        """Process a batch and return the best lineup and its score."""
        top_lineups = LineupOptimizer._process_batch_static(
            batch,
            self.bdnrp_data,
            self.constraints,
            self.player_handedness,
            self.handedness_constraint,
            self.top_n
        )
        
        # Update our running list of top lineups
        self.top_lineups.extend(top_lineups)
        self.top_lineups.sort(reverse=True)
        self.top_lineups = self.top_lineups[:self.top_n]
        
        # Return the best lineup and score from this batch
        if top_lineups:
            return top_lineups[0][1], top_lineups[0][0]
        return None, float('-inf')
    
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
        self.top_lineups = []  # Reset top lineups
        
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
        
        # Add debug info for constraints
        print(f"Has fixed position constraints: {has_constraints}")
        fixed_count = sum(1 for pos in self.constraints.values() if 1 <= pos <= 9)
        print(f"Number of fixed positions: {fixed_count}")
        
        # Process lineups in batches
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
    
    def find_optimal_leadoff(self):
        """
        Evaluate the top N lineup cycles to find the optimal leadoff position.
        Returns the best lineup with the optimal leadoff position.
        """
        if not self.top_lineups:
            raise ValueError("No lineup cycles available. Run optimize() first.")
        
        print(f"\nAnalyzing the top {len(self.top_lineups)} lineup cycles to find optimal leadoff position...")
        
        best_leadoff_lineup = None
        best_leadoff_score = float('-inf')
        best_cycle_rank = 0
        best_cycle_index = 0
        
        # Process each of the top lineup cycles
        for rank, (cycle_score, lineup) in enumerate(self.top_lineups, 1):
            print(f"\nEvaluating cycle #{rank}: {lineup}")
            print(f"Original cycle score: {cycle_score:.4f}")
            
            best_index = 0
            best_score = float('-inf')
            
            # Try each position as the leadoff
            leadoff_scores = []
            for i in range(9):
                leadoff_score = self.evaluate_lineup_with_leadoff(lineup, i)
                leadoff_scores.append(leadoff_score)
                
                if leadoff_score > best_score:
                    best_score = leadoff_score
                    best_index = i
            
            # Print the scores for each leadoff position
            for i, score in enumerate(leadoff_scores):
                player = lineup[i]
                print(f"  Leadoff {i+1}: {player} - Score: {score:.4f}{' (BEST)' if i == best_index else ''}")
            
            # Update the best overall leadoff if this is better
            if best_score > best_leadoff_score:
                best_leadoff_score = best_score
                # Reorder the lineup to put the best leadoff first
                best_leadoff_lineup = lineup[best_index:] + lineup[:best_index]
                best_cycle_rank = rank
                best_cycle_index = best_index
        
        print(f"\nBest leadoff lineup found from cycle #{best_cycle_rank} (originally ranked #{best_cycle_rank}/{len(self.top_lineups)})")
        print(f"Leadoff position selected: {best_cycle_index+1} ({best_leadoff_lineup[0]})")
        print(f"Final score with leadoff considerations: {best_leadoff_score:.4f}")
        
        return best_leadoff_lineup, best_leadoff_score, best_cycle_rank
    
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


def get_leadoff_brp_from_excel(sheet, player, player_stats, excel_range="E132"):
    """Get the leadoff BRP value for a player (first batter, no baserunners)."""
    # Set player stats
    stats = player_stats[player]
    sheet.Range("D27").Value = player
    sheet.Range("H27").Value = stats["pa"]
    sheet.Range("K27").Value = stats["h"]
    sheet.Range("L27").Value = stats["2b"]
    sheet.Range("M27").Value = stats["3b"]
    sheet.Range("N27").Value = stats["hr"]
    sheet.Range("P27").Value = stats["sb"]
    sheet.Range("R27").Value = stats["bb"]
    sheet.Range("AA27").Value = stats["hbp"]
    sheet.Range("AD27").Value = stats["ibb"]
    
    # Allow time for Excel to recalculate
    time.sleep(0.05)
    
    # Get the calculated leadoff BRP value
    brp = sheet.Range(excel_range).Value
    return brp


def get_second_ab_brp_from_excel(sheet, player, player_stats, excel_range="E136"):
    """Get the second at-bat BRP value for a player (second batter, at most one baserunner)."""
    # Set player stats
    stats = player_stats[player]
    sheet.Range("D27").Value = player
    sheet.Range("H27").Value = stats["pa"]
    sheet.Range("K27").Value = stats["h"]
    sheet.Range("L27").Value = stats["2b"]
    sheet.Range("M27").Value = stats["3b"]
    sheet.Range("N27").Value = stats["hr"]
    sheet.Range("P27").Value = stats["sb"]
    sheet.Range("R27").Value = stats["bb"]
    sheet.Range("AA27").Value = stats["hbp"]
    sheet.Range("AD27").Value = stats["ibb"]
    
    # Allow time for Excel to recalculate
    time.sleep(0.05)
    
    # Get the calculated second at-bat BRP value
    brp = sheet.Range(excel_range).Value
    return brp


def generate_bdnrp_data(players, player_stats, excel_file_path, output_csv=None, include_leadoff=True):
    """Generate BDNRP data for all player combinations using Excel."""
    # Check if we already have cached BDNRP data
    if output_csv and os.path.exists(output_csv) and os.path.exists("leadoff_brp.csv") and os.path.exists("second_ab_brp.csv"):
        print(f"Loading pre-calculated BDNRP data from {output_csv}")
        bdnrp_data = pd.read_csv(output_csv)
        leadoff_df = pd.read_csv("leadoff_brp.csv")
        second_ab_df = pd.read_csv("second_ab_brp.csv")
        leadoff_brp = {row['player']: row['leadoff_brp'] for _, row in leadoff_df.iterrows()}
        second_ab_brp = {row['player']: row['second_ab_brp'] for _, row in second_ab_df.iterrows()}
        return bdnrp_data, leadoff_brp, second_ab_brp

    excel, workbook, sheet = setup_excel(excel_file_path)
    try:
        bdnrp_tuples = []
        leadoff_brp = {}
        second_ab_brp = {}
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
        
        # If requested, get leadoff and second at-bat BRP values
        if include_leadoff:
            print("\nGenerating leadoff and second at-bat BRP values for each player...")
            for player in players:
                # Get leadoff BRP (first batter, no baserunners)
                leadoff_brp[player] = get_leadoff_brp_from_excel(sheet, player, player_stats)
                
                # Get second at-bat BRP (second batter, at most one baserunner)
                second_ab_brp[player] = get_second_ab_brp_from_excel(sheet, player, player_stats)
                
                print(f"Player: {player} - Leadoff BRP: {leadoff_brp[player]:.4f}, Second-AB BRP: {second_ab_brp[player]:.4f}")
        
        # Create the DataFrame
        bdnrp_data = pd.DataFrame(bdnrp_tuples)
        
        # Save to CSV if requested
        if output_csv:
            bdnrp_data.to_csv(output_csv, index=False)
            
            # Save leadoff and second at-bat BRP values to CSV files
            if include_leadoff:
                leadoff_df = pd.DataFrame([{'player': p, 'leadoff_brp': v} for p, v in leadoff_brp.items()])
                leadoff_df.to_csv('leadoff_brp.csv', index=False)
                
                second_ab_df = pd.DataFrame([{'player': p, 'second_ab_brp': v} for p, v in second_ab_brp.items()])
                second_ab_df.to_csv('second_ab_brp.csv', index=False)
            
            print(f"BDNRP data saved to {output_csv}")
            
        return bdnrp_data, leadoff_brp, second_ab_brp
        
    finally:
        # Clean up Excel resources
        workbook.Close(SaveChanges=False)
        excel.Quit()


def parse_and_optimize_lineup(json_input, excel_file_path, method='exhaustive', max_iterations=1000, top_n=15):
    """
    Parse JSON input containing player data and constraints, optimize the lineup,
    and return the result as a JSON object.
    """
    import os
    import pandas as pd

    # Extract handedness constraints directly from the JSON input
    handedness_constraint = {}
    if "max_consecutive_right" in json_input:
        handedness_constraint["max_consecutive_right"] = json_input["max_consecutive_right"]
    if "max_consecutive_left" in json_input:
        handedness_constraint["max_consecutive_left"] = json_input["max_consecutive_left"]
    
    if handedness_constraint:
        print("Handedness constraints applied:")
        if "max_consecutive_right" in handedness_constraint:
            print(f" - Maximum consecutive right-handed batters: {handedness_constraint['max_consecutive_right']}")
        if "max_consecutive_left" in handedness_constraint:
            print(f" - Maximum consecutive left-handed batters: {handedness_constraint['max_consecutive_left']}")

    # Step 1: Extract player info
    players = []
    player_stats = {}
    constraints = {}
    player_handedness = {}

    for pos in range(1, 10):
        pos_key = str(pos)
        if (pos_key in json_input and json_input[pos_key] is not None and
            json_input[pos_key]["name"] != "" and json_input[pos_key]["data"] is not None):
            pdata = json_input[pos_key]
            name = pdata["name"]
            players.append(name)
            player_stats[name] = pdata["data"]
            constraints[name] = pos
            player_handedness[name] = pdata.get("batting_hand", "R")

    for pos in range(10, 19):
        pos_key = str(pos)
        if (pos_key in json_input and json_input[pos_key] is not None and
            json_input[pos_key]["name"] != "" and json_input[pos_key]["data"] is not None):
            pdata = json_input[pos_key]
            name = pdata["name"]
            players.append(name)
            player_stats[name] = pdata["data"]
            constraints[name] = pos
            player_handedness[name] = pdata.get("batting_hand", "R")

    print("\nPlayer batting hands:")
    for player, hand in player_handedness.items():
        print(f" - {player}: {hand}")

    if len(players) != 9:
        raise ValueError(f"Expected 9 players, but found {len(players)}.")

    # Step 2: Load or generate BDNRP and BRP data
    print("\nStep 1: Generating BDNRP data...")
    bdnrp_csv = "bdnrp_values.csv"
    leadoff_csv = "leadoff_brp.csv"
    second_ab_csv = "second_ab_brp.csv"

    need_generation = not (os.path.exists(bdnrp_csv) and os.path.exists(leadoff_csv) and os.path.exists(second_ab_csv))

    if need_generation:
        bdnrp_data, leadoff_brp, second_ab_brp = generate_bdnrp_data(
            players, player_stats, excel_file_path, output_csv=bdnrp_csv, include_leadoff=True
        )
    else:
        print("Loading pre-calculated BDNRP data and leadoff values from CSV files.")
        bdnrp_data = pd.read_csv(bdnrp_csv)
        leadoff_df = pd.read_csv(leadoff_csv)
        second_ab_df = pd.read_csv(second_ab_csv)
        leadoff_brp = {row['player']: row['leadoff_brp'] for _, row in leadoff_df.iterrows()}
        second_ab_brp = {row['player']: row['second_ab_brp'] for _, row in second_ab_df.iterrows()}

    # Step 3: Initialize and run the lineup optimizer
    print("\nStep 2: Initializing lineup optimizer...")
    optimizer = LineupOptimizer(bdnrp_data, players, constraints, player_handedness, handedness_constraint)
    optimizer.top_n = top_n
    optimizer.set_leadoff_brp_data(leadoff_brp)
    optimizer.set_second_ab_brp_data(second_ab_brp)

    print("\nStep 3: Running lineup optimization...")
    best_lineup, best_score = optimizer.optimize(method=method, batch_size=10)

    print("\nStep 4: Finding optimal leadoff position...")
    leadoff_lineup, leadoff_score, original_rank = optimizer.find_optimal_leadoff()

    # Step 5: Calculate base BRP (unweighted, no leadoff adjustment)
    lineup_stats = optimizer.get_lineup_stats(leadoff_lineup)
    base_score = lineup_stats['base_bdnrp'].sum()

    # Step 6: Package result
    result = {}
    for i, player in enumerate(leadoff_lineup):
        result[str(i + 1)] = player

    result["expected runs"] = round(base_score * 9, 4)
    result["optimal_leadoff_info"] = {
        "leadoff_player": leadoff_lineup[0],
        "leadoff_adjusted_score": round(leadoff_score, 4),
        "original_cycle_rank": original_rank,
        "total_cycles_evaluated": len(optimizer.top_lineups)
    }

    print("\n===== OPTIMIZATION RESULTS =====")
    print(f"Best lineup with optimal leadoff: {leadoff_lineup}")
    print(f"Leadoff-adjusted score: {leadoff_score:.4f}")
    print(f"Expected run production per inning: {base_score:.4f}")
    print(f"Expected run production per game: {base_score * 9:.4f}")
    print(f"Original cycle rank before leadoff selection: {original_rank} of {len(optimizer.top_lineups)}")

    return result



# This is the proper way to use multiprocessing in Python
if __name__ == "__main__":
    # Your test_input dictionary and main execution code here
    test_input = {
    "json_input": {
        "1": {"name": "", "data": None, "batting_hand": "R"},
        "2": {"name": "", "data": None, "batting_hand": "R"},
        "3": {"name": "", "data": None, "batting_hand": "R"},
        "4": {"name": "", "data": None, "batting_hand": "R"},
        "5": {"name": "", "data": None, "batting_hand": "R"},
        "6": {"name": "", "data": None, "batting_hand": "R"},
        "7": {"name": "", "data": None, "batting_hand": "R"},
        "8": {"name": "", "data": None, "batting_hand": "R"},
        "9": {"name": "", "data": None, "batting_hand": "R"},

        "10": {
            "name": "Bryce Harper",
            "data": {"pa": 550, "h": 157, "2b": 42, "3b": 0, "hr": 30, "sb": 0, "bb": 65, "hbp": 2, "ibb": 11},
            "batting_hand": "LEFT"
        },
        "11": {
            "name": "Alec Bohm",
            "data": {"pa": 554, "h": 155, "2b": 44, "3b": 2, "hr": 15, "sb": 0, "bb": 38, "hbp": 6, "ibb": 2},
            "batting_hand": "RIGHT"
        },
        "12": {
            "name": "Jacob Realmuto",
            "data": {"pa": 380, "h": 101, "2b": 18, "3b": 1, "hr": 14, "sb": 0, "bb": 26, "hbp": 5, "ibb": 1},
            "batting_hand": "RIGHT"
        },
        "13": {
            "name": "Brandon Marsh",
            "data": {"pa": 418, "h": 104, "2b": 17, "3b": 3, "hr": 16, "sb": 0, "bb": 50, "hbp": 2, "ibb": 0},
            "batting_hand": "LEFT"
        },
        "14": {
            "name": "Kyle Schwarber",
            "data": {"pa": 573, "h": 142, "2b": 22, "3b": 0, "hr": 38, "sb": 0, "bb": 102, "hbp": 5, "ibb": 4},
            "batting_hand": "LEFT"
        },
        "15": {
            "name": "Bryson Stott",
            "data": {"pa": 506, "h": 124, "2b": 19, "3b": 2, "hr": 11, "sb": 0, "bb": 52, "hbp": 3, "ibb": 1},
            "batting_hand": "LEFT"
        },
        "16": {
            "name": "Johan Rojas",
            "data": {"pa": 338, "h": 82, "2b": 12, "3b": 3, "hr": 3, "sb": 0, "bb": 13, "hbp": 4, "ibb": 0},
            "batting_hand": "RIGHT"
        },
        "17": {
            "name": "Edmundo Sosa",
            "data": {"pa": 249, "h": 64, "2b": 12, "3b": 4, "hr": 7, "sb": 0, "bb": 13, "hbp": 8, "ibb": 0},
            "batting_hand": "RIGHT"
        },
        "18": {
            "name": "Kody Clemens",
            "data": {"pa": 114, "h": 25, "2b": 9, "3b": 1, "hr": 5, "sb": 0, "bb": 5, "hbp": 1, "ibb": 0},
            "batting_hand": "LEFT"
        }
    },
    "excel_file_path": r"C:\Users\buman\OneDrive\Desktop\Lineup_Optimization\Copy_Of_Lineup_Optimization.xlsx",
    "method": "exhaustive",
    "max_iterations": 1000,
    "top_n": 15
}

    
    result = parse_and_optimize_lineup(
        json_input=test_input["json_input"],
        excel_file_path=test_input["excel_file_path"],
        method=test_input["method"],
        max_iterations=test_input["max_iterations"],
        top_n=test_input["top_n"]
    )
    
    print("\nFinal optimized lineup:")
    for pos in map(str, range(1, 10)):
        print(f"{pos}. {result[pos]}")
    
    print(f"\nExpected runs per game: {result['expected runs']}")
    print(f"Leadoff player: {result['optimal_leadoff_info']['leadoff_player']}")
    print(f"Original cycle rank: {result['optimal_leadoff_info']['original_cycle_rank']} of {result['optimal_leadoff_info']['total_cycles_evaluated']}")