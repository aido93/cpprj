from class_gen import class_, consts, virtuals
from functions import method, funcs, statics
from enums import enum, switch

e1=enum('my_enum', 'q w e r=10 t y ')
e2=enum('my_enum2', 'a s d f=15 g h', upper=True)
e3=enum('my_enum3', 'z x c v b', upper=True, is_class=False)
e4=enum('my_enum4', '   o p u k l ', upper=False, is_class=False)

c1=class_('my_class', )
