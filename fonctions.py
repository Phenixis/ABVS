# *** BDD link ***
import sqlite3 as sql
from functools import wraps

db = sql.connect("Data/ABVS.bdd")
cursor = db.cursor()
PARAMS = ["abv", "mot_complet", "is_suffix", "has_sub_abv_maj", "has_sub_abv_plur", "is_sub_abv", 'use_abv',
          'use_non_abv']
PK = {"Abbreviations": PARAMS[0],
      "Users": "pseudo"}


def remove_final_space(s: str) -> str:
    return s[:-1] if s[-1] == ' ' else s

def def_params(nb_args: int) -> str:  # done
    """
    Renvoie un string contenant nb_args fois "?" entouré de parenthèses
    """
    return '(' + ("?, " * nb_args)[:-2] + ')'  # remove the 2 last chars because it is ", "


def select_command(columns: str | list[str] | tuple[str]):
    if type(columns) == str:
        return columns
    else:
        return ''.join([column + ', ' for column in columns])[:-2]


def select_values(table: str,
                  columns: str | list[str] | tuple[str],
                  condition: list[str, str | int] | tuple[str, str | int] | list[tuple[str, str | int]] = None,
                  order: list[str] = None) -> list[tuple[str | int]] | tuple[str | int]:  # done
    """
    Sélectionne toutes les valeurs d'une table selon les paramètres et les conditions fournis et les renvoie
    """
    command_line = f"SELECT {select_command(columns)} FROM {table}"
    parameters = []

    if condition:
        command_line += f" WHERE {conditions(condition)}"
        parameters += only_values(condition)
    if order:
        command_line += f" ORDER BY {order[0]} {order[1]}"

    # print(command_line)
    return cursor.execute(command_line, parameters).fetchall()


def select_all_values(table: str, condition: tuple[str, str | int] | list[tuple[str, str | int]] = None,
                      order: list[str] = None) -> list[tuple[str | int]]:  # done
    """
    Sélectionne toutes les valeurs d'une table et les renvoie
    """
    command_line = f"SELECT * FROM {table}"
    parameters = []

    if condition:
        command_line += f" WHERE {conditions(condition)}"
        parameters += only_values(condition)
    if order:
        command_line += f" ORDER BY {order[0]} {order[1]}"

    return cursor.execute(command_line, parameters).fetchall()


def add_values(table: str, values: list | tuple) -> None:  # done
    """
    Ajoute les valeurs 'values' dans la table 'table'
    """
    cursor.execute(f"INSERT INTO {table} VALUES {def_params(len(values))}", values)


def add_multiple_values_to_bdd(table: str, list_of_values: list | tuple) -> None:
    """
    - table: le nom de la table à laquelle on veut accéder en str
    - list_of_values: un objet représentant l'ensemble des valeurs à ajouter à la table sous forme de liste ou de tuple
    """
    for values in list_of_values:
        add_values(table, values)
    # db.commit()


def conditions(id: tuple[str, str | int] | list[tuple[str, str | int]], separator: str = " AND ") -> str:  # done
    """
    return a str which is in the form:
    param1 = ? AND param2 = ? ...
    """
    res = ""
    # print(id)
    if type(id[0]) == str:
        res = f"{id[0]} = ?"
    else:
        for couple in id:
            res += f"{couple[0]} = ?" + separator

        res = res[:-len(separator)]
    # print(res)
    return res


def del_value(table: str, condition: tuple[str, str | int] = None) -> None:  # done
    """
    Delete the values according to the given conditions
    """
    command_line = f"DELETE FROM {table}"
    parameters = []

    if condition:
        command_line += f" WHERE {conditions(condition)}"
        parameters += only_values(condition)
    # print(command_line, parameters)
    cursor.execute(command_line, parameters)


def only_values(lst: list[tuple] | tuple) -> list:  # done
    """
    return the values from a list of couples (param, value)
    """
    if type(lst[0]) != tuple and type(lst[0]) != list:
        lst = [lst]
    return [value[-1] for value in lst]


def update_val(table: str, to_set: tuple[str, str | int] | list[tuple[str, str | int]],
               condition: tuple[str, str | int] | list[tuple[str, str | int]]) -> None:  # done
    """
    update the values according to the given couple (param : value) and given conditions
    """
    command_line = f"UPDATE {table} SET {conditions(to_set, ', ')} WHERE {conditions(condition)}"
    parameters = only_values(to_set) + only_values(condition)

    # print(command_line, parameters)
    cursor.execute(command_line, parameters)


def def_abbrev() -> dict[str: dict[str: str | int]]:  # done
    """
    Récupère toutes les abréviations enregistrées dans la BDD et les renvoie
    """
    abbreviations = {}
    datas = select_all_values("Abbreviations")

    for data in datas:
        abbreviations[data[0]] = {PARAMS[i]: data[i] for i in range(len(data) - 2)}
        # print(abbreviations[data[0]])

    return abbreviations


def def_values() -> dict[str: int]:
    values = {}
    with open("Data/values.txt", 'r', encoding='utf-8') as f:
        for row in f:
            # print(row[:-1])
            if "***" not in row:
                row = row.split(':')
                if row[0] in ["nb_abv", "nb_sub_abv"]:
                    values[row[0]] = 0
                else:
                    if '%' in row[1]:
                        values[row[0]] = int(row[1][:-2])  # row[0] = le nom: row[1] = la valeur associée
                    else:
                        values[row[0]] = int(row[1])  # row[0] = le nom: row[1] = la valeur associée
    # print(values)
    return values


def def_stats() -> dict[str: list[int]]:
    stats_by_abv = {}
    values = select_values("Abbreviations", [PARAMS[0]] + PARAMS[-2:])

    for value in values:
        stats_by_abv[value[0]] = list(value[1:])

    return stats_by_abv


def abv_in_db(abv: str) -> bool:
    return True if select_values("Abbreviations", PARAMS[0], [PARAMS[0], abv]) else False


def column_changed(lst1: list, lst2: list):
    columns_changed = []

    if len(lst1) != len(lst2):
        print("Problem : lenght of lst1 if different from length of lst2")
        return ["Problem of lenght"]
    else:
        for i in range(len(lst1)):
            if remove_final_space(str(lst1[i])) != remove_final_space(str(lst2[i])):
                columns_changed.append(PARAMS[i])

    return columns_changed



def has_changed(table: str, columns: str | list[str] | tuple[str], id: str, values: list[str | int]) -> list:
    saved_values = select_values(table, columns, [PK[table], id])[0]
    return column_changed(saved_values, values)


def raise_an_error():
    bite


def get_line(path: str, nb_line: int) -> str:
    try:
        file = open(path, 'r', encoding='utf-8')
    except:
        return f"The path file {path} isn't correct."
    i = 0
    for line in file:
        i += 1
        if i == nb_line:
            while line.startswith(' '):
                line = line[1:]
            return line
    return "the file doesn't contains this number of line."


def get_error_datas(value) -> str:
    line = str(value)[14:-1]

    file = line[13:line.index(',')]

    nb_line_left = line.index('e', line.index(',')) + 2
    nb_line_right = line.index(' ', nb_line_left)
    nb_line = line[nb_line_left:nb_line_right]

    error_line = get_line(file, int(nb_line))

    return line + ':\n\t' + error_line