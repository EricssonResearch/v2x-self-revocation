import argparse
import yaml
import sys
from os.path import join
from jproperties import Properties

env = Properties()

def dump_properties(properties, filename):
    with open(filename, "wb") as f:
        properties.store(f, encoding="utf-8")


def find_scenario(scenarios, name):
    for scenario in scenarios:
        if scenario["name"] == name:
            return scenario
    
    #print(f"Warning: scenario {name} does not exist.")


def parse_scenario(run, scenario, env):
    run_name = f"{scenario['name']}_{run['name']}.properties"

    # copy scenario env
    for var in scenario["env"]:
        env[var] = str(scenario["env"][var])
        #print(var)

    # copy run env
    for var in run["env"]:
        env[var] = str(run["env"][var])

    # dump scenario
    dump_properties(env, join(sim_dir, "scenarios", run_name))

# parse args
parser = argparse.ArgumentParser()
parser.add_argument("--env_file", help="Location of .env file")
parser.add_argument("--sim_dir", help="Directory to store simulation files")
parser.add_argument("--scenario", help="Scenario to parse (leave empty if all scenarios)", nargs='?', const=None)
parser.add_argument("--run", help="Run to parse (leave empty if all runs)", nargs='?', const=None)

args = parser.parse_args()

env_file = args.env_file
sim_dir = args.sim_dir
requested_scenario = args.scenario
requested_run = args.run

print(requested_scenario)

with open(join(sim_dir, "simulation.yaml"), "r") as f:
    conf = yaml.safe_load(f)

with open(env_file, "rb") as f:
    env.load(f)

for scenario in conf["scenarios"]:
    # copy env
    for var in scenario["env"]:
        env[var] = str(scenario["env"][var])
        #print(var)


for run in conf["runs"]:
    if requested_run is not None and requested_run != run["name"]:
        continue

    if "scenarios" not in run:
        # all scenarios
        for scenario in conf["scenarios"]:
            parse_scenario(run, scenario, env)
    else:
        for s in run["scenarios"]:
            scenario = find_scenario(conf["scenarios"], s)
            if scenario is not None and \
                (requested_scenario is None or requested_scenario == s):
                parse_scenario(run, scenario, env)