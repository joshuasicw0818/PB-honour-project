from pb_instance import PB
import numpy as np


def utilitarianWelfare(pb, selected_subsets):
    """
    Calculate the utilitarian welfare: sum of utilities for all voters.
    """
    avg_total_utility = 0

    for s in selected_subsets:
        total_utility = 0
        for voter in pb.N:
            # Utility = count of approved projects
            total_utility += sum([1 for p in s if pb.rank(voter, p)])
        avg_total_utility += total_utility  
    return avg_total_utility / len(selected_subsets)

def egalitarianWelfare(pb, selected_subsets):
    """
    Calculate the egalitarian welfare: minimum utility for any voter.
    """
    min_utility = float('inf')
    for s in selected_subsets:
        for voter in pb.N:
            # Utility = count of approved projects
            utility = sum([1 for p in s if pb.rank(voter, p)])
            if utility < min_utility:
                min_utility = utility
    return min_utility

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
        product = np.prod(utilities)
        avg_nash_welfare += product ** (1 / len(utilities))  # Geometric mean of utilities

    return avg_nash_welfare / len(selected_subsets) if selected_subsets else 0  # Handle empty list of subsets


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
        avg_pmean_welfare += (sum([u ** p for u in utilities]) / len(utilities)) ** (1 / p)

    return avg_pmean_welfare / len(selected_subsets) if selected_subsets else 0  # Handle empty list of subsets


def proportionality(pb, selected_subsets):
    None

def individualShare(pb, selected_subsets):
    # every voter has a minimum amount of the budget allocated to their preferences, find this minimum

    # for each voter, find the cost of the projects they approved
    individual_shares = []
    for s in selected_subsets:
        for voter in pb.N:
            approved_projects = [project for project in s if pb.rank(voter, project)]
            cost = pb.cS(approved_projects)
            individual_shares.append(cost)
    return min(individual_shares)

def evaluateRule(pb, rule):
    """
    Apply a PB rule and evaluate it against the defined metrics.

    Parameters:
    - pb: The PB instance containing the projects, voters, etc.
    - rule: The PB rule to apply (e.g., PBCC, RSG).

    Returns:
    - A dictionary with the metric names and their corresponding values.
    """
    selected_subsets = rule.apply(pb)
    metrics = {
        'Utilitarian Welfare': utilitarianWelfare(pb, selected_subsets),
        'Egalitarian Welfare': egalitarianWelfare(pb, selected_subsets),
        'Nash Welfare': nashWelfare(pb, selected_subsets),
        'p-Mean Welfare (p=1)': pMeanWelfare(pb, selected_subsets, 1),
        'Individual Share': individualShare(pb, selected_subsets)
    }
    return metrics


def generateTable(pb, rules):
    """
    Generate a table of metric values for each rule applied to the PB instance.

    Parameters:
    - pb: The PB instance containing the projects, voters, etc.
    - rules: A list of PB rules to apply.

    Returns:
    - A DataFrame with the metric values for each rule.
    """
    import pandas as pd

    table = []
    for rule in rules:
        metrics = evaluateRule(pb, rule)
        table.append(metrics)

    return pd.DataFrame(table, index=[rule.__class__.__name__ for rule in rules])