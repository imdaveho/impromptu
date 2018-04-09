"""A simple implementation of a multimethod dispatch decorator.

As seen here:
* https://stackoverflow.com/questions/6434482/python-function-overloading
* http://www.artima.com/weblogs/viewpost.jsp?thread=101605

If there is a need for more full featured implementation:
* https://github.com/mrocklin/multipledispatch/tree/master/multipledispatch

"""

registry = {}

class MultiMethod(object):
    def __init__(self, name):
        self.name = name
        self.typemap = {}
    def __call__(self, *args):
        types = tuple(arg.__class__ for arg in args) # a generator expression!
        function = self.typemap.get(types)
        if function is None:
            raise TypeError("no match")
        return function(*args)
    def register(self, types, function):
        if types in self.typemap:
            raise TypeError("duplicate registration")
        self.typemap[types] = function

def dispatch(*types):
    def register(function):
        name = function.__name__
        mm = registry.get(name)
        if mm is None:
            mm = registry[name] = MultiMethod(name)
        mm.register(types, function)
        return mm
    return register

@dispatch(str, list, tuple)
def configure(newv, newcm, default):
    # format: (str, colormap)
    # eg: ("?", [(3,0,0)])
    if len(newv) != len(newcm):
        return default
    return (newv, newcm)

@dispatch(str, tuple, tuple)
def configure(newv, newtrp, default):
    # format: (str, (int, int[, int]))
    # eg: ("?", (3,0,0))
    # handle tuple2 vs. tuple3
    if len(newtrp) == 3:
        newcm = [newtrp for _ in newv]
        return (newv, newcm)
    elif len(newtrp) == 2:
        fg, bg = newtrp
        newcm = [(fg, 0, bg) for _ in newv]
        return (newv, newcm)
    else:
        return default

@dispatch(str, int, int, int, tuple)
def configure(newv, fg, attr, bg, default):
    # format: (str, int, int, int)
    # eg. ("?", 3, 0, 0)
    newcm = [(fg, attr, bg) for _ in newv]
    return (newv, newcm)

@dispatch(str, int, int, tuple)
def configure(newv, fg, bg, default):
    # format: (str, int, int)
    # eg. ("?", 3, 0)
    newcm = [(fg, 0, bg) for _ in newv]
    return (newv, newcm)

@dispatch(int, int, int, tuple)
def configure(fg, attr, bg, default):
    # format: (int, int, int)
    # eg. (3, 0, 0)
    v, _ = default
    newcm = [(fg, attr, bg) for _ in v]
    return (v, newcm)

@dispatch(int, int, tuple)
def configure(fg, bg, default):
    # format: (int, int)
    # eg. (3, 0)
    v, _ = default
    newcm = [(fg, 0, bg) for _ in v]
    return (v, newcm)

@dispatch(int, tuple)
def configure(fg, default):
    # format: int
    # eg. active = 4
    if type(fg) is not int:
        return default
    return (fg, 0, 0)

@dispatch(list, tuple)
def configure(newcm, default):
    # format: colormap
    # eg. ([(0,0,0), (3,0,0), (0,0,0)])
    v, _ = default
    if len(v) != len(newcm):
        return default
    return (v, newcm)

@dispatch(str, tuple)
def configure(newv, default):
    # format: (str)
    # eg. ("<?>")
    _, cm = default
    if len(newv) != len(cm):
        return default
    return (newv, cm)

# @dispatch(dict, list)
# def configure(newch, ch):
#     # choices={...}
#     return height

@dispatch(dict, dict)
def configure(newhook, default):
    if type(newhook) is not dict:
        return default
    return newhook

@dispatch(tuple, tuple)
def configure(colors, default):
    # case of inputs / active
    # format: (int, int[, int])
    # handle tuple2 vs. tuple3
    if len(colors) == 3:
        return colors
    elif len(colors) == 2:
        fg, bg = colors
        return (fg, 0, bg)
    else:
        return default

@dispatch(int, int)
def configure(height, default):
    # case of height
    if type(height) is not int:
        return default
    return height
