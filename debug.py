_vprint = lambda *a, **k: None # do-nothing function
_vvprint = lambda *a, **k: None # do-nothing function

def vprint(*args, **kwargs):
  _vprint(*args, **kwargs)

def vprintn(*args, **kwargs):
  _vprint(*args, end="", **kwargs)

def vvprint(*args, **kwargs):
  _vvprint(*args, **kwargs)

def vvprintn(*args, **kwargs):
  _vvprint(*args, end="", **kwargs)

def set_verbosity(verbose):
  global _vprint, _vvprint
  if verbose > 0:
    _vprint = lambda *args, **kwargs: print(*args, **kwargs)
    if verbose > 1:
      _vvprint = lambda *args, **kwargs: print(*args, **kwargs)
