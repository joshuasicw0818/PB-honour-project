# Participatory Budgeting Under Weak Rankings – Honour Project

This project evaluates and compares voting rules for indivisible Participatory Budgeting (PB) under weak rankings, building upon the methods proposed in Sreedurga et al. (2022).

## Contents
PB-honour-project/ ├── datasets/ # Contains original and generated datasets │ ├── stanford_2021/ # Main dataset used for experiments │ │ ├── og.csv # Original ordinal votes │ │ └── generated/ # Weak ranking versions of the above │ │ └── turk.csv ├── rules/ # Implementations of PB rules │ ├── atr.py # Approval Translation Rules │ ├── pbcc.py # PB-CC Rule │ └── rule.py # Base class for rules ├── main.py # Script to run experiments ├── evaluation.py # Welfare metric calculations ├── utils/ # Helper functions ├── plots/ # Output directory for figures and tables └── ug/ # Dissertation content and LaTeX tables

## Dataset Information
Datasets are sourced from https://pabulib.org/?vtype=ordinal
The one used for the dissertation is datasets/worldwide_turk7/worldwide_mechanical-turk_ranking-value-money-7.pb

## How to run
Generate weak rankings from pb files by running generator.py and changing parameters in genWeakRanks

Run evaluation of rules by running main.
Results will be uploaded in the output folder.
Generated output includes:
    Welfare tables comparing rules and RSG variants
    p-mean analysis
    RSG sensitivity analysis across 𝑘

output is as latex tables

