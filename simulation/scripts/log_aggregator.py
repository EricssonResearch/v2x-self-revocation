import sys
import os
from os.path import join
import re
import math
import json
from datetime import datetime
from jproperties import Properties

folder = sys.argv[1]
out = sys.argv[2]
sim_time = int(sys.argv[3])
down_time = int(sys.argv[4])
env_file = sys.argv[5]

RA_FILE = "ra.*\.log"
VEHICLE_FILE = "vehicle.*\-tc.log"
ATTACKER_FILE = "attacker.*\-tc.log"

start_regex = 'time="([0-9TZ\-:]+)" level=info msg="RA START"'
stop_regex = 'time="([0-9TZ\-:]+)" level=info msg="RA STOP"'
revoke_regex = 'time="([0-9TZ\-:]+)" level=info msg="REVOKE ([a-zA-Z0-9]+)"'
join_regex = 'time="([0-9TZ\-:]+)" level=info msg="JOIN ([a-zA-Z0-9]+)"'
create_regex = 'time="([0-9TZ\-:]+)" level=info msg="CREATE ([a-zA-Z0-9]+)"'
sign_regex = 'time="([0-9TZ\-:]+)" level=info msg="SIGN ([a-zA-Z0-9]+)"'
verify_regex = 'time="([0-9TZ\-:]+)" level=info msg="VERIFY ([a-zA-Z0-9]+)"'

files = os.listdir(folder)

ra_file = [f for f in files if re.match(RA_FILE, f)][0]
honest_files = [f for f in files if re.match(VEHICLE_FILE, f)]
malicious_files = [f for f in files if re.match(ATTACKER_FILE, f)]

revoked = {}
num_honest_vehicles = 0
num_malicious_vehicles = 0
num_honest_pseudonyms = 0
num_malicious_pseudonyms = 0

def time_to_timestamp(t_str):
    d = datetime.strptime(t_str, "%Y-%m-%dT%H:%M:%SZ")
    return int(math.floor(d.timestamp()))

def update_timings(log_line, metrics, distr_id=None):
    ts = time_to_timestamp(log_line[0][0])
    ps = log_line[0][1]

    if ps not in revoked:
        return

    if revoked[ps][metrics] < ts:
        revoked[ps][metrics] = ts

    if distr_id is not None and revoked[ps]["distribution"][distr_id] < ts:
        revoked[ps]["distribution"][distr_id] = ts


# read RA file and extract info about revoked pseudonyms
print("Getting info on revoked pseudonyms")
with open(join(folder, ra_file), "r") as f:
    fl = f.readlines()

# get start and stop times
start_info = re.findall(start_regex, "\n".join(fl))
if len(start_info) != 1:
    raise Exception("Cannot retrieve start time")

start_ts = time_to_timestamp(start_info[0])

stop_info = re.findall(stop_regex, "\n".join(fl))
if len(stop_info) != 1:
    raise Exception("Cannot retrieve stop time")

stop_ts = time_to_timestamp(stop_info[0])

# get revoked pseudonyms
for line in fl:
    revoke_info = re.findall(revoke_regex, line)

    if len(revoke_info) != 1:
        continue

    ts = time_to_timestamp(revoke_info[0][0])
    ps = revoke_info[0][1]

    if ts >= stop_ts - down_time:
        break

    #print(f"ts: {ts} ps: {ps}")
    rev_data = {
        "created": 0,
        "revoked": ts,
        "last_sign": 0,
        "last_verify": 0,
        "distribution": [0] * len(honest_files)
    }

    revoked[ps] = rev_data

# read files of honest vehicles and get data
for i in range(len(honest_files)):
    tc_file = honest_files[i]

    print(f"Reading {tc_file}")
    with open(join(folder, tc_file), "r") as f:
        fl = f.readlines()

    for line in fl:
        join_info = re.findall(join_regex, line)
        create_info = re.findall(create_regex, line)
        sign_info = re.findall(sign_regex, line)
        verify_info = re.findall(verify_regex, line)

        if len(join_info) == 1:
            num_honest_vehicles += 1
        elif len(create_info) == 1:
            num_honest_pseudonyms += 1
            update_timings(create_info, "created")
        elif len(sign_info) == 1:
            update_timings(sign_info, "last_sign")
        elif len(verify_info) == 1:
            update_timings(verify_info, "last_verify", distr_id=i)

# read files of malicious vehicles and get data
for tc_file in malicious_files:
    print(f"Reading {tc_file}")
    with open(join(folder, tc_file), "r") as f:
        fl = f.readlines()

    for line in fl:
        join_info = re.findall(join_regex, line)
        create_info = re.findall(create_regex, line)
        sign_info = re.findall(sign_regex, line)
        verify_info = re.findall(verify_regex, line)

        if len(join_info) == 1:
            num_malicious_vehicles += 1
        elif len(create_info) == 1:
            num_malicious_pseudonyms += 1
            update_timings(create_info, "created")
        elif len(sign_info) == 1:
            update_timings(sign_info, "last_sign")

print("Filtering out pseudonyms with missing data")
revoked_filtered = {k: v for k, v in revoked.items() if v["last_sign"] != 0 and v["last_verify"] != 0}

missing = len(revoked) - len(revoked_filtered)

if missing >= 10:
    raise Exception(f"{missing} pseudonyms missing")
else:
    print(f"Warning: {missing} pseudonyms missing")

print("Filtering out zero values in distributions")
for ps in revoked:
    revoked[ps]["distribution"] = [x for x in revoked[ps]["distribution"] if x > 0]
    
print(f"Writing results to {out}")
stats = {
    "sim_time": sim_time,
    "down_time": down_time,
    "ra_start_time": start_ts,
    "ra_end_time": stop_ts,
    "ra_time": stop_ts - start_ts,
    "tc_files_analyzed": len(honest_files) + len(malicious_files),
    "honest_vehicles": num_honest_vehicles,
    "malicious_vehicles": num_malicious_vehicles,
    "total_vehicles": num_honest_vehicles + num_malicious_vehicles,
    "honest_pseudonyms": num_honest_pseudonyms,
    "malicious_pseudonyms": num_malicious_pseudonyms,
    "revoked_pseudonyms": len(revoked),
    "total_pseudonyms": num_honest_pseudonyms + num_malicious_pseudonyms
}

env = {}
env_vars = Properties()
with open(env_file, "rb") as f:
    env_vars.load(f)
   
for item in env_vars.items():
    env[item[0]] = item[1].data

file_dump = {
    "stats": stats,
    "env": env,
    "pseudonyms": revoked
}
with open(out, "w") as f:
    json.dump(file_dump, f, indent=4)

print(f"Done.")
for k in stats:
    print(f"{k}: {stats[k]}")