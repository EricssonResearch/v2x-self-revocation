#!/usr/bin/env python

import sys

lines = sys.stdin.readlines()
lemma = sys.argv[1]

goals = {}

for line in lines:
  num = line.split(':')[0]

  if lemma in [
      "all_signatures_max_time_t_rev"
    , "no_heartbeats_processed_after_tolerance"
    , "effective_revocation"
    , "processing_hb_possible"
    , "revocation_possible"
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
    elif "!Time" not in line and "('1'+t+tv)" in line:
      goals.setdefault(41, num)
    elif "('1'+t)" in line:
      goals.setdefault(42, num)
    elif "'1'+" in line:
      goals.setdefault(43, num)
    elif "!Time( 'TC'" in line:
      goals.setdefault(50, num)

    # hard goals
    elif "!Time" in line:
      goals.setdefault(2000, num)
    elif "TvTmp" in line:
      goals.setdefault(10000, num)
    else:
      goals.setdefault(50, num)

  else:
    exit(0)

sorted_goals = sorted(goals.items(), key=lambda x : x[0])

for _, index in sorted_goals:
  print(index)

exit(0)