trace_t = [
  {"p": 1, "q": 1, "r": 1, "s": 1},
  {"p": 1, "q": 0, "r": 0, "s": 0},
  {"p": 1, "q": 0, "r": 1, "s": 0},
]

SUBS_CNT = 9
pre = [None]*SUBS_CNT
now = [None]*SUBS_CNT

# /* Initialization of state and pre */
state = trace_t.pop(0)
print("p=%s, q=%s, r=%s, s=%s" % (state["p"], state["q"], state["r"], state["s"]))

pre[8] = state["s"]
pre[7] = state["r"]
pre[6] = pre[7] or pre[8]
pre[5] = not pre[6] and pre[6]
pre[4] = state["q"]
pre[3] = (pre[3] or pre[4]) and not pre[5]
pre[2] = state["p"]
pre[1] = pre[2] and not pre[2]
pre[0] = not pre[1] or pre[3];


# /* Event interpretation loop */
while trace_t:
  state = trace_t.pop(0)
  print("p=%s, q=%s, r=%s, s=%s" % (state["p"], state["q"], state["r"], state["s"]))

  now[8] = state["s"]
  now[7] = state["r"]
  now[6] = now[7] or now[8]
  now[5] = not now[6] and pre[6]
  now[4] = state["q"]
  now[3] = (pre[3] or now[4]) and not now[5]
  now[2] = state["p"]
  now[1] = now[2] and not pre[2]
  now[0] = not now[1] or now[3];

  if now[0] == 0:
    print("Fail")
    exit(1)

  pre = now

print("Pass")
exit(0)

