from enum import IntEnum
import logging

import utils
import conf
import json

class PseudonymStatus(IntEnum):
    HONEST      = 0
    VICTIM      = 1
    MALICIOUS   = 2
    REVOKED     = 3

class Pseudonym():
    def __init__(self, ps, group, malicious):
        self.ps = ps
        self.group = group
        self.last_seen = utils.get_timestamp()
        self.last_malicious = 0
        self.status = PseudonymStatus.MALICIOUS if malicious else PseudonymStatus.HONEST
        self.is_unseen = False

    def update_last_seen(self):
        self.last_seen = utils.get_timestamp()

    def update_last_malicious(self):
        self.last_malicious = utils.get_timestamp()

    async def revoke(self):
        res, code = await utils.revoke_pseudonym(self.ps)

        if code == 200:
            self.status = PseudonymStatus.REVOKED

        return res, code

    def update_status(self):
        now = utils.get_timestamp()

        # check if the pseudonym is unseen
        if(now - self.last_seen >= conf.env("THRESHOLD_UNSEEN")):
            self.is_unseen = True
        else:
            self.is_unseen = False

        # check status
        if self.status in [PseudonymStatus.MALICIOUS, PseudonymStatus.REVOKED]:
            return True # no coming back from this

        if now - self.last_malicious >= conf.env("THRESHOLD_MALICIOUS"):
            logging.debug(f"{now - self.last_malicious} -> HONEST")
            self.status = PseudonymStatus.HONEST
        else:
            logging.debug(f"{now - self.last_malicious} -> VICTIM")
            self.status = PseudonymStatus.VICTIM

        return True

    def is_unused(self):
        now = utils.get_timestamp()
        return now - self.last_seen >= conf.env("THRESHOLD_UNUSED")

    def to_dict(self):
        return {
            #"pseudonym": self.ps,
            "group": self.group,
            "status": self.status.name,
            "last_seen": self.last_seen,
            "last_malicious": self.last_malicious,
            "is_unseen": self.is_unseen
        }

    def __repr__(self) -> str:
        return json.dumps(self.to_dict())

    def __str__(self) -> str:
        return self.__repr__()
