import itertools
from typing import List
import pandas as pd
import numpy as np
import concurrent.futures
from functools import lru_cache

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
        self.A = projects["project_id"].values
        self.N = voters["voter_id"].values
        self.L = float(metadata['budget'])
        self.f = self.generate_f()

        #voter preference profile
        self.pp = voters.set_index("voter_id")['vote']
        self.pp = self.pp.str.split('|', expand=False)
        self.pp = self.pp.apply(lambda x: [s.split(',') for s in x])      

    #project cost function
    def c(self, project: str):
        """
        Returns the cost of the given project.
        """
        return float(self.projects[self.projects["project_id"] == project]["cost"].values[0])
    
    #subset cost function
    def cS(self, projects: List[str]):
        """
        Returns the total cost of the given subset of projects.
        """
        return sum([int(c) for c in self.projects[self.projects["project_id"].isin(projects)]["cost"]])

    def rank(self, voter, project):
        """
        Returns the rank of the given project in the voter's preference list.
        """
        r = 1
        for e_c in self.pp[voter]:
            if project in e_c:
                return r
            r += len(e_c)
        return None
    
    #generate all possible feasible subsets of projects
    def generate_f(self):
        """
        Generates all possible feasible subsets of projects.
        """
        possible_s = ()
        for i in range(0, len(self.A)+1):
            for subset in itertools.combinations(self.A, i):
                s_cost = self.cS(subset)

                if s_cost <= self.L:
                    possible_s += (subset,)
                elif s_cost > self.L:
                    break
        return possible_s
    
    # function to calculate the rank threshold for a given voter and subset
    @lru_cache(maxsize=None)
    def t(self, voter, s, share):
            if self.cS(s) < share:
                #If the total cost of the subset is less than the share, return a large rank
                return self.m + 1
            for j in range(1, self.m + 1):
                # Find projects in the subset with rank <= j for this voter
                inter = (p for p in s if self.rank(voter, p) and self.rank(voter, p) <= j)

                # Check if the total cost of these projects meets or exceeds the share
                if self.cS(inter) >= share:
                    return j
            return self.m + 1
    
    # helper function to count the number of satisfied voters in a subset
    def cntSatisfaction(self, s, k, share):
            """
            Count the number of voters satisfied by the subset `s`.
            This will be run in parallel.
            """
            return len([i for i in self.N if self.t(i, s, share) <= k])
    
    def rsg_f(self, k, share):
        """
        Applies the RSG rule to the PB, returning the best subsets from the feasible set

        Parameters:
        - k: The maximum rank threshold.
        - share: The minimum budget share required to satisfy a voter.

        Returns:
        - A list of subsets (best_s) that maximize the number of satisfied voters.
        """
        best_s = []  # List to store the best subsets
        best_size = -float('inf')

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(lambda s: self.cntSatisfaction(s, k, share), self.f)

        for s, cnt in zip(self.f, results):
            if cnt > best_size:
                best_size = cnt
                best_s = [s]
            elif cnt == best_size:
                best_s.append(s)

        return best_s 
    

    



