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

import sys
import copy
from itertools import chain, islice, izip
from collections import defaultdict

class ddict(defaultdict):
    def __repr__(self):
        s = '{'
        for k, v in self.iteritems():
            s += '%s: %s ' % (k,v)
        s += '}'
        return s
defaultdict = ddict

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
        self.incoming = defaultdict(set)
        self.states = {}
        
    def incoming_states_to(self, target):
        for state in self.incoming[target]:
            yield state
        
    def get_state(self, state_label):
        if state_label not in self.states:
            self.add_state(state_label)
        return self.states[state_label]
    def remove_state(self, state_label):
        del self.states[state_label]
        
    def add_state(self, state_label, output=BOT):
        self.states[state_label] = State(state_label, output)
        
    def add_transition(self, source, input, output, target):
        self.T[source][input] = [output, target]
        
        self.incoming[target].add(source)
        
    def edge_output_string(self, source, input):
        return self.T[source][input][0]
    def set_edge_output_string(self, source, input, output):
        self.T[source][input][0] = output
        
    def edge_target_state(self, source, input):
        return self.T[source][input][1]
    def set_edge_target_state(self, source, input, target):    
        self.T[source][input][1] = target
        
        self.incoming[target].add(source)
        
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
    '''
>>> lcp(['123', '1234', '12'])
'12'
>>> lcp(['', '12345', '12'])
''
>>> lcp(['456', '234', '123'])
''
>>> lcp([])
''
>>> lcp(['123'])
'123'
>>> lcp(['123', '123', '123'])
'123'
>>> lcp(['123', '12', BOT])
'12'
>>> lcp([BOT, BOT])
BOT
    '''
    if (all( f == BOT for f in files )):
        return BOT
        
    # treat BOT as nothing
    files = [ f for f in files if f != BOT ]
    
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
        # print 'f_a',f_a
        # print 'setting edge output string %s from %s on %s'%(T.edge_output_string(state, input) + f_a, state, input)
        T.set_edge_output_string(state, input,
                                 T.edge_output_string(state, input) + f_a)
        # print 'T here:',T
        
    # index 1 is the output string
    outgoing_edges_outputs = [ e[1] for e in T.outgoing_edges_from(state) ]
    if outgoing_edges_outputs:
        f = lcp( [ state.output, lcp(outgoing_edges_outputs) ] )
    else:
        f = state.output
    len_f = len(f)
    
    print 'state %s, lcp: %s' % (state, f)
    
    if len_f > 0:
        for (input, output, outgoing_state) in T.outgoing_edges_from(state):
            T.set_edge_output_string(state, input,
                                     T.edge_output_string(state, input)[len_f:])

        if state.output == BOT: 
            state.output = BOT
        else:
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
    
    state1_successor = T.edge_target_state(state1, input)
    state2_successor = T.edge_target_state(state2, input)
    
    for (input, output, outgoing_state) in T.outgoing_edges_from(state1_successor):
        T.set_edge_output_string(state1_successor, input,
                                 u1 + T.edge_output_string(state1_successor, input))
    for (input, output, outgoing_state) in T.outgoing_edges_from(state2_successor):
        T.set_edge_output_string(state2_successor, input,
                                 u2 + T.edge_output_string(state2_successor, input))
    
    state1_successor.output = u1 + state1_successor.output
    state2_successor.output = u2 + state2_successor.output
    
def merge(orig_T, red_states, red_state, blue_state):
    # for any state incoming to blue_state:
    #     point it to red_state instead
    # fold(T, red_state, blue_state)
    T = copy.deepcopy(orig_T)
    for incoming_state in T.incoming_states_to(blue_state):
        for (input, output, outgoing_state) in T.outgoing_edges_from(incoming_state):
            T.set_edge_target_state(input, output, red_state)
    
    return fold(T, red_states, red_state, blue_state)
    
def fold(T, red_states, q, q_):
    w = outputs_are_equal(q.output, q_.output)
    print 'w: %s' % w
    if w is None:
        return None
    else:
        q.output = w

        for a in common_input_strings_out_of_states(T, q, q_):        
            if T.edge_target_state(q_, a) is not None:
                if T.edge_target_state(q, a) is not None:
                    # if q on input a takes you to a red state, fail
                    if T.edge_target_state(q, a) in red_states:
                        return None
                    else:
                        pushback(T, q, q_, a)
                        fold(T, red_states, T.edge_target_state(q, a), T.edge_target_state(q_, a))
                else:
                    T.set_edge_target_state(q, a,
                                            T.edge_target_state(q_, a))

        # T.remove_state(q_.label)
                
        return T
        # for any input string A on an edge coming out of both q and q_,
        #     if output strings are not equal, fail
        #     else,
        #         pushback(T, q, q_, A)
        #         fold(T, destination state of q on A, destination state of q_ on A)
        #    TODO: need to handle 'else: t(q,a)<-t(q',a)' line
        
def common_input_strings_out_of_states(T, state1, state2):
    state1_inputs = set()
    state2_inputs = set()
    
    for (input, _, _) in T.outgoing_edges_from(state1):
        state1_inputs.add(input)
    for (input, _, _) in T.outgoing_edges_from(state2):
        state2_inputs.add(input)
        
    # intersection
    return state1_inputs & state2_inputs
        
def ostia(data):
    T = build_ptt(data)
    print 'after build_ptt:\n',T
    make_onward(T, T.get_state(''))
    print 'after make_onward:\n',T
    
    red_states = { T.get_state('') }
    blue_states = { T.get_state(input) for (input, output) in data }

    while blue_states:
        q = blue_states.pop()
        print 'blue state: %s' % q
        
        for p in red_states:
            print 'trying to merge %s and %s' % (p,q)
            merged_T = merge(T, red_states, p, q)
            if merged_T is not None:
                # accept merged as the new T
                print 'accepting merged_T %s' % merged_T
                T = merged_T
                break
            else:
                print 'failed to merge'
        else:
            red_states.add(q)
            
        # update blue_states to contain
        # any state which a red state points to, but is not red
        for red_state in red_states:
            for (input, output, outgoing_state) in T.outgoing_edges_from(red_state):
                if outgoing_state not in red_states:
                    blue_states.add(outgoing_state)
                    
    return T

if __name__ == '__main__':
#    T = ostia([ ('abc', '101'), ('aec', '121'), ('fg', '345'), ('fh', '320') ])

    if '-t' in sys.argv[1:]:
        import doctest
        doctest.testmod()
        
    else:
        #data = [ ('a', '1'), ('b', '1'), ('aa', '01'), ('aaa', '001'), ('abab', '0101') ]
        # T = ostia(data)
        # print T
        
        T = Transducer()
        q1, q2, q3, q4, q5, q6 = State('q1', '0'), State('q2', '1'), \
            State('q3', '0'), State('q4', LAMBDA), \
            State('q5', LAMBDA), State('q6', '1')
        T.add_transition(q1, 'a', '1', q3)
        T.add_transition(q3, 'b', '1', q5)
        T.add_transition(q2, 'a', '10', q4)
        T.add_transition(q4, 'c', '1', q6)
        print T
        pushback(T, q1, q2, 'a')
        print T
        