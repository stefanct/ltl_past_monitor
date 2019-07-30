from template import solve

TRACE = [
  {"p": 1, "q": 1, "r": 1, "s": 1},
  {"p": 1, "q": 0, "r": 0, "s": 0},
  {"p": 1, "q": 0, "r": 1, "s": 0},
]

SUBS_CNT = 9

if __name__ == '__main__':

  ret = solve(TRACE, SUBS_CNT)
  if (ret == 1):
    print("Fail")
  else:
    print("Pass")
  exit(ret)

