import re

SIGN_REGEX = "SIGN ([a-zA-Z0-9]+) ([01])"
VERIFY_REGEX = "VERIFY ([a-zA-Z0-9 ]+)"

def parse_sign(msg):
    match = re.findall(SIGN_REGEX, msg)[0]
    ps = match[0]
    malicious = True if match[1] == "1" else False
    return ps, malicious

def parse_verify(msg):
    match = re.findall(VERIFY_REGEX, msg)[0]
    return match.split(" ")