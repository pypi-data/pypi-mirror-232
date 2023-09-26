def find(x, v):
  z = ""

  for p in range(len(x)):
    if x[p] != " " and x[p] != ",":
      z = z + x[p]

  x = z

  z = ""

  for p in range(len(v)):
    if v[p] != " " and v[p] != ",":
      z = z + v[p]

  v = z

  n = 0

  k = True

  g = 0

  p = True

  o = 0
  for z in range(len(x)):
    p = True
    n = 0
    while p:
      if v[n] != x[o + n] or n == len(v) - 1:
        p = False
        print(" ")
      n += 1
    if n == len(v):
        break
    o = z

  if o + 1 == len(x):
    print("List2 isn't in list1.")
  else:
    print(f"List2 is at the {o + 1} position in list1.")