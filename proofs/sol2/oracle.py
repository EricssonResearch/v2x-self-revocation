#!/usr/bin/env python

import sys

lines = sys.stdin.readlines()
lemma = sys.argv[1]

goals = {}

for line in lines:
  num = line.split(':')[0]

  if lemma in [
      "all_signatures_max_epoch_e_rev"
    , "no_heartbeats_processed_after_tolerance"
    , "effective_revocation"
    ]:
    # easy goals
    if "!KU( ~ltk" in line:
      goals.setdefault(0, num)
    elif "!Pseudonym" in line:
      goals.setdefault(1, num)
    elif "!Pk" in line:
      goals.setdefault(2, num)
    elif "!Ltk" in line:
      goals.setdefault(3, num)
    elif "!PRL(" in line:
      goals.setdefault(4, num)
    elif "!Parameters" in line:
      goals.setdefault(5, num)
    elif "!KU(" in line:
      goals.setdefault(6, num)

    # constraints
    elif "#vr." in line and ("#j" in line or "#k" in line):
      goals.setdefault(40, num)
    elif "'1'+" in line:
      goals.setdefault(42, num)
    elif "!Epoch( 'TC'" in line:
      goals.setdefault(43, num)

    # hard goals
    elif "!Epoch" in line:
      goals.setdefault(2000, num)
    elif "TolTmp" in line:
      goals.setdefault(10000, num)
    else:
      goals.setdefault(50, num)

  else:
    exit(0)

sorted_goals = sorted(goals.items(), key=lambda x : x[0])

for _, index in sorted_goals:
  print(index)

exit(0)