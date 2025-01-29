from pb_instance import PB
import numpy as np
import pandas as pd
from rules.atr import ATR
from rules.pbcc import PBCC
from colorama import Fore, Style, init
init(autoreset=True)
def utilitarianWelfare(pb, selected_subsets):
    """
    Calculate the utilitarian welfare: sum of utilities for all voters.
    """
    total_utility = 0

    for s in selected_subsets:
        for voter in pb.N:
            # Utility = count of approved projects
            total_utility += sum([1 for p in s if pb.rank(voter, p)]) 
    return total_utility / len(selected_subsets)

def egalitarianWelfare(pb, selected_subsets):
    """
    Calculate the egalitarian welfare: minimum utility for any voter.
    """
    # Minimum total utility across all selected subsets
    min_total_utility = float('inf')
    for s in selected_subsets:
        # List to store utilities for each voter in the current subset
        utilities = []
        for voter in pb.N:
            # Utility = count of approved projects
            utility = sum([1 for p in s if pb.rank(voter, p)])
            utilities.append(utility)
        min_total_utility = min(min_total_utility, min(utilities))
    return min_total_utility

def nashWelfare(pb, selected_subsets):
    """
    Calculate Nash welfare: the geometric mean of individual utilities across all selected subsets.
    
    For each subset, the utility for each voter is the number of projects they approve.
    The function returns the geometric mean of utilities for all voters across all subsets.
    """
    avg_nash_welfare = 0  # Initialize the total nash welfare

    # Loop over each selected subset
    for s in selected_subsets:
        # List to store utilities for each voter in the current subset
        utilities = []

        # Calculate the utility for each voter in the current subset
        for voter in pb.N:
            # Utility for this voter is the number of projects they approve in the subset
            utilities.append(sum([1 for project in s if pb.rank(voter, project)]))
        
        # Calculate the geometric mean of utilities for the current subset
        product = np.prod(np.array(utilities, dtype=np.float64))
        avg_nash_welfare += product ** (1 / pb.n)  # Geometric mean of utilities
    return avg_nash_welfare / len(selected_subsets) if selected_subsets else 0


def pMeanWelfare(pb, selected_subsets, p):
    """
    Calculate p-mean welfare: generalized utility metric across all selected subsets.
    
    For each subset, the utility for each voter is the number of projects they approve.
    The function calculates the p-mean of utilities for all voters across all subsets.
    """
    avg_pmean_welfare = 0  # Initialize the total p-mean welfare

    # Loop over each selected subset
    for s in selected_subsets:
        # List to store utilities for each voter in the current subset
        utilities = []

        # Calculate the utility for each voter in the current subset
        for voter in pb.N:
            # Utility for this voter is the number of projects they approve in the subset
            utilities.append(sum([1 for project in s if pb.rank(voter, project)]))

        # Calculate the p-mean of utilities for the current subset
        if p == 0:
            # When p=0, use the geometric mean
            product = np.prod(np.array(utilities, dtype=np.float64))
            avg_pmean_welfare += product ** (1 / len(utilities))
        else:
            avg_pmean_welfare += (sum([u ** p for u in utilities]) / len(utilities)) ** (1 / p)

    return avg_pmean_welfare / len(selected_subsets) 

def proportionality(pb, selected_subsets):
    groups = list(pb.voters["sex"].unique()) + list(pb.voters["education"].unique())
    groups_pd = pd.DataFrame(index=groups, columns=['count','budg_repped',"seen","prop"])

    for sex in pb.voters["sex"].unique():
        count = pb.voters[pb.voters["sex"] == sex].shape[0]
        groups_pd.loc[sex,"count"] = count
    for education in pb.voters["education"].unique():
        count = pb.voters[pb.voters["education"] == education].shape[0]
        groups_pd.loc[education,"count"] = count
    groups_pd["prop"] = [[] for i in range(len(groups_pd))]
    
    # Iterate through each selected subset of projects
    for s in selected_subsets:
        groups_pd["budg_repped"] = 0
        groups_pd["seen"] = [[] for i in range(len(groups_pd))]

        # assign budgets to groups
        for p in s:
            for voter in pb.N:
                if pb.rank(voter, p): # If the voter ranks the project
                    for group in groups_pd.index:
                        # If the project has not been allocated to this group yet
                        if p not in groups_pd.loc[group,"seen"]:
                            # Add the cost of the project to the group's budget representation
                            groups_pd.loc[group,"budg_repped"] += pb.c(p)
                            groups_pd.loc[group,"seen"].append(p)
                
        for group in groups_pd.index:
            if groups_pd.loc[group,"count"] > 0:
                group_frac = groups_pd.loc[group,"count"] / pb.n
                budg_frac = groups_pd.loc[group,"budg_repped"] / pb.L

                groups_pd.loc[group,"prop"].append(budg_frac / group_frac)
    groups_pd["prop"] = [np.mean(groups_pd.loc[group,"prop"]) for group in groups_pd.index]
    return np.mean(groups_pd["prop"])

def getRuleMetrics(pb, selected_subsets):
    w_metrics = {
        'Utilitarian': utilitarianWelfare(pb, selected_subsets),
        'Egalitarian': egalitarianWelfare(pb, selected_subsets),
        'Nash': nashWelfare(pb, selected_subsets),
        'AVG Prop': proportionality(pb, selected_subsets)
    }
    return w_metrics

def generateTables(pb):
    """
    Generate all tables of metric values for each rule applied to the PB instance.

    Parameters:
    - pb: The PB instance containing the projects, voters, etc.
    - rules: A list of PB rules to apply.

    Returns:
    - DataFrames with the metric values for each rule.
    """
    
    #dict of rules with rule label as key and rule object as value
    rules = {
        'ATR |.|': ATR("|.|"),
        'ATR c': ATR("c"),
        'ATR 1': ATR("1"),
        'PBCC': PBCC()
    }

    # Generate welfare table
    print(Fore.YELLOW + "Generating welfare table...")
    w_df = pd.DataFrame(columns=['Utilitarian', 'Egalitarian', 'Nash', 'AVG Prop'])
    rsg_ratios = [1,2,5]
    for r_name, rule in rules.items():
        w_df.loc[r_name] = getRuleMetrics(pb, rule.apply(pb))
        for rsg_r in rsg_ratios:
            w_df.loc[f"{r_name} RSG(1/{rsg_r})"] = getRuleMetrics(pb, rule.apply(pb, True, pb.m//rsg_r, pb.L/pb.n))
    print(Fore.GREEN + "Welfare table generated.")
    
    print("Generating RSG tables...")
    rsg_dfs = {}
    # range of k values to test
    k_range = [k for k in range(1,11)]

    for r_name, rule in rules.items():
        df = pd.DataFrame(columns=['Utilitarian', 'Egalitarian', 'Nash', 'AVG Prop'])
        df.index.name = 'k'
        for k in k_range:
            # share set to L/n
            selected_subsets = rule.apply(pb, True, pb.m//k , pb.L/pb.n)
            df.loc[f"1/{k}"] = getRuleMetrics(pb, selected_subsets)
        rsg_dfs[r_name] = df
        print(Fore.YELLOW + f"{r_name} RSG table generated.")
    print(Fore.GREEN + "RSG tables generated.")

    print("Generating p-mean welfare table...")
    # Generate p-mean welfare table
    p_vals = np.linspace(0, 1, 11)
    p_df = pd.DataFrame(columns=[f'{p:.1f}' for p in p_vals])

    for r_name, rule in rules.items():
        selected_subsets = rule.apply(pb)
        p_metrics = {}
        for p in p_vals:
            p_metrics[f'{p:.1f}'] = pMeanWelfare(pb, selected_subsets, p)
        p_df.loc[r_name] = p_metrics
    print(Fore.GREEN + "p-mean welfare table generated.")
    return w_df, p_df, rsg_dfs