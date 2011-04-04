class AtomicType(object):
    def __init__(self, typename):
        self.typename = typename
        
    def __eq__(self, other):
        if not isinstance(other, AtomicType): return False
        return self.typename == other.typename
    def __ne__(self, other):
        return not self == other
        
    def __str__(self):
        return self.typename
        
class FunctionType(object):
    def __init__(self, argtype, restype):
        self.argtype = argtype
        self.restype = restype
        
    def __eq__(self, other):
        if not isinstance(other, FunctionType): return False
        return self.argtype == other.argtype and self.restype == other.restype
    def __ne__(self, other):
        return not self == other
        
    def __str__(self):
        return '%s -> %s' % (self.argtype, self.restype)

class Integer(object):
    def __init__(self, v):
        self.v = v
        
    def __str__(self):
        return self.v
        
class Var(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type
    
    def __str__(self):
        return '%s:%s' % (self.name, self.type)
        
class Lambda(object):
    def __init__(self, var, body):
        self.var = var
        self.body = body
        
    def __str__(self):
        return '\(%s . %s)' % (self.var, self.body)
        
class Apply(object):
    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg
        
    def __str__(self):
        return '(%s %s)' % (self.fn, self.arg)
        
from itertools import count, imap
class TypeCheckerException(RuntimeError): pass
class HMTypeChecker(object):
    def __init__(self):
        self.newtypes = imap(lambda e: '_t'+str(e), count(0))
        self.types = {}
        
    def check_type(self, term):
        print term
        if isinstance(term, Integer):
            return AtomicType('int')
        elif isinstance(term, Lambda):
            # \x:X . t
            self.types[term.var.name] = term.var.type
            return FunctionType(term.var.type, self.check_type(term.body))
        elif isinstance(term, Var):
            vartype = self.types.get(term.name, None)
            if not vartype:
                raise TypeCheckerException('%s not free in environment' % term.name)
            return vartype
        elif isinstance(term, Apply):
            # (f x) f :: T1 -> T2, x :: X
            argtype = self.check_type(term.arg) # X
            funtype = self.check_type(term.fn)  # T1 -> T2
            if not isinstance(funtype, FunctionType):
                raise TypeCheckerException('function type expected, %s received' % funtype)
            
            # T1 should match X
            if funtype.argtype != argtype:
                raise TypeCheckerException('type %s expected, %s received' % (funtype.argtype, argtype))
            return funtype.restype

        raise TypeCheckerException('failed to check type')
        
if __name__ == '__main__':
    t = HMTypeChecker()
    
    # f = \x:int . 3 should be int -> int
    # g = \y:int . f should be int -> int -> int
    f=Lambda(Var('x',AtomicType('int')),Integer('3'))
    print t.check_type(f)
    g=Lambda(Var('y',AtomicType('int')),f)
    print t.check_type(g)
    y=Var('y',AtomicType('int'))
    z=Var('z',AtomicType('int'))
    h=Lambda(y,z)
    print t.check_type(h)
#    h=Lambda('z', )