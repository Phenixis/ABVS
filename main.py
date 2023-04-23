import sys
import traceback

from constants import *

abbreviations = {}
backup_moments = [round(time()) + BACKUP_INTERVAL * 60]


def verify_backup():
    actual_time = round(time())
    # print(actual_time, backup_moments[-1])
    if actual_time >= backup_moments[-1]:
        save_everything('sql&txt')
        backup_moments.append(actual_time + (BACKUP_INTERVAL * 60))


def suppr_text(length: int) -> None:
    write('\b' * length)


def log(message: str) -> None:
    global logs
    actual_date = str(datetime.today())
    actual_log = f"{actual_date[:-4]}: {message}"
    print(actual_log)
    logs += actual_log + '\n'


def save_logs():
    open("Data/log.txt", "a", encoding="utf-8").write(logs)


def abbreviation() -> None:
    """
    Démarre toutes les abréviations
    """
    for abv in ABBREV.keys():
        abbreviations[abv] = Abbreviation(ABBREV[abv][PARAMS[0]],
                                          ABBREV[abv][PARAMS[1]],
                                          ABBREV[abv][PARAMS[2]],
                                          ABBREV[abv][PARAMS[3]],
                                          ABBREV[abv][PARAMS[4]],
                                          ABBREV[abv][PARAMS[5]])
        abbreviations[abv].start_abv()

    log("ABVS est démarré")


def save_abbrevs(mode: str) -> None:
    if 'txt' in mode:
        res = ""

        for abv in sorted(ABBREV):
            res += mise_en_forme(ABBREV[abv])

        open('Backup/abbreviations.txt', 'w', encoding='utf-8').write(res)

    if 'sql' in mode:
        values_to_add = []
        for abv in sorted(ABBREV):
            if not abv_in_db(abv):
                values_to_add.append(list(ABBREV[abv].values()) + [0, 0])
            else:
                columns_changed = has_changed("Abbreviations", PARAMS[:-2], abv, list(ABBREV[abv].values()))
                values_to_set = [(columns_changed[i], ABBREV[abv][columns_changed[i]]) for i in
                                 range(len(columns_changed))]
                if columns_changed:
                    update_val("Abbreviations", values_to_set, [PARAMS[0], abv])

        add_multiple_values_to_bdd("Abbreviations", values_to_add)

        bdd = select_all_values("Abbreviations")

        for abv in bdd:
            if abv[0] not in ABBREV.keys():
                del_value("Abbreviations", ("abv", abv[0]))

    log("Abbreviations saved")


def save_values(mode: str = None) -> None:
    txt = ""
    for key in VALUES.keys():
        text_to_write = f"{key}:{VALUES[key]}"
        if key == "nb_sub_abv":
            text_to_write += "\n*** Usage stats: "
        elif "average" in key:
            text_to_write += "%"
        txt += text_to_write + '\n'

    if mode:
        open("Backup/values.txt", 'w', encoding="utf-8").write(txt)
    open("Data/values.txt", 'w', encoding="utf-8").write(txt)

    log("Values saved")


def save_stats(mode: str) -> None:
    if 'txt' in mode:
        txt_to_add = ""
        for abv in sorted(STATS_BY_ABV):
            txt_to_add += abv + ':' + str(STATS_BY_ABV[abv]) + '\n'
        open("Backup/stats.txt", "w", encoding="utf-8").write(txt_to_add)
    elif 'sql' in mode:
        for abv in sorted(STATS_BY_ABV):
            # print(abv, STATS_BY_ABV[abv])
            update_val("Abbreviations", [(PARAMS[6], STATS_BY_ABV[abv][0]), (PARAMS[7], STATS_BY_ABV[abv][1])],
                       [PARAMS[0], abv])

    log("Statistics saved")


def save_everything(mode: str) -> None:
    """
    Enregistre toutes les données sauf les logs
    """
    save_abbrevs(mode)
    save_values('backup' if 'txt' in mode else None)
    save_stats(mode)

    db.commit()


def stop_abbrev() -> None:
    """
    Enregistre les abréviations et les arrête toutes
    """
    save_everything('sql&txt')
    save_logs()
    for key in abbreviations.keys():
        abbreviations[key].end_abv()


def list_event_to_string(recorded: list[KeyboardEvent]) -> str:
    """
    Prend une liste d'événements keyboard et renvoie un string de ces événements
    """
    result = ""

    for i in range(len(recorded)):
        if recorded[i].name == "backspace" and len(result) >= 1:
            result = result[:-1]
        elif recorded[i].name == 'space':
            result += ' '
        elif recorded[i].name == 'enter':
            result += '\n'
        elif i <= len(recorded) - 1 and recorded[i].name == "^" and recorded[i + 1].scan_code in [16, 18, 23, 24, 22]:
            if recorded[i + 1].scan_code == 16:
                result += 'â'
            elif recorded[i + 1].scan_code == 18:
                result += 'ê'
            elif recorded[i + 1].scan_code == 23:
                result += 'î'
            elif recorded[i + 1].scan_code == 24:
                result += 'ô'
            elif recorded[i + 1].scan_code == 22:
                result += 'û'

        elif recorded[i].name not in ["ctrl", "ctrl droite", "maj", "esc", "right shift", "alt", "tab", "verr maj"]:
            result += recorded[i].name

    for letter in ["âa", "êe", "îi", "ôo", "ûu"]:
        while letter in result:
            result = remove_not_circumflex(result)

    return result


def remove_not_circumflex(text: str) -> str:
    """
    Prend en entrée un string et renvoie ce string sans la lettre suivant une voyelle avec accent circomflexe
    """
    for i in range(len(text)):
        if text[i] in 'âêîôû':
            return text[:i + 1] + text[i + 2:]


def remove_key_up(list_events: list[KeyboardEvent]) -> list[KeyboardEvent]:
    """
    Prend en entrée une liste d'événement keyboard et ne renvoie que les événements d'appuis sur touches
    """
    res = list_events[:]
    for event in list_events:
        if event.event_type == KEY_UP:
            res.remove(event)
    return res


def record_all(mode: str) -> str | list[str]:
    """
    Enregistre les touches entrées et renvoie
    """
    txt_to_write = ["\nLe mode entré n'est pas connu."]
    if mode == 'add' or mode == 'modif':
        txt_to_write = ["\nAbréviation : ",
                        "\nMot complet : ",
                        "\nEst-ce un suffixe : ",
                        "\nFaut-il une sous-abréviation avec une majuscule : ",
                        "\nFaut-il une sous-abréviation au pluriel : "]
    elif mode == 'suppr':
        txt_to_write = ["\nEntrez l'abréviation à supprimer puis appuyez sur [esc] : "]
    elif mode == 'rechercher':
        txt_to_write = ["\nEntrez l'abréviation à rechercher puis appuyez sur [esc] : "]
    else:
        confirm(txt_to_write[0])
        return ""

    all_values = []
    for txt in txt_to_write:
        write(txt)

        recorded = remove_key_up(record("esc"))
        all_values.append(list_event_to_string(recorded))

    suppr_text(len(''.join(txt_to_write)) + len(''.join(all_values)))

    res = ""
    if mode == 'add' or mode == 'modif':
        res = all_values  #.split(', ')
    elif mode == 'suppr' or mode == 'rechercher':
        res = all_values[0]

    # print(f"'{res}'")
    return res


def suppr_abbrev(abv_to_end: str) -> None:
    """
    Supprime l'abréviation de la bdd
    """
    abbreviations[abv_to_end].end_abv()
    del ABBREV[abv_to_end]
    del abbreviations[abv_to_end]
    del STATS_BY_ABV[abv_to_end]
    log(f"L'abréviation {abv_to_end} a été supprimée de la BDD. ")


def list_to_dico(lst: list[str]) -> dict[str]:
    res = {}
    for i in range(len(PARAMS) - 2):
        if i > 1:
            res[PARAMS[i]] = 1 if is_positive(lst[i]) else 0
        else:
            res[PARAMS[i]] = remove_final_space(lst[i])
    return res


def modif_abbrev(new_mot: list[str], abvs_key_to_end: str = None) -> None:
    """
    Supprime l'ancienne abréviation et rentre la nouvelle
    """
    print(new_mot, abvs_key_to_end)
    abvs_key_to_end = abvs_key_to_end if abvs_key_to_end is not None else new_mot[0]
    old_mot = list(ABBREV[abvs_key_to_end].values())[:-1]  # prend en compte le 'is_sub_abv', donc [:-1]
    columns_changed = column_changed(new_mot, old_mot)
    # print(columns_changed)
    for column in columns_changed:
        if column == PARAMS[0] or column == PARAMS[1]:
            verify_sub_abvs(old_mot)
            suppr_abbrev(abvs_key_to_end)

            add_abv(new_mot)

        elif column == PARAMS[2]:  # is_suffix
            abvs_key_to_end_declined = [abvs_key_to_end,
                                        abvs_key_to_end.capitalize(),
                                        abvs_key_to_end + 's',
                                        (abvs_key_to_end + 's').capitalize()]

            for abv in abvs_key_to_end_declined:
                if abv in abbreviations.keys() and abv in ABBREV.keys():
                    abbreviations[abv].end_abv()
                    abbreviations[abv].def_suffix(1 if is_positive(new_mot[2]) else 0)
                    abbreviations[abv].start_abv()
                    ABBREV[abv][PARAMS[2]] = 1 if is_positive(new_mot[2]) else 0

        elif column == PARAMS[3]:  # has sub-abv maj
            verify_sub_abv_maj(new_mot)
            verify_sub_abv_maj_plur(new_mot)

            ABBREV[abvs_key_to_end][PARAMS[3]] = 1 if is_positive(new_mot[3]) else 0

        elif column == PARAMS[4]:  # has sub-abv plur
            verify_sub_abv_plur(new_mot)
            verify_sub_abv_maj_plur(new_mot)

            ABBREV[abvs_key_to_end][PARAMS[4]] = 1 if is_positive(new_mot[4]) else 0

    if PARAMS[3] in columns_changed and PARAMS[4] in columns_changed:
        verify_sub_abv_plur(new_mot)

    """
    Old version

    # supprime l'ancienne
    verify_sub_abvs(new_mot)
    suppr_abbrev(abvs_key_to_end)

    # rentre la nouvelle
    add_in_abv(list_to_dico(new_mot + ['0']))
    abbreviations[new_mot[0]].start_abv()
    if int(new_mot[3]):  # Majuscule
        add_abv_maj(new_mot)
    if int(new_mot[4]):  # pluriel
        add_abv_plur(new_mot)
    if int(new_mot[3]) and int(new_mot[4]):  # les deux
        add_abv_maj_plur(new_mot)
    """


def add_abv_plur(mot: list[str]) -> None:
    """
    Ajoute une abréviation avec un "s" final.
    Est utilisée lorsque est rentrée le paramètre "1" lors de l'ajout d'une abréviation
    """
    add_in_abv(list_to_dico([mot[0] + 's', remove_final_space(mot[1]) + 's'] + mot[2:] + ['1']))
    abbreviations[mot[0] + 's'].start_abv()


def add_abv_maj(mot: list[str]) -> None:
    """
    Ajoute une abréviation avec la première lettre en majuscule.
    Est utilisée lorsque est rentrée le paramètre "1" lors de l'ajout d'une abréviation
    """
    add_in_abv(list_to_dico([mot[0].capitalize(), mot[1].capitalize()] + mot[2:] + ['1']))
    abbreviations[mot[0].capitalize()].start_abv()


def add_abv_maj_plur(mot: list[str]) -> None:
    """
    Ajoute une abréviation avec un "s" final et une majuscule en première lettre.
    Est utilisée lorsque est rentrée le paramètre "1" aux paramètres "majuscule" et "pluriel" lors de l'ajout d'une
    abréviation
    """
    add_in_abv(
        list_to_dico([(mot[0] + 's').capitalize(), (remove_final_space(mot[1]) + 's').capitalize()] + mot[2:] + ['1']))
    abbreviations[(mot[0] + 's').capitalize()].start_abv()


def add_in_abv(dico: dict) -> None:
    """
    Prend en entrée une liste représentant une abréviation
    la rajoute dans chaque liste nécessaire
    """
    # print(dico)
    if (dico[PARAMS[0]] not in ABBREV.keys() and
       dico[PARAMS[0]] not in abbreviations.keys() and
       dico[PARAMS[0]] not in STATS_BY_ABV.keys()):
        ABBREV[dico[PARAMS[0]]] = dico
        abbreviations[dico[PARAMS[0]]] = Abbreviation(abv=dico[PARAMS[0]],
                                                      fr=dico[PARAMS[1]],
                                                      suffix=dico[PARAMS[2]],
                                                      has_sub_abv_maj=dico[PARAMS[3]],
                                                      has_sub_abv_plur=dico[PARAMS[4]],
                                                      is_sub_abv=dico[PARAMS[5]])
        STATS_BY_ABV[dico[PARAMS[0]]] = [0, 0]
        log(f"L'abréviation {dico[PARAMS[0]]} est utilisable !")


def confirm(message: str, message_de_confirmation: str = "\nAppuyez sur [entrer]") -> None:
    write(message + message_de_confirmation)
    wait('enter')
    suppr_text(len(message + message_de_confirmation) + 1)


def verify_sub_abv_maj(mot: list[str]) -> None:
    if not is_positive(mot[3]) and is_positive(ABBREV[mot[0]][PARAMS[3]]):  # False and True
        suppr_abbrev(mot[0].capitalize())
    elif is_positive(mot[3]) and not is_positive(ABBREV[mot[0]][PARAMS[3]]):  # True and False
        add_abv_maj(mot)
    elif is_positive(mot[3]) and is_positive(ABBREV[mot[0]][PARAMS[3]]):  # True and True
        if mot[0].capitalize() in ABBREV.keys():
            if mot[1].capitalize() != remove_final_space(ABBREV[mot[0].capitalize()][PARAMS[1]]):
                suppr_abbrev(mot[0].capitalize())
                add_abv_maj(mot)
        else:
            add_abv_maj(mot)


def verify_sub_abv_plur(mot: list[str]) -> None:
    if not is_positive(mot[4]) and is_positive(ABBREV[mot[0]][PARAMS[4]]):  # False and True
        suppr_abbrev(mot[0] + 's')
    elif is_positive(mot[4]) and not is_positive(ABBREV[mot[0]][PARAMS[4]]):  # True and False
        add_abv_plur(mot)
    elif is_positive(mot[4]) and is_positive(ABBREV[mot[0]][PARAMS[3]]):  # True and True
        if mot[0] + 's' in ABBREV.keys():
            if (mot[1] + 's') != remove_final_space(ABBREV[mot[0] + 's'][PARAMS[1]]):
                suppr_abbrev(mot[0] + 's')
                add_abv_plur(mot)
        else:
            add_abv_plur(mot)


def verify_sub_abv_maj_plur(mot: list[str]) -> None:
    if (not is_positive(mot[3]) or not is_positive(mot[4])) and (is_positive(ABBREV[mot[0]][PARAMS[3]]) and
                                                                 is_positive(ABBREV[mot[0]][PARAMS[4]])):  # False and True
        suppr_abbrev((mot[0] + 's').capitalize())
    elif (is_positive(mot[3]) and is_positive(mot[4])) and (not is_positive(ABBREV[mot[0]][PARAMS[3]]) or
                                                            not is_positive(ABBREV[mot[0]][PARAMS[4]])):  # True and False
        add_abv_maj_plur(mot)
    elif (is_positive(mot[3]) and is_positive(mot[4])) and (is_positive(ABBREV[mot[0]][PARAMS[3]]) and
                                                            is_positive(ABBREV[mot[0]][PARAMS[4]])):  # True and 1
        if (mot[0] + 's').capitalize() in ABBREV.keys():
            if (mot[1] + 's').capitalize() != remove_final_space(ABBREV[(mot[0] + 's').capitalize()][PARAMS[1]]):
                suppr_abbrev((mot[0] + 's').capitalize())
                add_abv_maj_plur(mot)
        else:
            add_abv_maj_plur(mot)


def verify_sub_abvs(mot: list[str]) -> None:
    verify_sub_abv_maj(mot)
    verify_sub_abv_plur(mot)
    verify_sub_abv_maj_plur(mot)


def add_abv(mot: list[str]) -> None:
    """
    Prend en entrée la liste contenant les paramètres de l'abréviation
    vérifie si elle est dans la base de donnée et propose une modification si oui
    si non, la rajoute
    """
    log(str(mot))
    if all(val != "" for val in mot):
        if mot[0] in ABBREV.keys():  # abv in database
            text = f"\n***\nL'abréviation rentrée est déjà dans la BDD et " \
                   f"associée au mot \"{ABBREV[mot[0]][PARAMS[1]]}\".\n" \
                   f"Appuyez sur [o] pour modifier l'association de \"{mot[0]}\" avec \"{mot[1]}\", " \
                   f"sur [n] pour ne rien faire ou " \
                   f"sur [s] pour la supprimer : "
            write(text)
            go_on = True
            while go_on:
                sleep(0.0001)
                if is_pressed('o'):
                    suppr_text(len(text))

                    verify_sub_abvs(mot)

                    if list_to_dico(mot + ['0']) != ABBREV[mot[0]]:
                        modif_abbrev(mot)
                    go_on = False
                elif is_pressed('n'):
                    suppr_text(len(text))
                    log("L'abréviation n'a pas été ajoutée. ")
                    go_on = False
                elif is_pressed('s'):
                    suppr_text(len(text))
                    suppr_abbrev(mot[0])
                    go_on = False

        elif remove_final_space(mot[1]) in [abv[PARAMS[1]][:-1] for abv in ABBREV.values()]:
            abv = [key for key in ABBREV.keys() if
                   ABBREV[key][PARAMS[1]][:-1] == (mot[1][:-1] if mot[1][-1] == ' ' else mot[1])][0]
            text = f"\n***\nLe mot '{mot[1]}' est déjà associé à '{abv}'. \n" \
                   f"Appuyez sur [o] pour que '{mot[0]}' soit associé avec '{mot[1]}', " \
                   f"sur [n] pour ne rien faire ou " \
                   f"sur [s] pour supprimer l'association de '{abv}' avec '{mot[1]}' : "
            write(text)
            go_on = True
            while go_on:
                sleep(0.0001)
                if is_pressed('o'):
                    suppr_text(len(text) + 1)
                    modif_abbrev(mot, abv)
                    log("L'abréviation est maintenant associée au mot. ")
                    go_on = False
                elif is_pressed('n'):
                    suppr_text(len(text))
                    log("L'abréviation n'a pas été ajoutée. ")
                    go_on = False
                elif is_pressed('s'):
                    suppr_text(len(text))
                    suppr_abbrev(mot[0])
                    log(f"L'abréviation {mot[0]} a été supprimée de la BDD")
                    go_on = False

        else:
            add_in_abv(list_to_dico(mot + ['0']))
            abbreviations[mot[0]].start_abv()
            if is_positive(mot[3]):  # Majuscule
                add_abv_maj(mot)
            if is_positive(mot[4]):  # pluriel
                add_abv_plur(mot)
            if is_positive(mot[3]) and is_positive(mot[4]):  # les deux
                add_abv_maj_plur(mot)

        save_everything('sql')


def is_positive(val: str | int) -> bool:
    if val in ["yes", "y", "true", "t", "vrai", "v", "oui", "o", "1", 1]:
        return True
    elif val in ["no", "n", "false", "f", "faux", "non", "n", "0", 0]:
        return False
    else:
        txt_feedback = " n'est pas reconnu comme étant positif ou négatif. Si vous pensez qu'il est l'un ou l'autre, " \
                       "envoyez un feedback à l'adresse mail pro.maxduh22@gmail.com et votre proposition sera étudiée. " \
                       "En attendant, sachez qu'il a été considéré comme négatif pour s'assurer aucun paramètre " \
                       "involontaire. Si vous vouliez qu'il soit reconnu comme positif, modifiez l'abréviation et " \
                       "rentrez \"yes\" à la place."
        log(val + txt_feedback)


def selector() -> None:
    question = "\nQue voulez-vous faire ? \n"
    options = []
    options.append(("a", "Ajouter une abréviation"))  # touche d'accès, action
    options.append(("s", "Supprimer une abréviation"))
    options.append(("m", "Modifier une abréviation"))
    options.append(("r", "Rechercher si une abréviation est déja rentrée"))
    options.append(("d", "Voir mes données"))
    options.append(("t", "Voir mon temps gagné"))
    options.append(("esc", "Annuler"))

    text = question
    for option in options:
        text += f"[{option[0]}] - {option[1]}\n"
    text += "Entrez une touche associée : "

    write(text)

    go_on = True
    while go_on:
        if is_pressed("a"):  # ajouter une abréviation
            suppr_text(len(text) + 1)
            add_abv(record_all("add"))
            go_on = False

        if is_pressed("s"):  # supprimer une abréviation
            suppr_text(len(text) + 1)
            abv = record_all("suppr")
            if abv in ABBREV.keys():
                suppr_abbrev(abv)
            else:
                confirm("L'abréviation rentrée n'est pas dans la BDD.")
                go_on = False
            if abv.capitalize() in ABBREV.keys() or (abv + 's') in ABBREV.keys():
                suppr_sub_abvs_txt = f"Voulez-vous supprimez les sous-abréviations de {abv} ? " \
                                     f"Appuyez sur [o] si oui, sinon sur [n] : "
                write(suppr_sub_abvs_txt)
                suppr_sub_abvs = False

                go_on1 = True
                while go_on1:
                    if is_pressed("o"):
                        suppr_sub_abvs = True
                        go_on1 = False
                    if is_pressed("n"):
                        go_on1 = False
                suppr_text(len(suppr_sub_abvs_txt) + 1)

                if suppr_sub_abvs:
                    sub_abvs = [abv.capitalize(),
                                abv + 's',
                                (abv + 's').capitalize()]
                    for sub_abv in sub_abvs:
                        suppr_abbrev(sub_abv)

            save_everything('sql')
            go_on = False

        if is_pressed("m"):  # modifier une abréviation
            suppr_text(len(text) + 1)
            text1 = "Entrez les nouvelles informations de l'abréviation : "
            write(text1)
            mot = record_all("modif")
            suppr_text(len(text1))

            if all(val != "" for val in mot) and mot[0] in ABBREV.keys():
                modif_abbrev(mot)
                save_everything('sql&txt')
            else:
                if not all(val != "" for val in mot):
                    confirm("Toutes les informations n'ont pas été complétées.")
                else:
                    confirm("L'abréviation n'est pas dans la BDD.")

            go_on = False

        if is_pressed("r"):  # Rechercher si une abréviation est déja rentrée
            suppr_text(len(text)+1)

            abv = record_all("rechercher")
            txt = ""

            if abv in ABBREV.keys():
                txt = "L'abréviation est dans la BDD. Voici ces paramètres "
                params_beau = ["Abréviation",
                               "Mot complet",
                               "Est-ce un suffixe",
                               "Existe-il une sous-abréviation avec une majuscule",
                               "Existe-il une sous-abréviation au pluriel",
                               "Est-ce une sous-abréviation"]

                for i in range(len(list(ABBREV[abv].values()))):
                    param = params_beau[i]
                    value = ABBREV[abv][PARAMS[i]]
                    if value == 1:
                        value = 'oui'
                    elif value == 0:
                        value = 'non'
                    txt += f"\n{param} : {value}"
            else:
                txt = "L'abréviation n'est pas dans la BDD."

            confirm(txt)
            go_on = False


        if is_pressed("d"):  # voir mes données
            suppr_text(len(text) + 1)
            confirm("Cette fonctionnalité n'est pas encore prête. ")
            go_on = False

        if is_pressed("t"):  # Voir mon temps gagné
            suppr_text(len(text) + 1)
            confirm("Cette fonctionnalité n'est pas encore prête. ")
            go_on = False

        if is_pressed("esc"):  # Annuler
            suppr_text(len(text) +1)
            go_on = False


def cut_over_n_char(txt: str, n: int) -> str:
    if len(txt) <= n:
        return txt
    else:
        if '\n' not in txt[:n+1]:
            nieme_char = n
            while txt[nieme_char] != ' ':
                nieme_char -= 1
            return txt[:nieme_char + 1] + '\n' + cut_over_n_char(txt[nieme_char + 1:], n)
        else:
            return txt[:txt.index('\n')+1] + cut_over_n_char(txt[txt.index('\n')+1:], n)


def premier_demarrage() -> None:
    txt1 = "Merci d'avoir installé ABVS !\n" \
           "Je vois que c'est votre première fois dans ABVS: " \
           "c'est surprenant de voir du texte s'écrire sous vos yeux sans rien avoir écrit hein ?! " \
           "Sachez que c'est comme ça que vous communiquerez avec ABVS !\n" \
           "D'ailleurs, une réponse vous sera souvent demandée sous la forme de l'appui sur une touche, " \
           "cette touche sera notée entre crochets, comme ceci avec la touche a par exemple: [a] !\n" \
           "Aimeriez-vous que je vous fasse une courte explication de comment fonctionne ABVS et que je vous accompagne " \
           "dans l'écriture de votre première abréviation ?\n" \
           "Si oui, appuyez sur [o]. Si non, appuyez sur [n]: "

    txt1 = cut_over_n_char(txt1, 120)

    write(txt1)

    go_on1 = True
    while go_on1:
        if is_pressed('o'):
            suppr_text(len(txt1) + 1)

            txt2 = "Pour rentrer votre première abréviation, appuyez sur les touches [a], [b], [v], et [_] en même temps. " \
                   "Un texte s'affichera alors. " \
                   "Il vous donnera plusieurs options, que vous pourrez étudier plus tard, dont celle d'appuyer sur [a] " \
                   "pour \"ajouter une nouvelle abréviation\". " \
                   "Lorsque vous appuyerez sur [a], le texte s'effacera.\n" \
                   "Une nouvelle ligne apparaitra qui vous demande l'abréviation que vous utiliserez. Après l'avoir écrite, appuyez sur [esc].\n" \
                   "Une nouvelle ligne apparaitra qui vous demande le mot complet. Après l'avoir écrit, appuyez sur [esc].\n" \
                   "Une nouvelle ligne apparaitra qui vous demande si votre abréviation est un suffixe. Répondez " \
                   "simplement par 'oui' ou 'non'.\nPareil pour les deux lignes suivantes. " \
                   "Voici par exemple ce que vous pourriez rentrer :\n\n" \
                   "Abréviation : abv\n" \
                   "Mot complet : abréviation\n" \
                   "Est-ce un suffixe : non\n" \
                   "Faut-il une sous-abréviation avec une majuscule : oui\n" \
                   "Faut-il une sous-abréviation au pluriel : oui\n\n" \
                   "Ici, l'abréviation est 'abv', le mot auquel elle réfère est 'abréviation', ce " \
                   "n'est pas un suffixe: c'est un mot entier, l'abréviation sera déclinée " \
                   "avec une majuscule au début de l'abréviation et du mot complet (Abv -> Abréviation), "  \
                   "l'abréviation sera déclinée au pluriel (abvs -> abréviations). Sachez que si les deux " \
                   "derniers chiffres sont des '1', il y aura aussi une abréviation en majuscule et en pluriel " \
                   "(Abvs -> Abréviations).\nNous allons maintenant rentrer votre première abréviation !"

            confirm(cut_over_n_char(txt2, 120))

            txt = "Essayez avec notre exemple, vous pourrez le modifier plus tard : "
            write(txt)
            add_abv(record_all('add'))
            suppr_text(len(txt))

            txt = "Et voilà ! Votre première abréviation est rentrée dans la BDD. Vous pouvez essayez pour voir ! " \
                  "Écrivez 'abv' et tapez un espace ensuite !"

            confirm(txt, "\nAppuyez sur [entrer] lorsque vous serez prêt à continuer ! ")

            go_on1 = False
        elif is_pressed('n'):
            suppr_text(len(txt1) + 1)

            txt2 = "Bien, je vous laisse donc découvrir ABVS par vous-même ! Sachez que le fichier README est toujours " \
                   "à votre disposition si vous voulez de l'aide ! Je vous laisse entrez votre première abréviation " \
                   "(sans quoi le tutoriel vous sera encore proposé la fois prochaine). "

            confirm(cut_over_n_char(txt2, 120))

            add_abv(record_all("add"))

            go_on1 = False



try:
    go_on = True
    abbreviation()
    # raise_an_error()
    while go_on:
        sleep(0.05)
        if is_pressed("a + b + v + _"):
            suppr_text(4)

            if list(ABBREV.keys()) == []:
                premier_demarrage()
            else:
                selector()
        if is_pressed("shift + esc"):
            stop_abbrev()
            log("fin du programme !")
            go_on = False
        verify_backup()
except KeyboardInterrupt:
    save_everything('sql&txt')
except Exception as err:
    error_txt = "Une erreur est survenue. Envoyer un mail à \"pro.maxduh22@gmail.com\" avec ces lignes :\n"
    for value in traceback.extract_tb(err.__traceback__):
        error_txt += get_error_datas(value)
    error_txt += f"{str(type(err))[8:-2]} : {err}"
    log(error_txt)
    save_everything('sql&txt')