from rules.rule import Rule

# Define the ATR class inheriting from the Rule class
class ATR(Rule):
    
    def __init__(self, f):
        """
        Initialize the ATR object with a utility function f.
        Parameters:
        - f: The utility function to maximize ("|.|", "c", or "1").
        """
        self.f = f

    def apply(self, pb):
        """
        Apply the approval translation rule (ATR) to the given participatory budgeting (PB) instance.
        Steps:
        - Translate weak rankings into approval votes.
        - Maximize the utility function based on the approval votes.

        Parameters:
        - pb: The PB instance containing voters, projects, preferences, and budget.

        Returns:
        - The subset of projects that maximizes the utility function.
        """
        appr_votes = {}  # Dictionary to store approval votes for each voter

        # Loop through each voter in the PB instance
        for voter in pb.N:
            appr_votes[voter] = []  # Initialize the list of approved projects for this voter
            j = 1  # Start with the first rank in the preference profile

            # Add projects while staying within the budget
            while pb.cS(appr_votes[voter]) + pb.cS(pb.pp[voter][j-1]) <= pb.L:
                appr_votes[voter].extend(pb.pp[voter][j-1])  # Add projects from the current rank
                j += 1

            # Check remaining projects in the current rank for partial inclusion
            over = []  # List to store projects that can still fit within the budget
            for p in pb.pp[voter][j-1]:
                if pb.c(p) < pb.L - pb.cS(appr_votes[voter]):  # If adding project p doesn't exceed the budget
                    over.append(p)

            appr_votes[voter].extend(over)  # Add the remaining feasible projects
        
        # Maximize utility based on the approval votes
        return self.maximize(appr_votes, pb)

    def maximize(self, appr_votes, pb):
        """
        Find the feasible subset of projects that maximizes the utility function.

        Parameters:
        - appr_votes: A dictionary of approval votes for each voter.
        - pb: The PB instance containing voters, projects, preferences, and budget.

        Returns:
        - A list of subsets (best_s) that maximizes the utility function.
        """
        best_s = []  # List to store the best subsets
        best_u = -float('inf')  # Initialize the best utility as negative infinity

        # Loop through all feasible subsets of projects
        for s in pb.f:
            total_u = 0  # Initialize the total utility for this subset

            # Calculate the utility for each voter
            for i in pb.N:
                inter = set(appr_votes[i]).intersection(s)  # Intersection of approval votes and the subset

                # Compute utility based on the specified utility function
                if self.f == "|.|":
                    total_u += len(inter)  # Count the number of approved projects
                elif self.f == "c":
                    total_u += pb.cS(inter)  # Sum the costs of approved projects
                elif self.f == "1":
                    total_u += 1 if len(inter) > 0 else 0  # Add 1 if at least one project is approved

            # Update the best subset(s) if a higher utility is found
            if total_u > best_u:
                best_u = total_u
                best_s = [s]  # Replace with the current subset
            elif total_u == best_u:
                best_s.append(s)  # Add to the list of subsets with the same utility

        return best_s  # Return the subset(s) with the highest utility
