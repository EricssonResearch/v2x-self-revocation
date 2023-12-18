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
      "no_messages_accepted_after_revocation"
  ]:
    if "!KU( ~ltk" in line:
      add_goal(0, num)
    if "(#k < #vr.4))" in line:
      add_goal(1, num)
    if "tout" not in line and (
      ("('1'+t_rev+z+z.1)" in line and "('1'+'1'+t.1)" in line) or
      ("('1'++t_rev++z++z.1)" in line and "('1'++'1'++t.1)" in line) or
      ("('1'+t_rev+tv+z+z.1)" in line and "('1'+'1'+tv+t.1)" in line) or
      ("('1'++t_rev++tv++z++z.1)" in line and "('1'++'1'++tv++t.1)" in line)
    ):
      add_goal(2, num)
    elif "!Time( ('1'+t_rev+z)" in line or "!Time( ('1'++t_rev++z)" in line or \
    "!Time( ('1'+t_rev+tv+z)" in line or "!Time( ('1'++t_rev++tv++z)" in line:
      add_goal(3, num)
    elif "!KU( sign(<prl.1, t_hb>, ~ltk)" in line:
      add_goal(4, num)    
    elif "!Parameters( tv.1 )" in line:
      add_goal(5, num)  
    elif "!Timeout( tout )" in line:
      add_goal(6, num)
    else:
      add_goal(100, num)

  elif lemma in [
        "no_operations_after_timeout"
    ]:
    if "!KU( ~ltk" in line:
      add_goal(0, num)
    if "(#vr.7 < #k)" in line:
      add_goal(1, num)
    if "(#vr.6 < #k)" in line:
      add_goal(2, num)
    elif "!KU( sign(<prl, t_hb>, ~ltk)" in line:
      add_goal(3, num)
    elif "!Time( ('1'+t_rev+z)" in line or "!Time( ('1'++t_rev++z)" in line or \
        "!Time( ('1'+t_rev+tv+z)" in line or "!Time( ('1'++t_rev++tv++z)" in line:
      add_goal(4, num)
    if "(('1'+t_rev+z)" in line or "(('1'++t_rev++z)" in line or \
        "(('1'+t_rev+tv+z)" in line or "(('1'++t_rev++tv++z)" in line:
      add_goal(5, num)
    elif "!Timeout" in line:
      add_goal(6, num)
    else:
      add_goal(100, num)

  elif lemma in [
      "all_messages_accepted_signed_exists"
  ]:
    # easy goals
    if "!KU( ~ltk" in line or "!KU( ~ps_key" in line:
      add_goal(0, num)
    elif "!Parameters" in line:
      add_goal(1, num)     
    elif "!Pseudonym( pk(x)" in line:
      add_goal(2, num) 
    elif "!KU( sign" in line:
      add_goal(3, num)
    else:
      add_goal(100, num)

  elif lemma in [
      "all_messages_accepted_within_tolerance"
    , "all_heartbeats_processed_within_tolerance"
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
    "effective_revocation"
  ]:
    if "((t_v2v+tv.1) = (t_rev+z+tv.1+tv.1))" in line or \
      "((t_v2v++tv.1) = (t_rev++z++tv.1++tv.1))" in line:
      add_goal(1, num)
    else:
      add_goal(900, num)
  else:
    exit(0)

sorted_goals = sorted(goals.items(), key=lambda x : x)

for _, values in sorted_goals:
  for v in values:
    print(v)

exit(0)