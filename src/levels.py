from src.level import Level

def make_lvl_1():
    level = Level(11, 11)
    level.construct_lvl1()
    return level

def make_lvl_2():
    level = Level(10, 10)
    level.construct_lvl2()
    return level

def make_lvl_3():
    level = Level(10, 10)
    level.construct_lvl3()
    return level
