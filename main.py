import pandas as pd
import numpy as np
from evaluation import *
import os

from pb_instance import PB
from rules.atr import ATR
from rules.pbcc import PBCC

def parse_pb_file(filename):
    # Initialize dictionaries and lists to store metadata, projects, and votes
    metadata = {}
    projects = []
    votes = []
    
    # Open the file for reading
    with open(filename, 'r') as file:
        section = None          # Variable to track the current section of the file (e.g., 'META', 'PROJECTS', etc.)
        section_parsed = None   # Flag to indicate if the section has been parsed
        
        # Iterate through each line in the file
        for line in file:
            line = line.strip()
            
            # Check for section headers and set the current section accordingly
            if line == 'META':
                section = 'meta'  # Switch to the 'meta' section
                section_parsed = None  # Reset section parsing flag
                continue
            elif line == 'PROJECTS':
                section = 'projects'  
                section_parsed = None 
                continue
            if line == "VOTES":
                section = 'votes' 
                section_parsed = None  
                continue

            # Process the 'meta' section
            if section == 'meta':
                key, value = line.split(';', 1)  # Split the line into key and value at the first semicolon
                metadata[key] = value  # Store key-value pairs in the metadata dictionary

            # Process the 'projects' section
            elif section == 'projects':
                if not section_parsed:  # If it's the first line in the projects section
                    headers = line.split(';')  # Use this line to define the column headers
                    section_parsed = True  # Mark the section as parsed
                else:
                    # For subsequent lines, split the data by semicolon and zip with headers
                    project_data = line.split(';')
                    projects.append(dict(zip(headers, project_data)))  # Store the project data as a dictionary

            # Process the 'votes' section
            elif section == 'votes':
                if not section_parsed:  # If it's the first line in the votes section
                    headers = line.split(';')  
                    section_parsed = True
                else:
                    # For subsequent lines, split the data by semicolon and zip with headers
                    votes_data = line.split(';')
                    votes.append(dict(zip(headers, votes_data)))  # Store the votes data as a dictionary
                    
    # Return the parsed data: metadata as a dictionary, projects as a DataFrame, and votes as a DataFrame
    return metadata, pd.DataFrame(projects), pd.DataFrame(votes)

def parse_gen_voters(datafile, voterfile):
    """
    Parse the PB instance from the given datafile and the generated voters from the voterfile.
    """
    metadata, projects, _ = parse_pb_file(datafile)
    voters = pd.read_csv(voterfile)

    return metadata, projects, voters

def ouputTables(data, voterfiles, folder_names):
    for voterfile, folder_name in zip(voterfiles, folder_names):
        metadata, projects, voters = parse_gen_voters(data, voterfile)
        folder = f"output/{folder_name}"

        # create the folder if dont exist
        try:
            os.makedirs(folder)
        except FileExistsError:
            pass
        try:
            os.makedirs(f"{folder}/rsg")
        except FileExistsError:
            pass
        
        print(f"----Generating tables for {folder_name}----".center(50, "-"))
        
        # instantiate the PB class
        pb = PB(metadata, projects, voters)

        # get the comparison tables
        w_df, p_df, rsg_dfs = generateTables(pb)
        
        # save the tables to csv
        w_df.to_latex(f"{folder}/welfare.tex", float_format="%.2f")
        p_df.to_latex(f"{folder}/pmean.tex", float_format="%.2f")

        # save the rsg tables to csv
        for r_name, rsg_df in rsg_dfs.items():
            rsg_df.to_latex(f"{folder}/rsg/{r_name}.tex", float_format="%.2f")
        print(f"----Tables for {folder_name} generated----".center(50, "-"))

if __name__ == "__main__": 
    voterfiles = ["datasets/worldwide_turk7/generated/turk7.csv"]
    folder_names = ["worldwide_turk7"]
    ouputTables("datasets/worldwide_turk7/worldwide_mechanical-turk_ranking-value-money-7.pb", voterfiles, folder_names)
