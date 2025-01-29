from random import randint,sample
from main import parse_pb_file


def generatePB(pbfile, filename, vote_range, rank_range):
    metadata, projects, voters = parse_pb_file(pbfile)

    for voter in voters["voter_id"].values:
        vote = voters[voters["voter_id"] == voter]["vote"].values[0].split(",")
        vote_size = min(randint(vote_range[0], vote_range[1]), len(vote))
        
        vote = vote[0:vote_size]
        i = 0
        e_classes = []
        while i < len(vote):
            rank_size = min(randint(rank_range[0], rank_range[1]), len(vote) - i)
            e_class = vote[i:i + rank_size]
            e_classes.append(e_class)
            i += rank_size
        # make voter vote to e_class
        voters.loc[voters["voter_id"] == voter, "vote"] = '|'.join([','.join(e_class) for e_class in e_classes])

    voters.to_csv(f"datasets/generated/{filename}.csv", index=False)

def genRandPB(pbfile, filename, vote_range, rank_range):
    metadata, projects, voters = parse_pb_file(pbfile)

    for voter in voters["voter_id"].values:
        vote_size = min(randint(vote_range[0], vote_range[1]), len(vote))
        vote = sample(projects["project_id"].values, vote_size)
        
        i = 0
        e_classes = []
        while i < len(vote):
            rank_size = min(randint(rank_range[0], rank_range[1]), len(vote) - i)
            e_class = vote[i:i + rank_size]
            e_classes.append(e_class)
            i += rank_size
        # make voter vote to e_class
        voters.loc[voters["voter_id"] == voter, "vote"] = '|'.join([','.join(e_class) for e_class in e_classes])

    voters.to_csv(f"datasets/generated/{filename}.csv", index=False)

if __name__ == "__main__":
    generatePB("datasets/pb_data", "gen2", (2, 8), (1, 3))
    genRandPB("datasets/pb_data", "gen3", (2, 8), (1, 3))
    

