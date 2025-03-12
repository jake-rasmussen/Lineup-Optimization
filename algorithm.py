import numpy as np
import pandas as pd
from itertools import permutations
from concurrent.futures import ProcessPoolExecutor
import time

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
        Calculate the expected run production for a given lineup.
        
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
            
            # Add this 4-tuple's contribution to the total score
            total_score += self._get_bdnrp(p1, p2, p3, p4)
        
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
        # Generate all possible permutations of the lineup
        all_lineups = list(permutations(self.players, 9))
        total_lineups = len(all_lineups)
        print(f"Evaluating {total_lineups} possible lineups...")
        
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
    
    def _optimize_genetic(self, max_iterations=1000):
        """
        Genetic algorithm implementation for lineup optimization.
        This is a stochastic approach that can find near-optimal solutions faster.
        """
        # Implementation for genetic algorithm
        # Details omitted for brevity but would include:
        # - Population initialization with random lineups
        # - Fitness evaluation using the evaluate_lineup function
        # - Selection of top performers
        # - Crossover to create new lineup combinations
        # - Mutation to maintain diversity
        # - Termination after max_iterations or convergence
        
        print("Genetic algorithm implementation not provided in this sample")
        return None, 0.0
    
    def _optimize_simulated_annealing(self, max_iterations=10000):
        """
        Simulated annealing implementation for lineup optimization.
        Another stochastic approach that can escape local optima.
        """
        # Implementation for simulated annealing
        # Details omitted for brevity but would include:
        # - Start with a random lineup
        # - At each step, consider a neighboring lineup (swap two positions)
        # - Accept better solutions always, worse solutions with decreasing probability
        # - Decrease temperature parameter over time to reduce acceptance of worse solutions
        # - Terminate after max_iterations or when temperature reaches minimum
        
        print("Simulated annealing implementation not provided in this sample")
        return None, 0.0
    
    def get_lineup_stats(self, lineup=None):
        """
        Get detailed statistics for a lineup.
        
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
            
            bdnrp = self._get_bdnrp(p1, p2, p3, p4)
            stats.append({
                'position': i+1,
                'player': p4,
                'prev_three': [p1, p2, p3],
                'bdnrp': bdnrp
            })
        
        return pd.DataFrame(stats)

# Example usage
if __name__ == "__main__":
    # Create sample data - in practice, this would be loaded from your BDNRP sheets
    players = ["Player1", "Player2", "Player3", "Player4", "Player5", 
               "Player6", "Player7", "Player8", "Player9"]
    
    # Create sample BDNRP data
    # In practice, this would be your actual BDNRP calculations
    sample_data = []
    for p1 in players:
        for p2 in players:
            for p3 in players:
                for p4 in players:
                    if len({p1, p2, p3, p4}) == 4:  # Ensure all players are different
                        # Generate a sample BDNRP value - replace with actual values
                        bdnrp = np.random.normal(0.5, 0.2)
                        sample_data.append({
                            'player1': p1,
                            'player2': p2,
                            'player3': p3,
                            'player4': p4,
                            'bdnrp_value': bdnrp
                        })
    
    bdnrp_df = pd.DataFrame(sample_data)
    
    # Initialize and run the optimizer
    optimizer = LineupOptimizer(bdnrp_df, players)
    
    # For demonstration, use a smaller subset of players to make exhaustive search feasible
    demo_players = players[:6]  # Only optimize for 6 players = 720 permutations
    demo_optimizer = LineupOptimizer(bdnrp_df, demo_players)
    
    best_lineup, best_score = demo_optimizer.optimize(method='exhaustive', batch_size=100)
    
    print(f"\nBest lineup: {best_lineup}")
    print(f"Expected run production: {best_score:.4f}")
    
    # Get detailed stats for the best lineup
    lineup_stats = demo_optimizer.get_lineup_stats()
    print("\nDetailed lineup breakdown:")
    print(lineup_stats)