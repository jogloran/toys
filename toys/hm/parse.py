# grammar:
# term ::= ( term term ) | LAMBDA vardef . term | value | varname
# vardef ::= varname : type
# type ::= atomictype | type -> type | typevar
# typevar ::= BACKTICK typename
# atomictype ::= typename
# varname ::= ('a'..'Z')+
# typename ::= ('a'..'Z')+

import sys
def warn(msg, *args):
    print >>sys.stderr, "warning: %s" % (msg % args)
    
def err(msg, *args):
    print >>sys.stderr, "error: %s" % (msg % args)
    
try:
    import ply.lex as lex
    import ply.yacc as yacc
except ImportError:
    import lex, yacc
    
from hm import *
    
def p_term(stk):
    '''
    term : LPA term term RPA
         | LAMBDA vardef DOT term
         | value
         | var
    '''
    if len(stk) == 5:
        if stk[1] == '(':
            stk[0] = Apply(stk[2], stk[3])
        elif stk[1] == '\\':
            stk[0] = Lambda(stk[2], stk[4])
    elif len(stk) == 2:
        stk[0] = stk[1]
        

def p_var(stk):
    '''
    var : NAME
    '''
    stk[0] = Var(stk[1])
    
def p_int(stk):
    '''
    int : INT
    '''
    stk[0] = Integer(int(stk[1]))
    
def p_value(stk):
    '''
    value : int
    '''
    stk[0] = stk[1]
    
def p_typeatom(stk):
    '''
    typeatom : NAME
    '''
    stk[0] = AtomicType(stk[1])
    
def p_typevar(stk):
    '''
    typevar : BACKTICK NAME
    '''
    stk[0] = TypeVar(stk[2])
    
def p_varname(stk):
    '''
    varname : typeatom 
            | typevar
    '''
    stk[0] = stk[1]
    
def p_type(stk):
    '''
    type : varname
         | type ARROW type
         | LPA type ARROW type RPA
    '''
    if len(stk) == 6:
        stk[0] = FunctionType(stk[2], stk[4])
    if len(stk) == 4:
        stk[0] = FunctionType(stk[1], stk[3])
    elif len(stk) == 2:
        stk[0] = stk[1]
    
from itertools import imap, count
freshvars = imap(lambda e: TypeVar('_v'+str(e)), count(0))
def p_vardef(stk):
    '''
    vardef : varname COLON type
           | varname
    '''
    if len(stk) == 4:
        stk[0] = Var(stk[1], stk[3])
    elif len(stk) == 2:
        global freshvars
        stk[0] = Var(stk[1], freshvars.next())

tokens = ('INT', 'LAMBDA', 'LPA', 'RPA', 'DOT', 'COLON', 'ARROW', 'BACKTICK', 'NAME')

def t_NAME(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    return t

def t_INT(t):
    r'\d+'
    return t

def t_LAMBDA(t):
    r'\\'
    return t

def t_LPA(t):
    r'\('
    return t

def t_RPA(t):
    r'\)'
    return t
    
def t_DOT(t):
    r'\.'
    return t
    
def t_COLON(t):
    r':'
    return t
    
def t_ARROW(t):
    r'->'
    return t
    
def t_BACKTICK(t):
    r"[`']"
    return t
    
t_ignore = ' \t\r\v\f\n'

def t_error(t):
    warn("Illegal character `%s' encountered.", t.value[0])
    t.lexer.skip(1)
    
def p_error(stk):
    err("Syntax error encountered: %s", stk)
    
def parse(s):
    lex.lex()
    yacc.yacc()
    
    query = yacc.parse(s)
    return query
    
import sys
if __name__ == '__main__':
    term = parse(sys.argv[1])
    t = HMTypeChecker()
    try:
        print t.check_type(term)
    except TypeCheckerException, e:
        err(e.message)