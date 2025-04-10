from random import randint,sample
from main import parse_pb_file
import os

# This script generates weak ranks for voters from a PB instance.
def genWeakRanks(pbfile, filename, vote_range, rank_range):
    metadata, projects, voters = parse_pb_file(pbfile)

    print("Generating weak ranks...")
    
    for count, voter in enumerate(voters["voter_id"].values, start=1):
        # Print progress every 25% of the voters
        if count % int(len(voters) / 4) == 0:
            print(f"Voter: {count}/{len(voters)}")

        # split vote string into list
        vote = voters.loc[voters["voter_id"] == voter, "vote"].values[0].split(",")
        remaining = vote.copy()
        
        # Making sure the vote range is within the number of items
        range = min(vote_range[0], len(remaining)), min(vote_range[1], len(remaining))
        # randomly change size of vote
        remaining = remaining[:randint(vote_range[0], vote_range[1])]
        e_classes = []

        while remaining:
            # Randomly select a size for the equivalence class
            rank_size = min(randint(rank_range[0], rank_range[1]), len(remaining))
            # Randomly select items for the equivalence class
            e_class = sample(remaining, rank_size)
            e_classes.append(e_class)
            # remove used items
            remaining = [v for v in remaining if v not in e_class]

        # Join into weak ranking format: E1|E2|E3...
        voters.loc[voters["voter_id"] == voter, "vote"] = '|'.join([','.join(e) for e in e_classes])
    
    print("Saving generated voters...")
    # get filepath from pbfile and filename
    foldername = os.path.basename(os.path.dirname(pbfile))
    # create generated folder if it doesn't exist
    os.makedirs(f"datasets/{foldername}/generated", exist_ok=True)
    
    output_path = f"datasets/{foldername}/generated/{filename}.csv"
    
    voters.to_csv(output_path, index=False)
    


if __name__ == "__main__":
    genWeakRanks("datasets/worldwide_turk7/worldwide_mechanical-turk_ranking-value-money-7.pb", "turk7", (3, 20), (1, 3))
    
    