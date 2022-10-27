#!/usr/bin/env python

import sys

lines = sys.stdin.readlines()
lemma = sys.argv[1]

goals = {}

for line in lines:
  num = line.split(':')[0]

  if lemma in [
      "all_signatures_before_timeout"
    , "no_messages_accepted_with_timestamp_t_sign"
    , "no_operations_after_timeout"
    , "all_messages_accepted_signed_exists"
  ]:
    # easy goals
    if "!KU( ~ltk" in line:
      goals.setdefault(0, num)
    elif "!KU( ~ps_key" in line:
      goals.setdefault(1, num)
    elif "!Pseudonym" in line:
      goals.setdefault(2, num)
    elif "!Pk" in line:
      goals.setdefault(3, num)
    elif "!Ltk" in line:
      goals.setdefault(4, num)
    elif "!PRL(" in line:
      goals.setdefault(5, num)
    elif "!Parameters" in line:
      goals.setdefault(6, num)
    elif "!KU( sign" in line:
      goals.setdefault(7, num)

    # constraints
    elif "!Time" in line and not "!Timeout" in line and "'1'" in line:
      goals.setdefault(39, num)     
    elif line.count("#vr.") >= 4:
      goals.setdefault(40, num)
    elif "#vr." in line and ("#j" in line or "#k" in line):
      goals.setdefault(41, num)
    elif "!Time" not in line and "Tmp" not in line:
      goals.setdefault(99 - line.count("'1'"), num)

    # hard goals
    elif "!KU(" in line:
      goals.setdefault(900, num)
    elif "!Timeout" in line:
      goals.setdefault(1000, num)
    elif "!Time" in line:
      goals.setdefault(2000, num)
    elif "TrTmp" in line:
      goals.setdefault(10000, num)
    elif "TvTmp" in line:
      goals.setdefault(20000, num)
    else:
      goals.setdefault(100, num)

  elif lemma in [
      "all_messages_accepted_within_tolerance"
    , "all_heartbeats_processed_within_tolerance"
  ]:
    # easy goals
    if "!Pseudonym" in line:
      goals.setdefault(2, num)
    elif "!Ltk" in line:
      goals.setdefault(4, num)
    elif "!Parameters" in line:
      goals.setdefault(6, num)

    # hard goals
    elif "!KU(" in line:
      goals.setdefault(900, num)
    elif "!Pk" in line:
      goals.setdefault(901, num)
    elif "!PRL(" in line:
      goals.setdefault(902, num)
    elif "!Timeout" in line:
      goals.setdefault(1000, num)
    elif "!Time" in line:
      goals.setdefault(2000, num)
    elif "TrTmp" in line:
      goals.setdefault(10000, num)
    elif "TvTmp" in line:
      goals.setdefault(20000, num)
    else:
      goals.setdefault(100, num)

  elif lemma in [
    "effective_revocation"
  ]:
    if "t_rev+tr.1+tv.1+tv.1" in line:
      goals.setdefault(1, num)
    else:
      goals.setdefault(900, num)
  else:
    exit(0)

sorted_goals = sorted(goals.items(), key=lambda x : x[0])

for _, index in sorted_goals:
  print(index)

exit(0)