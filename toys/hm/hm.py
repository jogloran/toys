from itertools import imap, count

class FreshVars(object):
    '''Provides a source of strings of the form pref0, pref1, ...'''
    def __init__(self, prefix=''):
        self.prefix = prefix
        
    def __iter__(self):
        return imap(lambda e: self.prefix+str(e), count(0))

class TypeVar(object):
    '''Represents a type variable `a.'''
    newvars = iter(FreshVars('_a'))
    
    def __init__(self, typevarname=None):
        if not typevarname:
            typevarname = self.newvars.next()
        self.typevarname = typevarname
    
    def __repr__(self, brackets=False):
        return '`' + self.typevarname
    
    def __eq__(self, other):
        if not isinstance(other, TypeVar): return False
        return self.typevarname == other.typevarname
    def __ne__(self, other): return not self == other
    def __hash__(self):
        return hash(self.typevarname)
        
    def occurs_check(self, typevar, type):
        '''Determines if _typevar_ occurs within _type_.'''
        if isinstance(type, TypeVar):
            if type == typevar: return True
        elif isinstance(type, FunctionType):
            return (self.occurs_check(typevar, type.argtype) or
                    self.occurs_check(typevar, type.restype))
        return False
    
    def apply(self, subst):
        '''Applies a unifier _subst_ to this type variable, returning a type.'''
        # Substitute typevars repeatedly with their replacements
        value = self
        while isinstance(value, TypeVar):
            if value in subst:
                if self.occurs_check(value, subst[value]):
                    raise TypeCheckerException('occurs check failed: %s and %s' % (value, subst[value]))
                value = subst[value]
            else:
                return value
        
        return value.apply(subst)

class AtomicType(object):
    '''Represents an atomic type.'''
    def __init__(self, typename):
        self.typename = typename
    
    def __eq__(self, other):
        if not isinstance(other, AtomicType): return False
        return self.typename == other.typename
    def __ne__(self, other):
        return not self == other
    
    def apply(self, subst):
        '''Applies a unifier to this atomic type.'''
        return self # unify() only maps from TypeVars
    
    def __repr__(self, brackets=False):
        return self.typename

class FunctionType(object):
    '''Represents a function type Arg -> Res.'''
    def __init__(self, argtype, restype):
        self.argtype = argtype
        self.restype = restype
    
    def __eq__(self, other):
        if not isinstance(other, FunctionType): return False
        return self.argtype == other.argtype and self.restype == other.restype
    def __ne__(self, other):
        return not self == other
    
    def apply(self, subst):
        '''Applies a unifier to this function type.'''
        return FunctionType(self.argtype.apply(subst), self.restype.apply(subst))
    
    def __repr__(self, brackets=False):
        return '%s%s -> %s%s' % (
            '(' if brackets else '',
            self.argtype.__repr__(brackets=True), self.restype,
            ')' if brackets else '')

class Primitive(object): pass
class Integer(Primitive):
    def __init__(self, value=0):
        self.value = value
    
    @staticmethod
    def type(): return AtomicType('int')
    
    def __repr__(self): return str(self.value)
    
class Real(Primitive):
    def __init__(self, value=0.):
        self.value = value

    @staticmethod
    def type(): return AtomicType('real')

    def __repr__(self): return str(self.value)

class List(Primitive):
    @staticmethod
    def type(): return AtomicType('list')

class Var(object):
    '''Represents a reference to a previously bound variable.'''
    def __init__(self, name, type=None):
        self.name = name
        self.type = type
    
    def __eq__(self, other):
        return self.name == other.name
    def __ne__(self, other): return not self == other
    
    def __repr__(self):
        return '%s:(%s)' % (self.name, self.type)

class Lambda(object):
    '''Represents a unary lambda function.'''
    def __init__(self, var, body):
        self.var = var
        self.body = body
    
    def __repr__(self):
        return '\(%s . %s)' % (self.var, self.body)

class Apply(object):
    '''Represents a function application.'''
    def __init__(self, fn, arg):
        self.fn = fn
        self.arg = arg
    
    def __repr__(self):
        return '(%s %s)' % (self.fn, self.arg)

class TypeCheckerException(RuntimeError): pass
class HMTypeChecker(object):
    def unify(self, typeqs):
        '''Computes the most general unifier for _typeqs_, a set of type equations.'''
        unifier = {}
        while typeqs:
            lhs, rhs = typeqs.pop()
            if lhs == rhs: continue
            
            # given <`a, `b>, map `b arbitrarily to `a so that the reference
            # can be followed during substitution
            if isinstance(lhs, TypeVar) and isinstance(rhs, TypeVar):
                unifier.update({rhs: lhs})
            # given <`a, T>, map `a to T
            elif isinstance(lhs, TypeVar):
                unifier.update({lhs: rhs})
            # given <T, `b>, map `b to T
            elif isinstance(rhs, TypeVar):
                unifier.update({rhs: lhs})
            
            # given <A -> B, C -> D>, unify <A, C>, <B, D> 
            elif isinstance(lhs, FunctionType) and isinstance(rhs, FunctionType):
                typeqs.add( (lhs.argtype, rhs.argtype) )
                typeqs.add( (lhs.restype, rhs.restype) )
            # given <T1, T2>, raise an error if they aren't the same type
            elif isinstance(lhs, AtomicType) and isinstance(rhs, AtomicType):
                if lhs != rhs:
                    raise TypeCheckerException('atomic types %s and %s failed to unify' % (lhs, rhs))
            else:
                raise TypeCheckerException('failed to unify %s and %s' % (lhs, rhs))
        
        return unifier
    
    def __init__(self):
        self.newtypes = imap(lambda e: TypeVar(e), FreshVars('_t'))
    
    def check_type(self, term):
        '''Returns the type of _term_.'''
        return self._check_type(term, {}, {}, set())
    
    def _check_type(self, term, env, substs, typeqs):
        if isinstance(term, Primitive):
            return term.type()
        elif isinstance(term, Lambda):
            # TODO: need to avoid variable capture?
            env[term.var.name.typename] = term.var.type
            bodytype = self._check_type(term.body, env, substs, typeqs)
            return FunctionType(term.var.type, bodytype).apply(substs)
        elif isinstance(term, Var):
            vartype = env.get(term.name, None)
            if not vartype:
                raise TypeCheckerException('%s not bound in environment' % term.name)
            
            # term.type is None => use the type from the declaration of the variable
            if term.type is None: term.type = vartype
            
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
            # update env to reflect unification
            for var in env:
                env[var] = env[var].apply(substs)
            
            # return t with the unifier applied
            return newtype.apply(substs)
        
        raise TypeCheckerException('failed to check type: received %s as term' % term)
