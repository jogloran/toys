from itertools import count, imap

class TypeVar(object):
    newvars = imap(lambda e: '_a'+str(e), count(0))
    def __init__(self, typevarname=None):
        if not typevarname:
            typevarname = self.newvars.next()
        self.typevarname = typevarname
        
    def __repr__(self):
        return '`' + self.typevarname
    
    def apply(self, subst):
        value = subst.get(self, None)
        return value or self

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
        
    def __repr__(self):
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
        
    def apply(self, subst):
        return FunctionType(self.argtype.apply(subst), self.restype.apply(subst))
        
    def __repr__(self):
        return '(%s -> %s)' % (self.argtype, self.restype)

class Primitive(object): pass
class Integer(Primitive):
    def __init__(self, value=0):
        self.value = value
        
    @staticmethod
    def type(): return AtomicType('int')
    
    def __repr__(self): return str(self.value)
    
class List(Primitive):
    @staticmethod
    def type(): return AtomicType('list')
        
class Var(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type
        
    def __eq__(self, other):
        return self.name == other.name
    def __ne__(self, other): return not self != other
    
    def __repr__(self):
        return '%s:(%s)' % (self.name, self.type)
        
class Lambda(object):
    def __init__(self, var, body):
        self.var = var
        self.body = body
        
    def __repr__(self):
        return '\(%s . %s)' % (self.var, self.body)
        
class Apply(object):
    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg
        
    def __repr__(self):
        return '(%s %s)' % (self.fn, self.arg)
        
class TypeCheckerException(RuntimeError): pass
class HMTypeChecker(object):
    def unify(self, typeqs):
        # TODO: no detection of infinite types
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
        
    def check_type(self, term):
        return self._check_type(term, {}, {}, set())
        
    def _check_type(self, term, env, substs, typeqs):        
        if isinstance(term, Primitive):
            return term.type()
        elif isinstance(term, Lambda):
            env[term.var.name.typename] = term.var.type
            bodytype = self._check_type(term.body, env, substs, typeqs)
            return FunctionType(term.var.type.apply(substs), bodytype.apply(substs))
        elif isinstance(term, Var):
            vartype = env.get(term.name, None)
            if not vartype:
                raise TypeCheckerException('%s not bound in environment' % term.name)
                
            if term.type is None:
                term.type = vartype
                
            return vartype
        elif isinstance(term, Apply):
            # (f x) f :: T1 -> T2, x :: X
            argtype = self._check_type(term.arg, env, substs, typeqs)  # X
            funtype = self._check_type(term.fn,  env, substs, typeqs)  # T1 -> T2
            newtype = self.newtypes.next()
            
            if isinstance(funtype, AtomicType):
                raise TypeCheckerException('term of type %s not usable in funcall position' % funtype)
            
            # unify T1 -> T2 with X -> t and return t
            typeqs.add( (funtype, FunctionType(argtype, newtype)) )
            
            substs.update(self.unify(typeqs))
            return newtype.apply(substs)

        raise TypeCheckerException('failed to check type: received %s as term' % term)        
