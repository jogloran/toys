'''
>>> t = Transducer()
>>> P = State(label='P', output='400')
>>> Q = State(label='Q', output='512')
>>> R = State(label='R', output='516')
>>> t.add_transition(source=P, input="abc", output="123", target=Q)
>>> Q in t.outgoing_states_from(P)
True
>>> t.add_transition(source=P, input="fgh", output="512", target=R)
>>> R in t.outgoing_states_from(P)
True
>>> P in t.outgoing_states_from(Q)
False
'''

from itertools import chain, islice, izip
from collections import defaultdict

BOT = None
class State(object):
    def __init__(self, label, output=BOT):
        self.label = label
        self.output = output
        
    def __repr__(self):
        return '<St %s:%s>' % (self.label, self.output)
        
LAMBDA = ''
class Transducer(object):
    # { state: { input: [output, state] } }
    def __init__(self):
        self.T = defaultdict(lambda: defaultdict(lambda: [None, None]))
        self.states = {}
        
    def get_state(self, state_label):
        if state_label not in self.states:
            self.add_state(state_label)
        return self.states[state_label]
        
    def add_state(self, state_label, output=LAMBDA):
        self.states[state_label] = State(state_label, output)
        
    def add_transition(self, source, input, output, target):
        self.T[source][input] = [output, target]
        
    def edge_output_string(self, source, input):
        return self.T[source][input][0]
    def set_edge_output_string(self, source, input, output):
        self.T[source][input][0] = output
        
    def edge_target_state(self, source, input):
        return self.T[source][input][1]
    def set_edge_target_state(self, source, input, target):
        self.T[source][input][1] = target
        
    def outgoing_states_from(self, source):
        for (input, (output, target)) in self.T[source].iteritems():
            yield target
            
    def outgoing_edges_from(self, source):
        for (input, (output, target)) in self.T[source].iteritems():
            yield (input, output, target)
            
    def all_states(self):
        for state in self.states:
            yield state
            
    def __repr__(self):
        return '<Transducer states=%s transitions=%s>' % (self.states.values(), self.T)
            
def flatten(lol):
    '''
>>> list(flatten([ [1,2,3], [4,5] ]))
[1, 2, 3, 4, 5]
>>> list(flatten([[]]))
[]
>>> list(flatten([]))
[]
>>> list(flatten([1,2,3]))
Traceback (most recent call last):
    ...
TypeError: 'int' object is not iterable
    '''
    return chain.from_iterable(lol)
    
def descending_prefixes_of(s):
    '''
>>> list(descending_prefixes_of('abcde'))
['abcde', 'abcd', 'abc', 'ab', 'a', '']
    '''
    return [ s[:i] for i in xrange(len(s),-1,-1) ]
    
def each_pair(l):
    '''
>>> list(each_pair([1,2,3,4,5]))
[(1, 2), (2, 3), (3, 4), (4, 5)]
    '''
    return izip(islice(l, 0, len(l)-1),
                islice(l, 1, None))

def build_ptt(data_pairs):
    transducer = Transducer()
    
    for (input, output) in data_pairs:
        for (target_state_label, source_state_label) in each_pair(descending_prefixes_of(input)):
            source_state = transducer.get_state(source_state_label) #??
            target_state = transducer.get_state(target_state_label)
            
            transducer.add_transition(source_state, target_state_label[-1], LAMBDA, target_state)
            
        target_state = transducer.get_state(input)
        target_state.output = output
        
    return transducer
    
def lcp(files):
    # treat LAMBDA as nothing
    files = [ f for f in files if f ]
    
    if len(files) == 0:
        return ''
        
    if len(files) == 1:
        return files[0]

    files = [pair[1] for pair in sorted((len(fi), fi) for fi in files)]

    for i, comparison_ch in enumerate(files[0]):
        for fi in files[1:]:
            ch = fi[i]

            if ch != comparison_ch:
                return fi[:i]

    return files[0]
    
def make_onward(T, state):
    for (input, output, outgoing_state) in T.outgoing_edges_from(state):
        f_a = make_onward(T, outgoing_state)
        T.set_edge_output_string(state, input,
                                 T.edge_output_string(state, input) + f_a)
        
    # index 1 is the output string
    f = lcp( [ lcp( [ e[1] for e in T.outgoing_edges_from(state) ] ),
             state.output ] )
    len_f = len(f)
    
    if len_f > 0:
        for (input, output, outgoing_state) in T.outgoing_edges_from(state):
            T.set_edge_output_string(state, input,
                                     T.edge_output_string(state, input)[len_f:])
        state.output = state.output[len_f:]
        
    return f
    
def outputs_are_equal(w1, w2):
    if w1 == BOT: return w2
    elif w2 == BOT: return w1
    elif w1 == w2: return w1
    else: return None

def pushback(T, state1, state2, input):
    u = lcp([ T.edge_output_string(state1, input), T.edge_output_string(state2, input) ])
    len_u = len(u)
    
    u1 = T.edge_output_string(state1, input)[len_u:]
    u2 = T.edge_output_string(state2, input)[len_u:]
    
    T.set_edge_output_string(state1, input, u)
    T.set_edge_output_string(state2, input, u)
    
    for (input, output, outgoing_state) in T.outgoing_edges_from(state1):
        T.set_edge_output_string(state1, input,
                                 u1 + T.edge_output_string(state1, input))
        T.set_edge_output_string(state2, input,
                                 u2 + T.edge_output_string(state2, input))
    
    state1.output = u1 + state1.output
    state2.output = u2 + state2.output
    
def merge(T, red_state, blue_state):
    # for any state incoming to blue_state:
    #     point it to red_state instead
    # fold(T, red_state, blue_state)
    
def fold(T, q, q_):
    w = outputs_are_equal(q.output, q_.output)
    if w is None:
        raise
    else:
        q.output = w
        # for any input string A on an edge coming out of both q and q_,
        #     if output strings are not equal, fail
        #     else,
        #         pushback(T, q, q_, A)
        #         fold(T, destination state of q on A, destination state of q_ on A)
        #    TODO: need to handle 'else: t(q,a)<-t(q',a)' line

if __name__ == '__main__':
    T = build_ptt([ ('abc', '101'), ('aec', '121'), ('fg', '345'), ('fh', '320') ])
    make_onward(T, T.get_state(''))
    print T
    import doctest
    doctest.testmod()