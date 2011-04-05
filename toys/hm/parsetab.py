
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = '\xc8\xdc\x8ex\xc4\x7fw\xddQ\x94%S\xb2\x9e\x9a\xe3'
    
_lr_action_items = {'NAME':([0,1,3,4,5,6,7,8,9,15,17,18,20,23,24,25,28,],[3,-3,-5,-7,-6,3,-4,12,3,19,12,3,-1,12,-2,12,12,]),'INT':([0,1,3,4,5,6,7,9,18,20,24,],[5,-3,-5,-7,-6,5,-4,5,5,-1,-2,]),'BACKTICK':([8,17,23,25,28,],[15,15,15,15,15,]),'RPA':([1,3,4,5,7,10,11,12,16,19,20,21,24,27,29,30,],[-3,-5,-7,-6,-4,-10,-11,-8,20,-9,-1,-12,-2,-13,30,-14,]),'COLON':([10,11,12,13,19,],[-10,-11,-8,17,-9,]),'DOT':([10,11,12,14,19,21,22,27,30,],[-10,-11,-8,18,-9,-12,-15,-13,-14,]),'ARROW':([10,11,12,19,21,22,26,27,29,30,],[-10,-11,-8,-9,-12,25,28,25,25,-14,]),'LAMBDA':([0,1,3,4,5,6,7,9,18,20,24,],[8,-3,-5,-7,-6,8,-4,8,8,-1,-2,]),'LPA':([0,1,3,4,5,6,7,9,17,18,20,23,24,25,28,],[6,-3,-5,-7,-6,6,-4,6,23,6,-1,23,-2,23,23,]),'$end':([1,2,3,4,5,7,20,24,],[-3,0,-5,-7,-6,-4,-1,-2,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'term':([0,6,9,18,],[2,9,16,24,]),'typeatom':([8,17,23,25,28,],[10,10,10,10,10,]),'typevar':([8,17,23,25,28,],[11,11,11,11,11,]),'int':([0,6,9,18,],[4,4,4,4,]),'varname':([8,17,23,25,28,],[13,21,21,21,21,]),'value':([0,6,9,18,],[1,1,1,1,]),'vardef':([8,],[14,]),'var':([0,6,9,18,],[7,7,7,7,]),'type':([17,23,25,28,],[22,26,27,29,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> term","S'",1,None,None,None),
  ('term -> LPA term term RPA','term',4,'p_term','parse.py',27),
  ('term -> LAMBDA vardef DOT term','term',4,'p_term','parse.py',28),
  ('term -> value','term',1,'p_term','parse.py',29),
  ('term -> var','term',1,'p_term','parse.py',30),
  ('var -> NAME','var',1,'p_var','parse.py',43),
  ('int -> INT','int',1,'p_int','parse.py',49),
  ('value -> int','value',1,'p_value','parse.py',55),
  ('typeatom -> NAME','typeatom',1,'p_typeatom','parse.py',61),
  ('typevar -> BACKTICK NAME','typevar',2,'p_typevar','parse.py',67),
  ('varname -> typeatom','varname',1,'p_varname','parse.py',73),
  ('varname -> typevar','varname',1,'p_varname','parse.py',74),
  ('type -> varname','type',1,'p_type','parse.py',80),
  ('type -> type ARROW type','type',3,'p_type','parse.py',81),
  ('type -> LPA type ARROW type RPA','type',5,'p_type','parse.py',82),
  ('vardef -> varname COLON type','vardef',3,'p_vardef','parse.py',93),
]
