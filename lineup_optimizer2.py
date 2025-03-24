import numpy as np
import pandas as pd
from itertools import permutations
from concurrent.futures import ProcessPoolExecutor
import time
import win32com.client as win32
import os
import random

class LineupOptimizer:
    def __init__(self, bdnrp_data, players):
        """
        Initialize the lineup optimizer with BDNRP data and player list.
        
        Args:
            bdnrp_data (DataFrame): DataFrame containing the BDNRP values for 4-tuples
                                    Should have columns for player1, player2, player3, player4, and bdnrp_value
            players (list): List of player IDs/names to be included in the lineup
        """
        self.bdnrp_data = bdnrp_data
        self.players = players
        self.best_lineup = None
        self.best_score = float('-inf')
        self.evaluated_lineups = 0
        
        # Create a lookup dictionary for quick access to BDNRP values
        self.bdnrp_lookup = self._create_bdnrp_lookup()
    
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
    
    def evaluate_lineup(self, lineup):
        """
        Calculate the expected run production for a given lineup, accounting for
        the probability of extra at-bats for players at the top of the order.
        
        Args:
            lineup (list): A specific ordering of self.players
            
        Returns:
            float: The total expected run production
        """
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
        
        if method == 'exhaustive':
            return self._optimize_exhaustive(batch_size)
        elif method == 'genetic':
            return self._optimize_genetic(max_iterations)
        elif method == 'simulated_annealing':
            return self._optimize_simulated_annealing(max_iterations)
        else:
            raise ValueError(f"Unknown optimization method: {method}")
    
    def _optimize_exhaustive(self, batch_size=10000):
        """
        Exhaustively evaluate all possible lineups.
        Uses parallel processing to speed up computation.
        """
        # Record start time for this method
        start_time = time.time()
        
        # Generate all possible permutations of the lineup
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
        
        # Initialize population with random lineups
        population = []
        for _ in range(population_size):
            # Create a random permutation of players
            lineup = list(self.players)
            random.shuffle(lineup)
            population.append(lineup)
        
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
                
                # Order crossover
                child = self._order_crossover(parent1, parent2)
                
                # Mutation
                child = self._mutate(child, mutation_rate)
                
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
    
    def _order_crossover(self, parent1, parent2):
        """Order crossover for permutation problems."""
        size = len(parent1)
        
        # Choose crossover points
        start, end = sorted(random.sample(range(size), 2))
        
        # Create child with parent1 segment
        child = [None] * size
        for i in range(start, end + 1):
            child[i] = parent1[i]
        
        # Fill the rest with parent2 order
        parent2_idx = 0
        for i in range(size):
            if child[i] is None:
                while parent2[parent2_idx] in child:
                    parent2_idx += 1
                child[i] = parent2[parent2_idx]
                parent2_idx += 1
        
        return child
    
    def _mutate(self, lineup, mutation_rate):
        """Mutate a lineup by swapping positions."""
        for i in range(len(lineup)):
            if random.random() < mutation_rate:
                j = random.randint(0, len(lineup) - 1)
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
        
        # Start with a random solution
        current_lineup = list(self.players)
        random.shuffle(current_lineup)
        
        current_score = self.evaluate_lineup(current_lineup)
        best_lineup = list(current_lineup)
        best_score = current_score
        self.evaluated_lineups += 1
        
        # Initialize temperature
        temp = initial_temp
        
        # Main simulated annealing loop
        for iteration in range(max_iterations):
            # Create a neighbor by swapping two positions
            neighbor = list(current_lineup)
            i, j = random.sample(range(len(neighbor)), 2)
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            
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
            
            stats.append({
                'position': i+1,
                'player': p4,
                'prev_three': [p1, p2, p3],
                'base_bdnrp': base_bdnrp,
                'extra_ab_prob': extra_ab_probability,
                'position_weight': position_weight,
                'weighted_bdnrp': weighted_bdnrp
            })
        
        df = pd.DataFrame(stats)
        df['contrib_pct'] = (df['weighted_bdnrp'] / df['weighted_bdnrp'].sum()) * 100
        
        return df

def setup_excel(file_path):
    """Connect to Excel and open the workbook."""
    excel = win32.Dispatch('Excel.Application')
    excel.Visible = False  # Run Excel in the background
    workbook = excel.Workbooks.Open(file_path)
    sheet = workbook.Sheets("4 tuple values 0 outs")
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

def optimize_lineup(excel_file_path, players, bdnrp_csv=None, method='genetic', max_iterations=1000):
    """End-to-end function to optimize lineup based on BDNRP values."""
    # Generate or load BDNRP data
    print("Step 1: Preparing BDNRP data...")
    bdnrp_data = generate_bdnrp_data(players, excel_file_path, output_csv=bdnrp_csv)
    
    # Initialize the optimizer
    print("\nStep 2: Initializing lineup optimizer...")
    optimizer = LineupOptimizer(bdnrp_data, players)
    
    # Run the optimization
    print("\nStep 3: Running lineup optimization...")
    if method == 'exhaustive':
        best_lineup, best_score = optimizer.optimize(method='exhaustive', batch_size=10000)
    elif method == 'genetic':
        best_lineup, best_score = optimizer.optimize(method='genetic', max_iterations=max_iterations)
    elif method == 'simulated_annealing':
        best_lineup, best_score = optimizer.optimize(method='simulated_annealing', max_iterations=max_iterations)
    else:
        raise ValueError(f"Unknown optimization method: {method}")
    
    # Display results
    print("\n===== OPTIMIZATION RESULTS =====")
    print(f"Best lineup: {best_lineup}")
    print(f"Expected run production: {best_score:.4f}")
    
    # Get detailed stats for the best lineup
    lineup_stats = optimizer.get_lineup_stats()
    print("\nDetailed lineup breakdown:")
    print(lineup_stats)
    
    # Save results to CSV
    results_csv = "lineup_optimization_results.csv"
    lineup_stats.to_csv(results_csv, index=False)
    print(f"\nDetailed results saved to {results_csv}")
    
    return best_lineup, best_score, lineup_stats

if __name__ == "__main__":
    # Configuration
    excel_file_path = r"C:\path\to\Lineup Optimization 1.xlsx"  # Update with your file path
    
    # Your list of 9 players (update these names to match your Excel file)
    players = ["Player1", "Player2", "Player3", "Player4", "Player5", 
               "Player6", "Player7", "Player8", "Player9"]
    
    # CSV file to cache BDNRP calculations (to avoid recalculating)
    bdnrp_csv = "bdnrp_values.csv"
    
    # Run the optimization (choose method: 'exhaustive', 'genetic', or 'simulated_annealing')
    # Use 'genetic' or 'simulated_annealing' for faster results with 9 players
    optimize_lineup(excel_file_path, players, bdnrp_csv, method='genetic', max_iterations=1000)