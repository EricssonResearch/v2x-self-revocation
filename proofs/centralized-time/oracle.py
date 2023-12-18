#!/usr/bin/env python3

import sys

lines = sys.stdin.readlines()
lemma = sys.argv[1]

goals = {}

def add_goal(ranking, goal):
  if ranking not in goals:
    goals[ranking] = []

  goals[ranking].append(goal)

for line in lines:
  num = line.split(':')[0]

  if lemma in [
      "all_signatures_max_time_t_rev"
    ]:
    # easy goals
    if "!KU( ~ltk" in line:
      add_goal(0, num)
    elif "!Pk" in line:
      add_goal(2, num)
    elif "!Ltk" in line and not "ps" in line:
      add_goal(3, num)
    elif "!Parameters" in line:
      add_goal(6, num)

    # constraints
    elif "(#vr." in line and not "ps_key" in line:
      add_goal(40, num)
    elif "!KU(" in line:
      add_goal(50, num)
    elif "!Time( 'TC'" in line:
      add_goal(100, num)

    # hard goals
    elif "!Time" in line:
      add_goal(2000, num)
    elif "!Pseudonym(" in line:
      add_goal(2500, num)
    elif "!PRL(" in line:
      add_goal(3000, num)
    elif "TvTmp" in line:
      add_goal(10000, num)
    else:
      add_goal(1000, num)

  elif lemma in [
      "effective_revocation"
    ]:
    # easy goals
    if "!KU( ~ltk" in line or "!KU( ~ps_key" in line:
      add_goal(0, num)
    elif "!Pseudonym(" in line and ("pk(~ps_key)" in line or "pk(~ltk)" in line):
      add_goal(1, num)
    elif "!Pk" in line:
      add_goal(2, num)
    elif "!Ltk" in line and not "ps" in line:
      add_goal(3, num)
    elif "!Parameters" in line:
      add_goal(6, num)
    elif "!KU( sign(<prl.1, t_v2v>, ~ltk)" in line:
      add_goal(7, num)

    # constraints
    elif "!Time( 'RA'" in line and "'1'+" in line:
      add_goal(20, num)
    elif "!Pseudonym( pk(x)" in line:
      add_goal(30, num)
    elif "!KU( sign" in line:
      add_goal(40, num)
    elif "(#vr." in line and not "ps_key" in line:
      add_goal(50, num)
    elif "!KU(" in line and not "sign" in line:
      add_goal(60, num)
    elif "'1'+'1'" in line or "'1'++'1'" in line:
      add_goal(70, num)

    # hard goals
    elif "!Time( 'TC'" in line:
      add_goal(1500, num)
    elif "!Time" in line:
      add_goal(2000, num)
    elif "!Pseudonym(" in line:
      add_goal(2500, num)
    elif "!PRL(" in line:
      add_goal(3000, num)
    elif "TvTmp" in line:
      add_goal(10000, num)
    else:
      add_goal(999, num)

  elif lemma in [
      "all_heartbeats_processed_within_tolerance"
  ]:
    # easy goals
    if "!KU( ~ltk" in line or "!KU( ~ps_key" in line:
      add_goal(0, num)
    elif "!Pseudonym(" in line and ("pk(~ps_key)" in line or "pk(~ltk)" in line):
      add_goal(1, num)
    elif "!Ltk" in line:
      add_goal(4, num)
    elif "!Parameters" in line:
      add_goal(6, num)

    # hard goals
    elif "!KU(" in line:
      add_goal(900, num)
    elif "!Pk" in line:
      add_goal(901, num)
    if "!Pseudonym" in line:
      add_goal(902, num)
    elif "!PRL(" in line:
      add_goal(903, num)
    elif "!Timeout" in line:
      add_goal(1000, num)
    elif "!Time" in line:
      add_goal(2000, num)
    elif "TvTmp" in line:
      add_goal(20000, num)
    else:
      add_goal(100, num)

  elif lemma in [
      "no_heartbeats_processed_after_tolerance"
    ]:
    # easy goals
    if "!KU( ~ltk" in line:
      add_goal(0, num)
    elif "!Pk" in line:
      add_goal(1, num)
    elif "!Parameters" in line:
      add_goal(2, num)
    elif "Time( 'TC', t )" in line:
      add_goal(3, num)
    elif "!KU( sign(<prl.2, t>, ~ltk)" in line:
      add_goal(4, num)
    elif "#vr < #k" in line and ("cnt+z" in line or "cnt++z" in line):
      add_goal(5, num)
    elif "#k < #vr.3" in line and ("'1'+cnt" in line or "'1'++cnt" in line):
      add_goal(6, num)
    elif "t_rev" in line and (
      "('1'+'1'+t)" in line or "('1'++'1'++t)" in line or
      "('1'+'1'+t+tv)" in line or "('1'++'1'++t++tv)" in line
      ):
      add_goal(7, num)

  elif lemma in [
      "processing_hb_possible"
    , "revocation_possible"
    ]:
    # easy goals
    if "!KU( ~ltk" in line:
      add_goal(0, num)
    elif "!Pseudonym(" in line:
      add_goal(1, num)
    elif "!Pk" in line:
      add_goal(2, num)
    elif "!Ltk" in line:
      add_goal(3, num)
    elif "!Parameters" in line:
      add_goal(6, num)
    elif "!Time( 'TC'" in line:
      add_goal(7, num)
    elif "!KU(" in line:
      add_goal(8, num)

    # constraints
    elif "#vr." in line and ("#j" in line or "#k" in line):
      add_goal(40, num)
    elif "!Time" not in line and ("('1'+t+tv)" in line or "('1'++t++tv)" in line):
      add_goal(41, num)
    elif "('1'+t)" in line or "('1'++t)" in line:
      add_goal(42, num)
    elif "'1'+" in line or "'1'++" in line:
      add_goal(43, num)
    elif "!Time( 'TC'" in line:
      add_goal(100, num)

    # hard goals
    elif "!PRL(" in line:
      add_goal(1000, num)
    elif "!Time" in line:
      add_goal(2000, num)
    elif "TvTmp" in line:
      add_goal(10000, num)
    else:
      add_goal(50, num)
  
  else:
    exit(0)

sorted_goals = sorted(goals.items(), key=lambda x : x)

for _, values in sorted_goals:
  for v in values:
    print(v)

exit(0)