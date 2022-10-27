import random

class CredentialManager():
    def __init__(self):
        self.__ltp = None
        self.__pseudonyms = []

    def get_ltp(self):
        return self.__ltp

    def get_pseudonyms(self):
        return self.__pseudonyms

    def get_random_pseudonym(self):
        if not self.__pseudonyms:
            return None
    
        return random.choice(self.__pseudonyms)

    def set_ltp(self, ltp):
        self.__ltp = ltp

    def add_pseudonym(self, ps):
        if ps not in self.__pseudonyms:
            self.__pseudonyms.append(ps)

    def remove_pseudonym(self, ps):
        self.__pseudonyms.remove(ps)

    def clear(self):
        self.__ltp = None
        self.__pseudonyms.clear()