import itertools
from typing import List
import pandas as pd
import numpy as np
import concurrent.futures
from functools import lru_cache

def rsg_satisfaction_worker(args):
    """
    worker function to count the number of satisfied voters in a subset for rsg_f
    Uses a vecotorized approach
    """
    subset, k, share, rank_matrix, cost_vector = args

    subset = list(subset)
    if not subset:
        return 0

    # Select relevant columns
    ranks = rank_matrix[:, subset]
    # mask is 1 if the rank is less than or equal to k, else 0
    mask = (ranks <= k).astype(int)
    # Compute the costs of the projects in the subset
    costs = cost_vector[subset]

    # Compute total cost of approved projects per voter
    voter_costs = (mask * costs).sum(axis=1)
    # Check if the total cost meets or exceeds the share
    satisfied = (voter_costs >= share).sum()

    # Return the number of satisfied voters
    return satisfied

class PB:
    def __init__(self, metadata, projects, voters):
        """
        Initializes the PB instance with the given metadata, projects, and voters.

        Parameters:
        - metadata: A dictionary containing metadata about the PB instance.
        - projects: A DataFrame containing information about the projects.
        - voters: A DataFrame containing information about the voters.
        """
        self.projects = projects
        self.voters = voters
        self.n = voters.shape[0]
        self.m = projects.shape[0]
        self.N = voters["voter_id"].values
        self.L = float(metadata['budget'])
        self.A = projects["project_id"].values
        
        # precomputed cost map for each project
        self.cost_map = {pid: float(cost) for pid, cost in zip(projects["project_id"], projects["cost"])}

        self.f = self.generate_f()

        #voter preference profile
        self.pp = voters.set_index("voter_id")['vote']
        self.pp = self.pp.str.split('|', expand=False)
        self.pp = self.pp.apply(lambda x: [s.split(',') for s in x])   
        
        # precomputed rank lookup for each voter and project
        self.rank_lookup = {
            (voter, project): rank
            for voter in self.N
            for rank, group in enumerate(self.pp[voter], start=1)
            for project in group
        } 
        
        # store feasible subsets with a specfic rsg applied (k, share)
        self.cached_rsgs = {} 

    #project cost function
    def c(self, project: str):
        """
        Returns the cost of the given project.
        """
        
        return self.cost_map[project]
    
    #subset cost function
    def cS(self, projects: List[str]):
        """
        Returns the total cost of the given subset of projects.
        """
        return sum(self.c(p) for p in projects)

    def rank(self, voter, project):
        """
        Returns the rank of the given project in the voter's preference list.
        If the project is not ranked, returns None.
        """
        return self.rank_lookup.get((voter, project), None)
    
    #generate all possible feasible subsets of projects
    def generate_f(self):
        """
        Generates all possible feasible subsets of projects.
        """
        possible_s = []
        # make a sorted copy of the project list
        sorted_projects = sorted(self.A, key=lambda pid: self.c(pid))
        
        # Iterate through all possible subset sizes
        for i in range(0, len(sorted_projects)+1):
            # Generate all combinations of projects of size i
            for subset in itertools.combinations(sorted_projects, i):
                s_cost = self.cS(subset)

                if s_cost <= self.L:
                    possible_s.append(subset)
                else:
                    break
        return possible_s
    
    def rsg_f(self, k, share):
        """
        Applies the RSG rule to the PB, returning the best subsets from the feasible set
        uses a vectorized approach to evaluate the satisfaction of voters

        Parameters:
        - k: The maximum rank threshold.
        - share: The minimum budget share required to satisfy a voter.

        Returns:
        - A list of subsets (best_s) that maximize the number of satisfied voters.
        """
        
        # Check if the result is already cached
        if (k, share) in self.cached_rsgs.keys():
            return self.cached_rsgs[(k, share)]

        # project ID to index mapping
        pid_to_idx = {pid: i for i, pid in enumerate(self.A)}
        
        # Build voter ID → index
        vid_to_idx = {vid: i for i, vid in enumerate(self.N)}
        
        cost_vector = np.array([self.c(pid) for pid in self.A]) 
        
        # Initialize rank_matrix with default m+1
        rank_matrix = np.full((len(self.N), len(self.A)), self.m + 1, dtype=int)

        # Fill it using rank_lookup
        for (voter, project), rank in self.rank_lookup.items():
            if project in pid_to_idx and voter in vid_to_idx:
                v_idx = vid_to_idx[voter]
                p_idx = pid_to_idx[project]
                rank_matrix[v_idx, p_idx] = rank

        # Map subsets to index-based tuples
        subset_args = [
            (
                [pid_to_idx[p] for p in subset],  # index-based subset
                k,
                share,
                rank_matrix,
                cost_vector
            )
            for subset in self.f # get each feasible subset
        ]

        # Vectorized evaluation
        best_s = []
        best_score = -float('inf')

        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Map the worker function to the subset arguments
            results = executor.map(rsg_satisfaction_worker, subset_args)
            # Iterate through the results and find the best subsets
            for s, score in zip(self.f, results):
                # if the score is better than the best score, update the best score and best_s
                if score > best_score:
                    best_score = score
                    best_s = [s]
                elif score == best_score:
                    best_s.append(s)
                    
        # Cache the result
        self.cached_rsgs[(k, share)] = best_s

        return best_s
    



