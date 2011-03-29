from collections import defaultdict

class Arc(object):
    def __init__(self, u, v, weight=0.):
        self.u = u
        self.v = v
        self.weight = weight
        
    def __repr__(self):
        return "(%s -> %s {%f})" % (self.u, self.v, self.weight)

class Graph(object):
    def __init__(self):
        self.incoming = defaultdict(set)
        self.outgoing = defaultdict(set)
        
    def add(self, u, v, weight=0.):
        a = Arc(u, v, weight)
        self.incoming[v].add(a)
        self.outgoing[u].add(a)
        
    def each_incoming(self, u):
        try:
            for arc in self.incoming[u]: yield arc
        except KeyError:
            return
    
    def each_outgoing(self, u):
        try:
            for arc in self.outgoing[u]: yield arc
        except KeyError:
            return
            
    def __repr__(self):
        return repr(self.outgoing)
