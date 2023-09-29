import numpy as np

### Parameters used to compute the average number of revocations ###
AVG_PRL_SIZE = 5 # average PRL size for Scenario 2 - 20% attackers -- computed from Markov analysis
T_PRL = 30 # time in PRL considered
PSEUDONYMS = 800 # number of pseudonyms considered

def print_scenario(scenario, attackers):
    assert len(scenario) == len(attackers)

    for i in range(len(scenario)):
        print(f"{int(attackers[i] * 100)}% attackers: {scenario[i]:.15f} ")

# Vehicle classes: used to compute probabilities for Scenario 1 and 2
vehicle_classes = {
    "honest_1": {
        "p": 0.01, # 1% probability to get revoked within the specified duration
        "duration": 86400 # a week
    },
    "honest_2": {
        "p": 0.99, # 99% probability to get revoked within the specified duration
        "duration": 86400 # a week
    },
    "malicious": {
        "p": 0.75, # 75% probability to get revoked within the specified duration
        "duration": 1800 # 30 min
    },
}

# Shares of attackers in the network: from 0% to 20%
attackers = np.array([0.0, 0.01, 0.02, 0.05, 0.1, 0.2])

print(f"Vehicle classes considered: {vehicle_classes}")
print(f"Shares of attackers considered: {attackers}")

print("Computing per-second revocation probabilities for each vehicle class and share of attackers..")
probabilities = {}
for vc in vehicle_classes:
    # computing the per-second probability via geometric series (See Appendix D-D)
    p =  1 - (1 - vehicle_classes[vc]["p"]) ** (1 / vehicle_classes[vc]["duration"])

    probabilities[vc] = {
        "per-second p": p,
        "attackers": []
    }
    for attacker in attackers:
        if "honest" in vc:
            attacker_p = (1 - attacker) * p
        else:
            attacker_p = attacker * p

        probabilities[vc]["attackers"].append(attacker_p)


print("Computing total (honest + malicious) probabilities for each scenario..")

# h1 <-> Scenario 1: 
# honest vehicles get revoked at least once a day with 1% probability
# malicious vehicles get revoked every 30 minutes with 75% probabiity
h1 = np.add(probabilities["honest_1"]["attackers"], probabilities["malicious"]["attackers"])
print(f"Probabilities Scenario 1")
print_scenario(h1, attackers)

# h2 <-> Scenario 2: 
# honest vehicles get revoked at least once a day with 99% probability
# malicious vehicles get revoked every 30 minutes with 75% probabiity
h2 = np.add(probabilities["honest_2"]["attackers"], probabilities["malicious"]["attackers"])
print(f"Probabilities Scenario 2")
print_scenario(h2, attackers)

print(f"Computing expected number of revocations over a day for n={PSEUDONYMS} and T_prl={T_PRL}..")

# From the paper: E_rev = n * s * p * (1 - p_prl)
p_prl = AVG_PRL_SIZE / PSEUDONYMS
rev_h1 = PSEUDONYMS * 86400 * h1 * (1 - p_prl)
rev_h2 = PSEUDONYMS * 86400 * h2 * (1 - p_prl)

print(f"Expected revocations over a day Scenario 1")
print_scenario(rev_h1, attackers)

print(f"Expected revocations over a day Scenario 2")
print_scenario(rev_h2, attackers)

print("All done!")