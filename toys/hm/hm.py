class TypeVar(object):
    def __init__(self, typevarname):
        self.typevarname = typevarname
        
    def __str__(self):
        return self.typevarname
    __repr__ = __str__
    
    def apply(self, subst):
        value = subst.get(self, None)
        if value: return value
        return self

class AtomicType(object):
    def __init__(self, typename):
        self.typename = typename
        
    def __eq__(self, other):
        if not isinstance(other, AtomicType): return False
        return self.typename == other.typename
    def __ne__(self, other):
        return not self == other
        
    def apply(self, subst):
        return self
        
    def __str__(self):
        return self.typename
    __repr__ = __str__
        
class FunctionType(object):
    def __init__(self, argtype, restype):
        self.argtype = argtype
        self.restype = restype
        
    def __eq__(self, other):
        if not isinstance(other, FunctionType): return False
        return self.argtype == other.argtype and self.restype == other.restype
    def __ne__(self, other):
        return not self == other
        
    def apply(self, subst):
        arg = subst.get(self.argtype, None)
        res = subst.get(self.restype, None)
        if arg: self.argtype = arg
        if res: self.argtype = res
        return self
        
    def __str__(self):
        return '(%s -> %s)' % (self.argtype, self.restype)
    __repr__ = __str__

class Primitive(object): pass
def Prim(_type):
    class _(Primitive):
        @staticmethod
        def type():
            return _type
    return _

class Integer(Primitive):
    def __init__(self, v):
        self.v = v
        
    def __str__(self):
        return self.v
        
    @staticmethod
    def type(): return AtomicType('int')
    
class List(Primitive):
    @staticmethod
    def type(): return AtomicType('list')
        
class Var(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type
    
    def __str__(self):
        return '%s:(%s)' % (self.name, self.type)
        
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
    def unify(self, typeqs):
        unifier = {}
        while typeqs:
            lhs, rhs = typeqs.pop()
            if isinstance(lhs, TypeVar):
                unifier.update({lhs: rhs})
            elif isinstance(rhs, TypeVar):
                unifier.update({rhs: lhs})
            elif isinstance(lhs, FunctionType) and isinstance(rhs, FunctionType):
                typeqs.add( (lhs.argtype, rhs.argtype) )
                typeqs.add( (lhs.restype, rhs.restype) )
            elif isinstance(lhs, AtomicType) and isinstance(rhs, AtomicType):
                if lhs != rhs:
                    raise TypeCheckerException('failed to unify %s and %s' % (lhs, rhs))
        
        return unifier
                
    def __init__(self):
        self.newtypes = imap(lambda e: TypeVar('_t'+str(e)), count(0))
        
    def check_type(self, term, env=None, substs=None, typeqs=None):
        if not env: env = {}
        if not substs: substs = {}
        if not typeqs: typeqs = set()

        if isinstance(term, Primitive):
            return term.type()
        elif isinstance(term, Lambda):
            # \x:X . t
            env[term.var.name] = term.var.type
            bodytype = self.check_type(term.body, env, substs, typeqs)
            return FunctionType(term.var.type.apply(substs), bodytype)
        elif isinstance(term, Var):
            vartype = env.get(term.name, None)
            if not vartype:
                raise TypeCheckerException('%s not free in environment' % term.name)
            return vartype
        elif isinstance(term, Apply):
            # (f x) f :: T1 -> T2, x :: X
            argtype = self.check_type(term.arg, env, substs, typeqs) # X
            funtype = self.check_type(term.fn,  env, substs, typeqs)  # T1 -> T2
            newtype = self.newtypes.next()
            
            typeqs.add( (funtype, FunctionType(argtype, newtype)) )
            
            print 'new:%s'%newtype
            substs.update(self.unify(typeqs))
            print substs
            print 'after subst:%s'%newtype.apply(substs)
            return newtype.apply(substs)

        raise TypeCheckerException('failed to check type')
        
        
if __name__ == '__main__':
    t = HMTypeChecker()
    
    # f = \x:int . 3 should be int -> int
    # g = \y:int . f should be int -> int -> int
    f=Lambda(Var('x',AtomicType('int')),Integer('3'))
    print t.check_type(f)
    g=Lambda(Var('y',AtomicType('int')),f)
    print t.check_type(g)
    y=Var('y',AtomicType('Y'))
    z=Var('z',AtomicType('Z'))
    ytoz=Var('f',FunctionType(AtomicType('Y'),AtomicType('Z')))
    # h=Lambda(y,z)
    # print t.check_type(h)
    i=Lambda(ytoz,Lambda(y,Apply(ytoz,y)))
    print i
    print t.check_type(i)
#    h=Lambda('z', )

    int=AtomicType('int')
    list=AtomicType('list')
    f=Lambda(Var('x', int), List())
    print t.check_type(f)
    g=Lambda(Var('f', t.check_type(f)), Apply(f,Integer(0)))
    print t.check_type(g)
    h=Apply(f,Integer(0))
    print t.check_type(h)
    x=Var('x',TypeVar('a'))
    i=Lambda(x,Apply(f,x))
    print t.check_type(i)
    j=Lambda(Var('x',int),Apply(f,x))
    print "f's type: %s"% t.check_type(f)
    print t.check_type(j)