import logging

import freshness

class Pseudonym():
    def __init__(self, id):
        self.id = id
        self.expiration = freshness.get_freshness_parameter() + \
                          freshness.get_prl_duration_time()

class PRL():
    def __init__(self, key):
        self.prl = []
        self.revoked = [] # not needed in practice, just to avoid revoking twice
        self.key = key
        self.__heartbeat = None

    def add_pseudonym(self, id):
        if id in self.revoked:
            logging.debug(f"{id} already in PRL")
            return False

        pseudonym = Pseudonym(id)
        self.prl.append(pseudonym)
        self.revoked.append(id)
        return True

    def remove_old_pseudonyms(self):
        now = freshness.get_freshness_parameter()
        self.prl = list(filter(lambda x : now <= x.expiration, self.prl))

    def get_heartbeat(self):
        if self.__heartbeat is None:
            self.generate_heartbeat()

        return self.__heartbeat

    def generate_heartbeat(self):
        now = freshness.get_freshness_parameter()
        #logging.debug(f"Generating new heartbeat : {now}")

        prl = list(map(lambda x : x.id, self.prl))

        hb = {
            "iss" : "RA",
            "prl" : prl,
            "iat" : now
        }

        self.__heartbeat = self.key.sign_jwt(hb)
        #logging.debug(f"New HB: {self.__heartbeat}")
        #logging.debug(f"Verified: {self.key.verify_jwt(self.__heartbeat)}")
