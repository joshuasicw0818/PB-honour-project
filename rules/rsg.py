from rules.rule import Rule

class RSG(Rule):
    def __init__(self, k, share):
        self.k = k
        self.share = share
    
    def apply(self, pb):
        pass

    def t(self, voter, s, pb):
        if pb.cS(s) < self.share:
            return pb.m+1
        pass