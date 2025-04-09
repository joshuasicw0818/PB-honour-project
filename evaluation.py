from concurrent.futures import ThreadPoolExecutor
from pb_instance import PB
import numpy as np
import pandas as pd
from rules.atr import ATR
from rules.pbcc import PBCC
from colorama import Fore, Style, init\
    
init(autoreset=True)
def utilitarianWelfare(pb, selected_subsets):
    """
    Calculate the utilitarian welfare: sum of utilities for all voters.
    """
    total_utility = 0

    # Loop over each selected subset
    for s in selected_subsets:
        for voter in pb.N:
            # Utility = count of approved projects
            total_utility += sum([1 for p in s if pb.rank(voter, p)])
            
    # Return the average utility for each voter across all selected subsets
    return total_utility / (len(selected_subsets) * pb.n) if selected_subsets else 0

def egalitarianWelfare(pb, selected_subsets):
    """
    Calculate the egalitarian welfare: minimum utility for any voter.
    """
    # The average Minimum total utility of selected subsets
    min_utilities = []

    for s in selected_subsets:
        # List to store utilities for each voter in the current subset
        utilities = []
        for voter in pb.N:
            # Utility = count of approved projects
            utility = sum([1 for p in s if pb.rank(voter, p)])
            utilities.append(utility)

        # Store the minimum utility for this subset
        min_utilities.append(min(utilities))
        # print min and max

    # Return the average minimum utility across all best subsets
    return sum(min_utilities) / len(min_utilities)

def nashWelfare(pb, selected_subsets):
    """
    Calculate Nash welfare: the geometric mean of individual utilities across all selected subsets.
    
    For each subset, the utility for each voter is the number of projects they approve.
    The function returns the geometric mean of utilities for all voters across all subsets.
    """
    avg_nash = 0  # Initialize the total nash welfare
    epsilon = 1e-6  # Small value to avoid log(0)

    # Loop over each selected subset
    for s in selected_subsets:
        # List to store utilities for each voter in the current subset
        utilities = []

        # Calculate the utility for each voter in the current subset
        for voter in pb.N:
            # Utility for this voter is the number of projects they approve in the subset
            util = sum([1 for project in s if pb.rank(voter, project)])
            if util == 0:
                utilities.append(epsilon)  # Avoid log(0) by using epsilon
            
            utilities.append(util)  # Append the utility for this voter
        
        utilities = np.array(utilities, dtype=np.float64)  # Convert to numpy array for numerical stability
        
        # Calculate the geometric mean of utilities for the current subset
        nash = np.exp(np.mean(np.log(utilities + epsilon)))  # Add epsilon to avoid log(0)
        avg_nash += nash

    # get the average nash welfare across all selected subsets
    return avg_nash / len(selected_subsets) if selected_subsets else 0


def pMeanWelfare(pb, selected_subsets, p):
    """
    Calculate p-mean welfare: generalized utility metric across all selected subsets.
    
    For each subset, the utility for each voter is the number of projects they approve.
    The function calculates the p-mean of utilities for all voters across all subsets.
    """
    avg_pmean_welfare = 0  # Initialize the total p-mean welfare

    # Loop over each selected subset
    for s in selected_subsets:
        
        # np array to store utilities for each voter in the current subset
        utils = np.array([
            # Utility for this voter is the number of projects they approve in the subset
            sum([1 for project in s if pb.rank(voter, project)]) or 1e-6  # Avoid zero utility
            for voter in pb.N
        ], dtype=np.float64)  # Convert to numpy array for numerical stability

        # Calculate the p-mean of utilities for the current subset
        if p == 0:
            # Geometric mean (log space)
            pmean = np.exp(np.mean(np.log(utils)))
        else:
            # For other values of p, use the generalized mean
            pmean = (np.mean(utils ** p)) ** (1 / p)
        avg_pmean_welfare += pmean

    # Return the average p-mean welfare across all selected subsets
    # If selected_subsets is empty, return 0 to avoid division by zero
    return avg_pmean_welfare / len(selected_subsets) if selected_subsets else 0

def getRuleMetrics(pb, selected_subsets):
    w_metrics = {
        'Utilitarian': utilitarianWelfare(pb, selected_subsets),
        'Egalitarian': egalitarianWelfare(pb, selected_subsets),
        'Nash': nashWelfare(pb, selected_subsets),
        'P(0.2) Mean': pMeanWelfare(pb, selected_subsets, 0.2)
    }
    return w_metrics

def generateTables(pb: PB):
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
    
    # Create a DataFrame to store welfare metrics
    w_df = pd.DataFrame(columns=['Utilitarian', 'Egalitarian', 'Nash', 'P(0.2) Mean'])
    
    # iterate through each rule and calculate the metrics
    for r_name, rule in rules.items():
        print(Fore.LIGHTCYAN_EX + f"    Generating {r_name} welfare table...")
        # Apply the rule to get the selected subsets
        w_df.loc[r_name] = getRuleMetrics(pb, rule.apply(pb))
        
    print(Fore.GREEN + "Welfare table generated.")
    
    print(Fore.YELLOW + "Generating RSG tables...")
    rsg_dfs = {}
    # range of k values to test

    k_set = [1, 2, 3, 4, 5, 7, 10]
    #get avg cost of projects
    avg_cost = pb.cS(pb.A) / pb.m
    
    for r_name, rule in rules.items():
        df = pd.DataFrame(columns=['Utilitarian', 'Egalitarian', 'Nash', 'P(0.2) Mean'])
        df.index.name = 'k'

        for k in k_set:
            # share set to L/n
            selected_subsets = rule.apply(pb, True, k , pb.L/pb.m)
                     
            # Calculate the welfare metrics for each k value
            df.loc[f"Top-{k}"] = getRuleMetrics(pb, selected_subsets)
        rsg_dfs[r_name] = df
        print(Fore.LIGHTCYAN_EX + f"  {r_name} RSG table generated.")
    print(Fore.GREEN + "RSG tables generated.")
    
    """ 
    Generate p-mean welfare table, 
        showing p-mean welfare for p values from 0 to 1 for each rule
    """
    print(Fore.YELLOW + "Generating p-mean welfare table...")
    p_vals = [0.0, 0.2, 0.5, 1.0]
    # Create a DataFrame to store p-mean welfare metrics
    p_df = pd.DataFrame(columns=[f'{p:.1f}' for p in p_vals])

    # iterate through each rule and calculate the metrics
    for r_name, rule in rules.items():
        print(Fore.LIGHTCYAN_EX + f"    Generating {r_name} p-mean welfare table...")
        # Apply the rule to get the selected subsets
        selected_subsets = rule.apply(pb)
        
        # helper function to compute p-mean welfare for each p value
        def compute_pmean(p):
            # Calculate the p-mean welfare for the current p value
            return f'{p:.1f}', pMeanWelfare(pb, selected_subsets, p)
        
        # Use multithreading to compute p-mean for each p
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(compute_pmean, p_vals))
        
        # Convert the results to a dictionary
        p_metrics = {
            p: metric for p, metric in results
        }
        # Add the metrics for that rule to the DataFrame
        p_df.loc[r_name] = p_metrics
    print(Fore.GREEN + "p-mean welfare table generated.")
    return w_df, p_df, rsg_dfs