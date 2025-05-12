import numpy as np
import pandas as pd
from itertools import permutations
from concurrent.futures import ProcessPoolExecutor
import time
import win32com.client as win32
import os
import random
import json

class LineupOptimizer:
    def __init__(self, bdnrp_data, players, constraints=None):
        """
        Initialize the lineup optimizer with BDNRP data and player list.
        
        Args:
            bdnrp_data (DataFrame): DataFrame containing the BDNRP values for 4-tuples
                                    Should have columns for player1, player2, player3, player4, and bdnrp_value
            players (list): List of player IDs/names to be included in the lineup
            constraints (dict, optional): Dictionary mapping player names to position constraints
                                         Position 1-9 locks player to that position, 10+ means no constraint
        """
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
            if position >= 1 and position <= 9:  # This is a fixed position constraint
                if position in used_positions:
                    raise ValueError(f"Position {position} is assigned to multiple players: {used_positions[position]} and {player}")
                used_positions[position] = player
    
    def _create_bdnarp_lookup(self):
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
    
    def evaluate_lineup(self, lineup):
        """
        Calculate the expected run production for a given lineup, accounting for
        the probability of extra at-bats for players at the top of the order.
        
        Args:
            lineup (list): A specific ordering of self.players
            
        Returns:
            float: The total expected run production, or -inf if lineup violates constraints
        """
        # Check if lineup satisfies all position constraints
        for i, player in enumerate(lineup):
            position = i + 1  # Convert to 1-based position
            constraint = self.constraints.get(player, 10)
            if constraint >= 1 and constraint <= 9 and constraint != position:
                # This player has a constraint that isn't satisfied
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
            # The first batter has 8/9 chance, second has 7/9, etc.
            extra_ab_probability = (8 - i) / 9 if i < 8 else 0
            
            # The base contribution counts as 1.0, plus the extra at-bat probability
            # This effectively gives the first batter 1 + 8/9 = 17/9 weight, etc.
            position_weight = 1.0 + extra_ab_probability
            
            # Apply the position weight to the BDNRP value
            total_score += position_score * position_weight
        
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
    
    def optimize(self, method='exhaustive', max_iterations=None, batch_size=10000):
        """
        Find the optimal lineup based on BDNRP values.
        
        Args:
            method (str): Optimization method - 'exhaustive', 'genetic', or 'simulated_annealing'
            max_iterations (int): Maximum number of iterations for non-exhaustive methods
            batch_size (int): Number of lineups to evaluate in each parallel batch
            
        Returns:
            list: The optimal lineup ordering
            float: The expected run production of the optimal lineup
        """
        start_time = time.time()
        self.evaluated_lineups = 0
        
        # Pre-generate valid lineups that satisfy fixed constraints if there are any
        if any(pos >= 1 and pos <= 9 for pos in self.constraints.values()):
            print("Constraints detected - generating only valid lineup permutations...")
            
        if method == 'exhaustive':
            return self._optimize_exhaustive(batch_size)
        elif method == 'genetic':
            return self._optimize_genetic(max_iterations)
        elif method == 'simulated_annealing':
            return self._optimize_simulated_annealing(max_iterations)
        else:
            raise ValueError(f"Unknown optimization method: {method}")
    
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
    
    def _optimize_exhaustive(self, batch_size=10000):
        """
        Exhaustively evaluate all possible lineups that satisfy constraints.
        Uses parallel processing to speed up computation.
        """
        # Record start time for this method
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
        
        # Process lineups in batches for better parallelization
        with ProcessPoolExecutor() as executor:
            batch_results = []
            for i in range(0, total_lineups, batch_size):
                batch = all_lineups[i:i+batch_size]
                batch_results.append(executor.submit(self._process_batch, batch))
                
                # Update progress
                self.evaluated_lineups += len(batch)
                if (i + batch_size) % (batch_size * 10) == 0 or i + batch_size >= total_lineups:
                    progress = min(100, (i + batch_size) / total_lineups * 100)
                    elapsed = time.time() - start_time
                    print(f"Progress: {progress:.1f}% ({self.evaluated_lineups:,}/{total_lineups:,}) - Elapsed: {elapsed:.1f}s")
            
            # Find the best lineup across all batches
            for future in batch_results:
                lineup, score = future.result()
                if score > self.best_score:
                    self.best_score = score
                    self.best_lineup = lineup
        
        print(f"Optimization complete. Evaluated {self.evaluated_lineups:,} lineups in {time.time() - start_time:.1f}s")
        return self.best_lineup, self.best_score
    
    def _create_valid_random_lineup(self):
        """Create a random lineup that satisfies position constraints."""
        # Initialize lineup with fixed players
        lineup = [None] * 9
        flexible_players = []
        
        # Place fixed players
        for player, constraint in self.constraints.items():
            if constraint >= 1 and constraint <= 9:
                lineup[constraint - 1] = player
            else:
                flexible_players.append(player)
        
        # Shuffle the flexible players
        random.shuffle(flexible_players)
        
        # Fill in flexible players
        flex_idx = 0
        for i in range(9):
            if lineup[i] is None:
                lineup[i] = flexible_players[flex_idx]
                flex_idx += 1
        
        return lineup
    
    def _optimize_genetic(self, max_iterations=1000, population_size=100, elite_size=20, mutation_rate=0.01):
        """
        Genetic algorithm implementation for lineup optimization.
        This is a stochastic approach that can find near-optimal solutions faster.
        
        Args:
            max_iterations: Maximum number of generations
            population_size: Number of lineups in each generation
            elite_size: Number of top lineups to keep for the next generation
            mutation_rate: Probability of mutation for each position in a lineup
            
        Returns:
            tuple: (best_lineup, best_score)
        """
        print(f"Starting genetic algorithm optimization with {population_size} population size...")
        start_time = time.time()
        
        # Initialize population with random lineups that satisfy constraints
        population = []
        for _ in range(population_size):
            population.append(self._create_valid_random_lineup())
        
        # Track the best lineup found so far
        best_overall_lineup = None
        best_overall_score = float('-inf')
        
        # Main evolution loop
        for generation in range(max_iterations):
            # Evaluate fitness of each lineup in the population
            fitness_scores = [(lineup, self.evaluate_lineup(lineup)) for lineup in population]
            self.evaluated_lineups += len(population)
            
            # Sort by fitness (descending)
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Update best overall
            current_best_lineup, current_best_score = fitness_scores[0]
            if current_best_score > best_overall_score:
                best_overall_lineup = current_best_lineup
                best_overall_score = current_best_score
            
            # Print progress periodically
            if generation % 10 == 0 or generation == max_iterations - 1:
                elapsed = time.time() - start_time
                print(f"Generation {generation}/{max_iterations} - Best score: {current_best_score:.4f} - Evaluated: {self.evaluated_lineups:,} - Elapsed: {elapsed:.1f}s")
            
            # Create the next generation
            next_generation = []
            
            # Keep elite lineups
            for i in range(elite_size):
                next_generation.append(fitness_scores[i][0])
            
            # Create children through selection and crossover
            while len(next_generation) < population_size:
                # Tournament selection
                parent1 = self._tournament_selection(fitness_scores, tournament_size=3)
                parent2 = self._tournament_selection(fitness_scores, tournament_size=3)
                
                # Order crossover with constraint preservation
                child = self._constraint_preserving_crossover(parent1, parent2)
                
                # Constraint-respecting mutation
                child = self._constraint_respecting_mutation(child, mutation_rate)
                
                next_generation.append(child)
            
            # Replace the old population
            population = next_generation
        
        print(f"Genetic algorithm complete. Evaluated {self.evaluated_lineups:,} lineups in {time.time() - start_time:.1f}s")
        
        self.best_lineup = best_overall_lineup
        self.best_score = best_overall_score
        return best_overall_lineup, best_overall_score
    
    def _tournament_selection(self, fitness_scores, tournament_size):
        """Select a lineup using tournament selection."""
        tournament = random.sample(fitness_scores, tournament_size)
        tournament.sort(key=lambda x: x[1], reverse=True)
        return tournament[0][0]
    
    def _constraint_preserving_crossover(self, parent1, parent2):
        """Perform crossover while preserving position constraints."""
        # Find flexible positions (those without fixed constraints)
        flexible_positions = []
        for i, player in enumerate(parent1):
            pos = i + 1
            if self.constraints.get(player, 10) > 9:  # No fixed constraint
                flexible_positions.append(i)
        
        if not flexible_positions:
            # All positions are fixed, just return parent1
            return list(parent1)
        
        # Choose crossover points among flexible positions
        if len(flexible_positions) >= 2:
            crossover_indices = sorted(random.sample(flexible_positions, 2))
            start, end = crossover_indices[0], crossover_indices[1]
        else:
            # Only one flexible position, no meaningful crossover
            return list(parent1)
        
        # Create child with parent1 segment
        child = list(parent1)
        
        # Get the players from parent2 that should be in the child but aren't yet
        remaining_players = []
        for i, player in enumerate(parent2):
            if player not in child[start:end+1] and self.constraints.get(player, 10) > 9:
                remaining_players.append(player)
        
        # Fill flexible positions outside the crossover segment
        remaining_idx = 0
        for i in flexible_positions:
            if i < start or i > end:  # Outside crossover segment
                if remaining_idx < len(remaining_players):
                    child[i] = remaining_players[remaining_idx]
                    remaining_idx += 1
        
        return child
    
    def _constraint_respecting_mutation(self, lineup, mutation_rate):
        """Mutate a lineup by swapping positions, respecting constraints."""
        # Find flexible positions (those without fixed constraints)
        flexible_positions = []
        for i, player in enumerate(lineup):
            if self.constraints.get(player, 10) > 9:  # No fixed constraint
                flexible_positions.append(i)
        
        if len(flexible_positions) < 2:
            # Need at least 2 flexible positions for swapping
            return lineup
        
        # Apply mutation with some probability
        if random.random() < mutation_rate:
            # Pick two different flexible positions to swap
            i, j = random.sample(flexible_positions, 2)
            lineup[i], lineup[j] = lineup[j], lineup[i]
        
        return lineup
    
    def _optimize_simulated_annealing(self, max_iterations=50000, initial_temp=100, cooling_rate=0.995):
        """
        Simulated annealing implementation for lineup optimization.
        
        Args:
            max_iterations: Maximum number of iterations
            initial_temp: Initial temperature
            cooling_rate: Rate at which temperature decreases
            
        Returns:
            tuple: (best_lineup, best_score)
        """
        print(f"Starting simulated annealing optimization with {max_iterations} max iterations...")
        start_time = time.time()
        
        # Start with a random solution that satisfies constraints
        current_lineup = self._create_valid_random_lineup()
        
        current_score = self.evaluate_lineup(current_lineup)
        best_lineup = list(current_lineup)
        best_score = current_score
        self.evaluated_lineups += 1
        
        # Initialize temperature
        temp = initial_temp
        
        # Main simulated annealing loop
        for iteration in range(max_iterations):
            # Create a neighbor by swapping two flexible positions
            neighbor = self._get_constrained_neighbor(current_lineup)
            
            # Evaluate the neighbor
            neighbor_score = self.evaluate_lineup(neighbor)
            self.evaluated_lineups += 1
            
            # Decide whether to accept the neighbor
            score_diff = neighbor_score - current_score
            
            if score_diff > 0:
                # Accept better solutions
                current_lineup = neighbor
                current_score = neighbor_score
                
                # Update best solution if needed
                if current_score > best_score:
                    best_lineup = list(current_lineup)
                    best_score = current_score
            else:
                # Accept worse solutions with a probability based on temperature
                acceptance_probability = np.exp(score_diff / temp)
                if random.random() < acceptance_probability:
                    current_lineup = neighbor
                    current_score = neighbor_score
            
            # Cool the temperature
            temp *= cooling_rate
            
            # Print progress periodically
            if iteration % 1000 == 0 or iteration == max_iterations - 1:
                elapsed = time.time() - start_time
                progress = (iteration + 1) / max_iterations * 100
                print(f"Progress: {progress:.1f}% - Temp: {temp:.4f} - Best score: {best_score:.4f} - Current score: {current_score:.4f} - Evaluated: {self.evaluated_lineups:,} - Elapsed: {elapsed:.1f}s")
                
            # Stop if temperature is very low
            if temp < 0.01:
                print(f"Stopping early at iteration {iteration} due to low temperature.")
                break
        
        print(f"Simulated annealing complete. Evaluated {self.evaluated_lineups:,} lineups in {time.time() - start_time:.1f}s")
        
        self.best_lineup = best_lineup
        self.best_score = best_score
        return best_lineup, best_score
    
    def _get_constrained_neighbor(self, lineup):
        """Generate a neighboring lineup by swapping two flexible positions."""
        # Find flexible positions (those without fixed constraints)
        flexible_positions = []
        for i, player in enumerate(lineup):
            if self.constraints.get(player, 10) > 9:  # No fixed constraint
                flexible_positions.append(i)
        
        if len(flexible_positions) < 2:
            # Can't create a neighbor through swapping
            return list(lineup)
        
        # Create a neighbor by swapping two random flexible positions
        neighbor = list(lineup)
        i, j = random.sample(flexible_positions, 2)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        
        return neighbor
    
    def get_lineup_stats(self, lineup=None):
        """
        Get detailed statistics for a lineup, including the weighted BDNRP that
        accounts for extra at-bat probabilities.
        
        Args:
            lineup (list): Lineup to analyze. If None, uses the best lineup found.
            
        Returns:
            DataFrame: Detailed breakdown of BDNRP contributions by position
        """
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
            
            # Calculate extra at-bat probability and weight
            extra_ab_probability = (8 - i) / 9 if i < 8 else 0
            position_weight = 1.0 + extra_ab_probability
            weighted_bdnrp = base_bdnrp * position_weight
            
            # Add constraint information
            has_constraint = self.constraints.get(p4, 10) <= 9
            
            stats.append({
                'position': i+1,
                'player': p4,
                'prev_three': [p1, p2, p3],
                'base_bdnrp': base_bdnrp,
                'extra_ab_prob': extra_ab_probability,
                'position_weight': position_weight,
                'weighted_bdnrp': weighted_bdnrp,
                'constrained': has_constraint
            })
        
        df = pd.DataFrame(stats)
        df['contrib_pct'] = (df['weighted_bdnrp'] / df['weighted_bdnrp'].sum()) * 100
        
        return df

# NEW FUNCTIONS FOR JSON HANDLING

def parse_json_constraints(json_input):
    """
    Parse the JSON input format and convert it to the constraint format needed by LineupOptimizer.
    
    Args:
        json_input (dict): JSON object with positions 1-18 as keys and player IDs as values
        
    Returns:
        tuple: (players_list, constraints_dict)
    """
    # Extract players from positions 1-9 (fixed) and 10-18 (flexible)
    fixed_players = {}
    flexible_players = []
    
    # Process positions 1-9 (fixed positions)
    for pos in range(1, 10):
        pos_key = str(pos)
        if pos_key in json_input and json_input[pos_key] is not None:
            player_id = json_input[pos_key]
            fixed_players[player_id] = pos
    
    # Process positions 10-18 (flexible positions)
    for pos in range(10, 19):
        pos_key = str(pos)
        if pos_key in json_input and json_input[pos_key] is not None:
            player_id = json_input[pos_key]
            flexible_players.append(player_id)
    
    # Combine all players into a single list
    all_players = list(fixed_players.keys()) + flexible_players
    
    # Create constraints dictionary
    constraints = {}
    for player in all_players:
        if player in fixed_players:
            constraints[player] = fixed_players[player]
        else:
            constraints[player] = 10  # Default to flexible
    
    return all_players, constraints

def format_json_output(best_lineup, best_score):
    """
    Format the optimization result as a JSON object.
    
    Args:
        best_lineup (list): The optimal lineup ordering
        best_score (float): The expected run production score
        
    Returns:
        dict: JSON-formatted result
    """
    result = {}
    
    # Add each player to their position
    for i, player in enumerate(best_lineup):
        position = i + 1
        result[str(position)] = player
    
    # Add the expected runs score
    result["expected runs"] = round(best_score, 4)
    
    return result

def optimize_lineup_from_json(excel_file_path, json_input, bdnrp_csv=None, method='genetic', max_iterations=1000):
    """
    End-to-end function to optimize lineup based on JSON input format.
    
    Args:
        excel_file_path (str): Path to the Excel file containing BDNRP calculations
        json_input (dict): JSON object with positions 1-18 as keys and player IDs as values
        bdnrp_csv (str, optional): Path to save/load BDNRP data
        method (str): Optimization method - 'exhaustive', 'genetic', or 'simulated_annealing'
        max_iterations (int): Maximum number of iterations for non-exhaustive methods
        
    Returns:
        dict: JSON-formatted optimization result
    """
    # Parse the JSON input
    players, constraints = parse_json_constraints(json_input)
    
    if len(players) != 9:
        raise ValueError(f"Expected 9 players, but found {len(players)}. Please ensure you provide exactly 9 unique players.")
    
    # Generate or load BDNRP data
    print("Step 1: Preparing BDNRP data...")
    bdnrp_data = generate_bdnrp_data(players, excel_file_path, output_csv=bdnrp_csv)
    
    # Initialize the optimizer
    print("\nStep 2: Initializing lineup optimizer...")
    if constraints:
        print("Position constraints applied:")
        for player, position in constraints.items():
            if position >= 1 and position <= 9:
                print(f"  - {player}: fixed to position {position}")
    
    optimizer = LineupOptimizer(bdnrp_data, players, constraints)
    
    # Run the optimization
    print("\nStep 3: Running lineup optimization...")
    best_lineup, best_score = optimizer.optimize(method=method, max_iterations=max_iterations)
    
    # Format the result as JSON
    result_json = format_json_output(best_lineup, best_score)
    
    # Display results
    print("\n===== OPTIMIZATION RESULTS =====")
    print(f"Best lineup JSON: {json.dumps(result_json, indent=2)}")
    
    # Get detailed stats for the best lineup
    lineup_stats = optimizer.get_lineup_stats()
    
    # Save results to CSV
    results_csv = "lineup_optimization_results.csv"
    lineup_stats.to_csv(results_csv, index=False)
    print(f"\nDetailed results saved to {results_csv}")
    
    return result_json

def generate_bdnrp_data(players, excel_file_path, output_csv=None):
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
                            # Get BDNRP for this combination
                            bdnrp = get_bdnrp_from_excel(sheet, p1, p2, p3, p4)
                            
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

def setup_excel(file_path):
    """Connect to Excel and open the workbook."""
    excel = win32.Dispatch('Excel.Application')
    excel.Visible = False  # Run Excel in the background
    workbook = excel.Workbooks.Open(file_path)
    sheet = workbook.Sheets("4 Tuple Values 0 Outs")
    return excel, workbook, sheet

def get_bdnrp_from_excel(sheet, p1, p2, p3, p4):
    """Get BDNRP for a specific 4-tuple from Excel."""
    # Set player names in the appropriate cells
    sheet.Range("D4").Value = p1
    sheet.Range("D11").Value = p2
    sheet.Range("D18").Value = p3
    sheet.Range("D27").Value = p4
    
    # Allow time for Excel to recalculate
    time.sleep(0.1)
    
    # Get the calculated BDNRP value
    bdnrp = sheet.Range("H103").Value
    return bdnrp

if __name__ == "__main__":
    # Configuration
    excel_file_path = r"C:\path\to\Lineup Optimization 1.xlsx"  # Update with your file path
    
    # Example JSON input
    json_input = {
        "1": None,        # No player fixed in position 1
        "2": "Player2",   # Player2 is fixed to bat 2nd
        "3": None,        # No player fixed in position 3
        "4": "Player4",   # Player4 is fixed to bat 4th
        "5": None,        # No player fixed in position 5
        "6": None,        # No player fixed in position 6
        "7": None,        # No player fixed in position 7
        "8": None,        # No player fixed in position 8
        "9": None,        # No player fixed in position 9
        "10": "Player1",  # These are flexible players (can go in any position)
        "11": "Player3",
        "12": "Player5",
        "13": "Player6",
        "14": "Player7",
        "15": "Player8",
        "16": "Player9",
        "17": None,       # Not all positions 10-18 need to be filled
        "18": None
    }
    
    # CSV file to cache BDNRP calculations (to avoid recalculating)
    bdnrp_csv = "bdnrp_values.csv"
    
    # Run the optimization
    result_json = optimize_lineup_from_json(excel_file_path, json_input, bdnrp_csv, method='exhaustive', max_iterations=1000)
    
    # Print the final result
    print("\nFinal optimized lineup:")
    print(json.dumps(result_json, indent=2))