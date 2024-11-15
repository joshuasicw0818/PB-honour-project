import itertools
from typing import List
import random
import pandas as pd
import numpy as np

class PB:
    def __init__(self, metadata, projects, voters):
        self.projects = projects
        self.n = int(metadata['num_votes'])
        self.m = int(metadata['num_projects'])
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
        return float(self.projects[self.projects["project_id"] == project]["cost"].values[0])
    
    #subset cost function
    def cS(self, projects: List[str]):
        return sum([int(c) for c in self.projects[self.projects["project_id"].isin(projects)]["cost"]])

    def rank(self, voter, project):
        r = 1
        for i in range(len(self.pp[voter])):
            if project in self.pp[voter][i]:
                return r
            r += len(self.pp[voter][i])
        return r
    
    #generate all possible feasible subsets of projects
    def generate_f(self):
        possible_s = ()
        for i in range(0, len(self.A)+1):
            for subset in itertools.combinations(self.A, i):
                s_cost = self.cS(subset)

                if s_cost <= self.L:
                    possible_s += (subset,)
                elif s_cost > self.L:
                    break
        return possible_s
    



