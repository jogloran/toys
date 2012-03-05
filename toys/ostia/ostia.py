# coding: utf-8
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

def debug(s, *args):
    print >>sys.stderr, s % args

import sys
import copy
from itertools import chain, islice, izip
from collections import defaultdict

class ddict(defaultdict):
    def __repr__(self):
        s = '{ '
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
        
    def __hash__(self):
        return hash(self.label)
        
    def __eq__(self, other):
        return self.label == other.label
        
    def __deepcopy__(self, memo):
        return self#State(self.label, self.output)
        
LAMBDA = ''
class Transducer(object):
    def as_graph(self):
        states = '\n'.join(r'"s%(state)s" [label="%(state)s:%(output)s"]' % {
            'state': state.label,
            'output': state.output
        } for state in self.states.values())

        edges = '\n'.join(r's%(src)s -> s%(dst)s [label="%(edge)s"]' % {
            'src': state.label,
            'dst': target.label,
            'edge': '%s:%s' % (input, output)
        } for state in self.states.values()
          for (input, output, target) in self.outgoing_edges_from(state))
        
        return '''
digraph G {
    %(states)s
%(edges)s
}
''' % locals()

    # { state: { input: [output, state] } }
    def __init__(self):
        self.T = defaultdict(lambda: defaultdict(lambda: [None, None]))
        self.incoming = defaultdict(set)
        self.states = {}
        
    def incoming_states_to(self, target):
        for (state, input) in self.incoming[target]:
            yield (state, input)
        
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
        
        self.incoming[target].add( (source, input) )
        
    def edge_output_string(self, source, input):
        return self.T[source][input][0]
    def set_edge_output_string(self, source, input, output):
        self.T[source][input][0] = output
        
    def edge_target_state(self, source, input):
        return self.T[source][input][1]
    def set_edge_target_state(self, source, input, target):    
        self.T[source][input][1] = target
        
        self.incoming[target].add( (source, input) )
        
    def outgoing_states_from(self, source):
        for (input, (output, target)) in self.T[source].items():
            yield target
            
    def outgoing_edges_from(self, source):
        for (input, (output, target)) in self.T[source].items():
            yield (input, output, target)
            
    def all_states(self):
        for state in self.states:
            yield state
            
    def __repr__(self):
        return '<Transducer %s>' % self.T
            
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
'''    
    if len(files) == 0:
        return ''
        
    if (all( f == BOT for f in files )):
        return BOT

    # treat BOT as nothing
    files = [ f for f in files if f != BOT ]
        
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
        debug('f_a: %s', f_a)
        # print 'setting edge output string %s from %s on %s'%(T.edge_output_string(state, input) + f_a, state, input)
        T.set_edge_output_string(state, input,
                                 T.edge_output_string(state, input) + f_a)
        # print 'T here:',T
    # if state.label=='':
    #     import pdb;pdb.set_trace()
        
    # index 1 is the output string
    outgoing_edges_outputs = [ e[1] for e in T.outgoing_edges_from(state) ]
    if outgoing_edges_outputs:
        f = lcp( [ state.output, lcp(outgoing_edges_outputs) ] )
    else:
        f = state.output
    len_f = len(f)
    
    if len_f > 0 and not state.label == '':
        for (input, output, outgoing_state) in T.outgoing_edges_from(state):
            T.set_edge_output_string(state, input,
                                     T.edge_output_string(state, input)[len_f:])
        
        if state.output is not BOT:
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

    if state1_successor.output is not BOT:
        state1_successor.output = u1 + state1_successor.output
    if state2_successor.output is not BOT:
        state2_successor.output = u2 + state2_successor.output
    
def merge(orig_T, red_states, red_state, blue_state):
    # for any state incoming to blue_state:
    #     point it to red_state instead
    # fold(T, red_state, blue_state)
    T = orig_T#copy.deepcopy(orig_T)
    
    # red_state = T.get_state(red_state.label)
    # blue_state = T.get_state(blue_state.label)
    
    reassignments = {}
    # for every state that used to point to blue_state,
    for incoming_state, input in T.incoming_states_to(blue_state):
        # point it to red_state instead
        
        previous_target_state = T.edge_target_state(incoming_state, input)
        debug('setting destination of %s on %s from %s to %s',
            incoming_state, input, previous_target_state, red_state)
        reassignments[ (incoming_state, input) ] = previous_target_state
        T.set_edge_target_state(incoming_state, input, red_state)

    result = fold(T, red_states, red_state, blue_state)

    if result is None:
        # roll back
        for (incoming_state, input), old_target_state in reassignments.items():
            debug('rolling back destination of %s on %s from %s to %s',
                incoming_state, input, T.edge_target_state(incoming_state, input), old_target_state)
            T.set_edge_target_state(incoming_state, input, old_target_state)
            
    return result
    
def fold(T, red_states, q, q_):
    w = outputs_are_equal(q.output, q_.output)
    if w is None:
        return None
    else:
        old_q_output = q.output
        q.output = w

        for (input_, output_, outgoing_state_) in T.outgoing_edges_from(q_):
            found_matching = False
            for (input, output, outgoing_state) in T.outgoing_edges_from(q):
                if input == input_:
                    if T.edge_target_state(q, input) in red_states:
                    # if T.edge_output_string(q, input) != T.edge_output_string(q_, input):
                        # import pdb;pdb.set_trace()
                        debug('%s is a red state, failing', T.edge_target_state(q, input))
                        q.output = old_q_output
                        return None
                    else:
                        pushback(T, q, q_, input)
                        fold(T, red_states, T.edge_target_state(q, input), T.edge_target_state(q_, input))
                        found_matching = True
            
            if not found_matching:
                T.add_transition(q, input_,
                                 T.edge_output_string(q_, input_),
                                 T.edge_target_state(q_, input_))                
        return T
        
def ostia(data):
    T = build_ptt(data)
    make_onward(T, T.get_state(''))
    
    red_states = { T.get_state('') }
    blue_states = [ T.get_state(input) for (input, output) in data if len(input) == 1 ]

    while blue_states:
        debug('blue states: %s',blue_states)
        debug('red states: %s',red_states)
        
        q = blue_states.pop(0)
        debug('POP blue state: %s', q)
        
        for p in red_states:
            debug('TRYING MERGE %s and %s',p,q)
            merged_T = merge(T, red_states, p, q)
            if merged_T is not None:
                # accept merged as the new T
                debug('SUCCEEDED MERGE %s and %s merged_T %s', p, q, merged_T)
                T = merged_T
                break
            else:
                debug('FAILED MERGE %s and %s',p,q)
        else:
            debug('exhausted all merges between %s and red states', q)
            red_states.add(q)
            
        # update blue_states to contain
        # any state which a red state points to, but is not red
        for red_state in red_states:
            # print 'considering red state %s' % red_state
            
            for (input, output, outgoing_state) in T.outgoing_edges_from(red_state):
                # if outgoing_state is None: continue
                if outgoing_state not in red_states:
                    if outgoing_state not in blue_states: # to get set behaviour
                        blue_states.append(outgoing_state)
                    
    return T

if __name__ == '__main__':
#    T = ostia([ ('abc', '101'), ('aec', '121'), ('fg', '345'), ('fh', '320') ])

    if '-t' in sys.argv[1:]:
        import doctest
        doctest.testmod()
        
    else:
        data = [ ('a', '1'), ('b', '1'), ('aa', '01'), ('ab', '01'), ('aaa', '001'), ('abab', '0101') ]
        # data = [ ('abc', 'abc'), ('def', 'def'), ('def', 'deg')]
        T = ostia(data)
        print T.as_graph()
        
        # T = build_ptt(data)
        # print 'ptt',T
        # make_onward(T, T.get_state(''))
        # print T
        # T = build_ptt(data)
        # make_onward(T, T.get_state(''))
        # print T
        # red_states = [T.get_state('')]
        # print
        # _ = merge(T, red_states, T.get_state(''), T.get_state('a'))
        # print 'new:', _
        # T = merge(T, red_states, T.get_state(''), T.get_state('b'))
        # print 'new:', T
        # T = merge(T, red_states, T.get_state('a'), T.get_state('aa'))
        # print 'new:', T
        # sys.exit(1)
        
        # fold tests
        # T = Transducer()
        #         q_ = State('q_', '0')
        #         qa = State('qa', '1')
        #         qb = State('qb', '0')
        #         qaa = State('qaa', '0')
        #         qaaa = State('qaaa', LAMBDA)
        #         qaab = State('qaab', BOT)
        #         qaabb = State('qaabb', LAMBDA)
        #         T.add_transition(q_, 'b', '1', qb)
        #         T.add_transition(qb, 'a', '1', q_)
        #         T.add_transition(q_, 'a', '1', qa)
        #         T.add_transition(qa, 'a', '1', q_)
        #         T.add_transition(qa, 'b', LAMBDA, qb)
        #         
        #         T.add_transition(qaab, 'b', LAMBDA, qaabb)
        #         T.add_transition(qaa, 'b', '11', qaab)
        #         T.add_transition(qaa, 'a', '11', qaaa)
        #         fold(T, [q_], q_, qaa) # expecting figure 18.10
        #         fold(T, [q_, qaa], q_, qaaa)
        #         print T
        
        # make_onward tests with BOT
        # T = Transducer()
        # q_ = State('q_', '1')
        # qa = State('qa', BOT)
        # qaa = State('qaa', '1')
        # qab = State('qab', LAMBDA)
        # T.add_transition(q_, 'a', '0', qa)
        # T.add_transition(qa, 'a', '00', qaa)
        # T.add_transition(qa, 'b', LAMBDA, qab)
        # T.add_transition(qaa, 'a', LAMBDA, qab)
        # make_onward(T, q_)
        
        # pushback tests
        # T = Transducer()
        # q1, q2, q3, q4, q5, q6 = State('q1', '0'), State('q2', '1'), \
        #     State('q3', '0'), State('q4', LAMBDA), \
        #     State('q5', LAMBDA), State('q6', '1')
        # T.add_transition(q1, 'a', '1', q3)
        # T.add_transition(q3, 'b', '1', q5)
        # T.add_transition(q2, 'a', '10', q4)
        # T.add_transition(q4, 'c', '1', q6)
        # print T
        # pushback(T, q1, q2, 'a')
        # print T
        