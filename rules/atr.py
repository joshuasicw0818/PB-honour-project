from rules.rule import Rule

class ATR(Rule):
    def __init__(self, f):
        self.f = f

    def apply(self, pb):
        appr_votes = {}
        for voter in pb.N:
            appr_votes[voter] = []
            j = 1
            while pb.cS(appr_votes[voter]) + pb.cS(pb.pp[voter][j-1]) <= pb.L:
                appr_votes[voter].extend(pb.pp[voter][j-1])
                j += 1
            over = []
            for p in pb.pp[voter][j-1]:
                if pb.c(p) < pb.L - pb.cS(appr_votes[voter]):
                    over.append(p)
            appr_votes[voter].extend(over)
        
        return self.maximize(appr_votes, pb)

    def maximize(self, appr_votes, pb):
        #Find the feasible subset of projects that maximizes the utility function
        best_s = []
        best_u = -float('inf')

        for s in pb.f:
            total_u = 0

            for i in pb.N:
                inter = set(appr_votes[i]).intersection(s)
                if self.f == "|.|":
                    total_u += len(inter)
                elif self.f == "c":
                    total_u += pb.cS(inter)
                elif self.f == "1":
                    total_u += 1 if len(inter) > 0 else 0

            if total_u > best_u:
                best_u = total_u
                best_s = [s]
            elif total_u == best_u:
                best_s.append(s)

        return best_s
