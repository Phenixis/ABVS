# *** modules ***
from keyboard import *
from time import sleep, time
from datetime import datetime
import sys
import traceback

# *** define functions ***
from fonctions import *

# *** define values ***
ABBREV = def_abbrev()
VALUES = def_values()
STATS_BY_ABV = def_stats()
BACKUP_INTERVAL = 5 # en minute

logs = "\n*** " + str(datetime.today())[:-7] + " ***\n"


def add_abbreviation0(source_text, replacement_text, match_suffix=False, timeout=2, sub_abv=0):
    has_circumflex = False
    for circumflex in ["^a", "^e", "^i", "^o", "^u"]:
        if circumflex in source_text:
            has_circumflex = True
    replacement = (('\b' * len(source_text)) if has_circumflex else '\b' * (len(source_text) + 1)) + replacement_text

    if sub_abv == 1:
        VALUES["nb_sub_abv"] += 1
    elif sub_abv == 0:
        VALUES["nb_abv"] += 1

    def callback():
        write(replacement)

        if source_text + '(' in replacement_text:
            VALUES["use_mot_complet"] += 1
            original_abv = replacement_text.split('(')[1][:-2]
            STATS_BY_ABV[original_abv][1] += 1
        else:
            VALUES["use_abv"] += 1
            STATS_BY_ABV[source_text][0] += 1

        VALUES["sum"] = VALUES["use_abv"] + VALUES["use_mot_complet"]
        VALUES["average_use_abv"] = int((VALUES["use_abv"] / VALUES["sum"]) * 100)
        VALUES["average_use_non_abv"] = int((VALUES["use_mot_complet"] / VALUES["sum"]) * 100)

    return add_word_listener(source_text, callback, match_suffix=match_suffix, timeout=float(timeout))


def mise_en_forme(dico: dict[str]) -> str:
    res = dico['abv'] + ' {\n'

    for key in dico:
        if key in PARAMS:
            res += '\t' + str(key) + ': \"' + str(dico[key]) + '\",\n'

    return res + '}\n'


# *** classe ***
from Abbreviation import Abbreviation