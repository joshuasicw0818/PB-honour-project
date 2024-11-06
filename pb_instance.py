import itertools
from typing import List
import pandas as pd
import numpy as np

class PB:
    def __init__(self, metadata, projects, voters):
        self.projects = projects
        self.n = metadata['num_votes']
        self.m = metadata['num_projects']
        self.A = projects["project_id"].values
        self.N = voters["voter_id"].values
        self.L = float(metadata['budget'])

        self.pp = voters.set_index("voter_id")['vote']
        self.pp = self.pp.str.split(',', expand=False)
        self.f = self.generate_f()

    #project cost function
    def c(self, project: str):
        return float(self.projects[self.projects["project_id"] == project]["cost"].values[0])
    
    #subset cost function
    def cS(self, projects: List[str]):
        return sum([int(c) for c in self.projects[self.projects["project_id"].isin(projects)]["cost"]])

    def rank(self, voter, project):
        return self.pp[voter].index(project)+1
    
    def generate_f(self):
        possible_s = []
        for i in range(1, len(self.A)+1):
            s = list(itertools.combinations(self.A, i))
            if self.cS(s) <= self.L:
                possible_s.extend(s)
        return possible_s



