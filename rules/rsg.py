from rules.rule import Rule

class RSG(Rule):
    def __init__(self, k, share):
        self.k = k
        self.share = share
    
    def apply(self, pb):
        best_s = []
        best_size = -float('inf')

        for s in pb.f:
            cnt = len([i for i in pb.N if self.t(i, s, pb) <= self.k])
            if cnt > best_size:
                best_size = cnt
                best_s = [s]
            elif cnt == best_size:
                best_s.append(s)
        return best_s

    def t(self, voter, s, pb):
        if pb.cS(s) < self.share:
            return pb.m+1
        
        for j in range(1, pb.m+1):
            inter = (p for p in s if pb.rank(voter, p) <= j)
            if pb.cS(inter) >= self.share:
                return j
        