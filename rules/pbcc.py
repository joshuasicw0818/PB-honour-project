import numpy as np

from pb_instance import PB
from rules.rule import Rule

class PBCC(Rule):
    def apply(self, pb):
        best_s = []
        best_u = -float('inf')

        for s in pb.f:
            util = 0
            for i in pb.N:
                r = min([pb.rank(i, p) for p in s], default=float('inf'))
                util += pb.m - r

            if util > best_u:
                best_u = util
                best_s = [s]
            elif util == best_u:
                best_s.append(s)
        return best_s