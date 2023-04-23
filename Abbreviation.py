from constants import *


class Abbreviation:

    def __init__(self, abv: str, fr: str, suffix: int = 0, has_sub_abv_maj: int = 0, has_sub_abv_plur: int = 0,
                 is_sub_abv: int = 0):
        self.abv = abv
        self.mot_complet = fr + " " if fr[-1] != " " else fr
        self.is_suffix = suffix
        self.is_sub_abv = is_sub_abv
        self.dico = {PARAMS[i]: [self.abv,
                                 self.mot_complet,
                                 self.is_suffix,
                                 has_sub_abv_maj,
                                 has_sub_abv_plur,
                                 self.is_sub_abv][i] for i in range(len(PARAMS[:-2]))}
        self.started = False

    def __repr__(self):
        nom = self.abv if self.abv != "" else self.mot_complet.capitalize()
        res = nom + "\n" + f"\tFrançais: {self.mot_complet}"
        return res + "\n "

    def def_fr(self, value: str):
        self.update(PARAMS[1], value)
        self.mot_complet = value

    def def_abbrev(self, value: str):
        self.update(PARAMS[0], value)
        self.abv = value

    def def_suffix(self, value: int):
        self.update(PARAMS[2], value)
        self.is_suffix = True if value else False

    def start_abv(self):
        raise_an_error()
        if not self.started:
            self.started = True
            add_abbreviation0(self.abv, self.mot_complet, self.is_suffix, sub_abv=self.is_sub_abv)
            add_abbreviation0(self.mot_complet[:-1], self.mot_complet[:-1] + '(' + self.abv + ')' + ' ', self.is_suffix, sub_abv=2)

    def end_abv(self):
        if self.started:
            self.started = False
            remove_abbreviation(self.abv)
            remove_abbreviation(self.mot_complet[:-1])


    def update(self, column, value):
        ABBREV[self.abv][column] = value
