import os
import googlemaps
from pandas import read_excel
from flatlib import const
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart


# Some global variables
P_ASP_P_30 = {  # P_asp_P sheet coefficients
    "Sex": 7.5, "Love": 5, "Sociable": 3.33, "Friendly": 2.14, "Communicative": 3.75,
    "Teamwork": 3.33, "Complicate": 1.36, "Distant": 2.31, "Trust": 6, "Conflictive": 3
}

P_ASP_H_30 = {
    "Sociable": 6, "Growth": 4.286, "Communicative": 4.286, "Family-Oriented": 6, "Adventure": 4.286,
    "Domestic": 5, "Conflictive": 3.333, "Distant": 1.579, "Spiritual/Travel": 4.286, "Friendly": 3.75,
    "Teamwork": 2.727, "Complicate": 2.143}

CONSTANT_LIMITS_FOR_SIGNS = {
    "Ar": (0, 30),
    "Ta": (30, 60),
    "Ge": (60, 90),
    "Ca": (90, 120),
    "Le": (120, 150),
    "Vg": (150, 180),
    "Li": (180, 210),
    "Sc": (210, 240),
    "Sg": (240, 270),
    "Cp": (270, 300),
    "Aq": (300, 330),
    "Pi": (330, 360)
}

CONSTANT_LORDSHIP = {
    "Ar": "Ma", "Ta": "Ve", "Ge": "Me", "Ca": "Mo",
    "Le": "Su", "Vg": "Me", "Li": "Ve", "Sc": "Ma",
    "Sg": "Ju", "Cp": "Sa", "Aq": "Sa", "Pi": "Ju"
}

HOUSE_ORDER = {}

P_ASP_P_TABLE_DEGS = {
    1: {"180": 7, ">150": 8, "120<": 5, ">120": 9, "90<": 4, ">90": 10, "60<": 3, ">60": 11},
    2: {"180": 8, ">150": 9, "120<": 6, ">120": 10, "90<": 5, ">90": 11, "60<": 4, ">60": 12},
    3: {"180": 9, ">150": 10, "120<": 7, ">120": 11, "90<": 6, ">90": 12, "60<": 5, ">60": 1},
    4: {"180": 10, ">150": 11, "120<": 8, ">120": 12, "90<": 7, ">90": 1, "60<": 6, ">60": 2},
    5: {"180": 11, ">150": 12, "120<": 9, ">120": 1, "90<": 8, ">90": 2, "60<": 7, ">60": 3},
    6: {"180": 12, ">150": 1, "120<": 10, ">120": 2, "90<": 9, ">90": 3, "60<": 8, ">60": 4},
    7: {"180": 1, ">150": 2, "120<": 11, ">120": 3, "90<": 10, ">90": 4, "60<": 9, ">60": 5},
    8: {"180": 2, ">150": 3, "120<": 12, ">120": 4, "90<": 11, ">90": 5, "60<": 10, ">60": 6},
    9: {"180": 3, ">150": 4, "120<": 1, ">120": 5, "90<": 12, ">90": 6, "60<": 11, ">60": 7},
    10: {"180": 4, ">150": 5, "120<": 2, ">120": 6, "90<": 1, ">90": 7, "60<": 12, ">60": 8},
    11: {"180": 5, ">150": 6, "120<": 3, ">120": 7, "90<": 2, ">90": 8, "60<": 1, ">60": 9},
    12: {"180": 6, ">150": 7, "120<": 4, ">120": 8, "90<": 3, ">90": 9, "60<": 2, ">60": 10}
}

P_ASP_P_TABLE_PLANET_CONEXION = {
    "SuSu": "Sociable", "SuMo": "Friendly", "SuMe": "Communicative", "SuMa": "Teamwork", "SuJu": "Friendly",
    "SuVe": "Sociable", "SuSa": "Distant", "SuRa": "Conflictive", "SuKe": "Conflictive", "SuAs": "Sociable",

    "MoSu": "Friendly", "MoMo": "Trust", "MoMe": "Communicative", "MoMa": "Teamwork", "MoJu": "Friendly",
    "MoVe": "Love", "MoSa": "Distant", "MoRa": "Conflictive", "MoKe": "Conflictive", "MoAs": "Love",

    "MeSu": "Communicative", "MeMo": "Friendly", "MeMe": "Friendly", "MeMa": "Communicative", "MeJu": "Communicative",
    "MeVe": "Friendly", "MeSa": "Distant", "MeRa": "Complicate", "MeKe": "Complicate", "MeAs": "Friendly",

    "MaSu": "Teamwork", "MaMo": "Teamwork", "MaMe": "Teamwork", "MaMa": "Teamwork", "MaJu": "Teamwork",
    "MaVe": "Sex", "MaSa": "Distant", "MaRa": "Conflictive", "MaKe": "Conflictive", "MaAs": "Teamwork",

    "JuSu": "Sociable", "JuMo": "Friendly", "JuMe": "Communicative", "JuMa": "Sociable", "JuJu": "Friendly",
    "JuVe": "Trust", "JuSa": "Distant", "JuRa": "Complicate", "JuKe": "Complicate", "JuAs": "Friendly",

    "VeSu": "Sociable", "VeMo": "Love", "VeMe": "Friendly", "VeMa": "Sex", "VeJu": "Friendly",
    "VeVe": "Love", "VeSa": "Sociable", "VeRa": "Complicate", "VeKe": "Complicate", "VeAs": "Love",

    "SaSu": "Distant", "SaMo": "Distant", "SaMe": "Communicative", "SaMa": "Distant", "SaJu": "Sociable",
    "SaVe": "Friendly", "SaSa": "Distant", "SaRa": "Complicate", "SaKe": "Conflictive", "SaAs": "Distant",

    "RaSu": "Conflictive", "RaMo": "Conflictive", "RaMe": "Complicate", "RaMa": "Conflictive", "RaJu": "Complicate",
    "RaVe": "Sex", "RaSa": "Distant", "RaRa": "Complicate", "RaKe": "Complicate", "RaAs": "Complicate",

    "KeSu": "Complicate", "KeMo": "Complicate", "KeMe": "Complicate", "KeMa": "Complicate", "KeJu": "Complicate",
    "KeVe": "Sex", "KeSa": "Distant", "KeRa": "Complicate", "KeKe": "Complicate", "KeAs": "Complicate",

    "AsSu": "Sociable", "AsMo": "Trust", "AsMe": "Communicative", "AsMa": "Teamwork", "AsJu": "Trust",
    "AsVe": "Love", "AsSa": "Distant", "AsRa": "Complicate", "AsKe": "Complicate", "AsAs": "Trust"
}

P_ASP_H_TABLE_ISSUES = {
    "Su1": "Sociable", "Su2": "Growth", "Su3": "Communicative", "Su4": "Family-Oriented", "Su5": "Adventure", "Su6": "Domestic",
    "Su7": "Sociable", "Su8": "Distant", "Su9": "Spiritual/Travel", "Su10": "Teamwork", "Su11": "Friendly", "Su12": "Distant",

    "Mo1": "Sociable", "Mo2": "Growth", "Mo3": "Communicative", "Mo4": "Family-Oriented", "Mo5": "Adventure", "Mo6": "Domestic",
    "Mo7": "Love", "Mo8": "Distant", "Mo9": "Spiritual/Travel", "Mo10": "Teamwork", "Mo11": "Friendly", "Mo12": "Distant",

    "Me1": "Sociable", "Me2": "Growth", "Me3": "Communicative", "Me4": "Family-Oriented", "Me5": "Adventure", "Me6": "Domestic",
    "Me7": "Friendly", "Me8": "Distant", "Me9": "Spiritual/Travel", "Me10": "Teamwork", "Me11": "Friendly", "Me12": "Distant",

    "Ma1": "Teamwork", "Ma2": "Growth", "Ma3": "Teamwork", "Ma4": "Teamwork", "Ma5": "Adventure", "Ma6": "Domestic",
    "Ma7": "Conflictive", "Ma8": "Conflictive", "Ma9": "Spiritual/Travel", "Ma10": "Teamwork", "Ma11": "Friendly", "Ma12": "Conflictive",

    "Ju1": "Sociable", "Ju2": "Growth", "Ju3": "Communicative", "Ju4": "Family-Oriented", "Ju5": "Adventure", "Ju6": "Domestic",
    "Ju7": "Friendly", "Ju8": "Distant", "Ju9": "Spiritual/Travel", "Ju10": "Teamwork", "Ju11": "Friendly", "Ju12": "Distant",

    "Ve1": "Love", "Ve2": "Growth", "Ve3": "Communicative", "Ve4": "Family-Oriented", "Ve5": "Adventure", "Ve6": "Domestic",
    "Ve7": "Love", "Ve8": "Distant", "Ve9": "Spiritual/Travel", "Ve10": "Teamwork", "Ve11": "Friendly", "Ve12": "Distant",

    "Sa1": "Distant", "Sa2": "Growth", "Sa3": "Distant", "Sa4": "Distant", "Sa5": "Distant", "Sa6": "Distant",
    "Sa7": "Distant", "Sa8": "Distant", "Sa9": "Spiritual/Travel", "Sa10": "Teamwork", "Sa11": "Teamwork", "Sa12": "Distant",

    "Ra1": "Conflictive", "Ra2": "Complicate", "Ra3": "Communicative", "Ra4": "Complicate", "Ra5": "Adventure", "Ra6": "Distant",
    "Ra7": "Conflictive", "Ra8": "Complicate", "Ra9": "Communicative", "Ra10": "Complicate", "Ra11": "Complicate", "Ra12": "Complicate",

    "Ke1": "Conflictive", "Ke2": "Complicate", "Ke3": "Complicate", "Ke4": "Complicate", "Ke5": "Complicate", "Ke6": "Complicate",
    "Ke7": "Conflictive", "Ke8": "Conflictive", "Ke9": "Complicate", "Ke10": "Complicate", "Ke11": "Complicate", "Ke12": "Conflictive"
}

#
def bdate_to_degs(bdate):  # format: dd.mm.yyyy
    date_array = bdate.split('.')
    d, m, y = int(date_array[0]), int(date_array[1]), int(date_array[2])
    # String to search
    date_str = "Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec".split(',')[m - 1] + ' ' + str(d) + ' ' + str(y)
    data = read_excel(os.path.dirname(os.path.abspath(__file__)) + "/ephe.xlsx")[2:].values.tolist()
    # Search just in some values, not in all
    i = (y - int(data[0][0].split(' ')[2])) * 365
    data = data[i:i + 370]
    res = [i for i in data if date_str in i[0]][0][1:]
    return res

#
def bdate_time_place_to_degs(api, bdate, btime, bplace, lati=None, long=None):
    bdate = [int(i) for i in bdate.split('.')]
    if bdate[0] < 10:
        bdate[0] = '0' + str(bdate[0])
    else:
        bdate[0] = str(bdate[0])
    if bdate[1] < 10:
        bdate[1] = '0' + str(bdate[1])
    else:
        bdate[1] = str(bdate[1])
    bdate[2] = str(bdate[2])

    if len(bdate[0]) == 2:
        bdate = bdate[2] + '/' + bdate[1] + '/' + bdate[0]
    else:
        bdate = bdate[0] + '/' + bdate[1] + '/' + bdate[2]

    btime = str(btime)
    #
    if bplace is not None:
        place = api.geocode(bplace)
        lat, lon = place[0]['geometry']['location']['lat'], place[0]['geometry']['location']['lng']
    else:
        lat, lon = lati, long

    utcdiff = api.timezone([lat, lon])['rawOffset']
    udsign = str(utcdiff)[0]
    udsign = udsign if udsign == '-' else '+'
    utcdiff = abs(utcdiff)
    udh = utcdiff // 3600
    udm = (utcdiff - udh * 3600) // 60
    if udh < 10:
        udh = '0' + str(udh)
    else:
        udh = str(udh)
    if udm < 10:
        udm = '0' + str(udm)
    else:
        udm = str(udm)
    utcdiff = udsign + udh + ':' + udm

    nslat = None
    ewlon = None
    if lat < 0:
        nslat = 's'
    else:
        nslat = 'n'
    if lon < 0:
        ewlon = 'w'
    else:
        ewlon = 'e'
    lat = abs(lat)
    lon = abs(lon)
    lat_d = int(str(lat).split('.')[0])
    lat_m = str(int((lat - lat_d) * 60))
    lat_d = str(lat_d)
    lon_d = int(str(lon).split('.')[0])
    lon_m = str(int((lon - lon_d) * 60))
    lon_d = str(lon_d)
    bpl = [lat_d + nslat + lat_m, lon_d + ewlon + lon_m]
    #

    date = Datetime(bdate, btime, utcdiff)
    pos = GeoPos(bpl[0], bpl[1])
    chart = Chart(date, pos)

    res=[]
    res.append(chart.get(const.SUN).lon)
    res.append(chart.get(const.MOON).lon)
    res.append(chart.get(const.MERCURY).lon)
    res.append(chart.get(const.MARS).lon)
    res.append(chart.get(const.JUPITER).lon)
    res.append(chart.get(const.VENUS).lon)
    res.append(chart.get(const.SATURN).lon)
    res.append(chart.get(const.NORTH_NODE).lon)
    res.append(chart.get(const.SOUTH_NODE).lon)
    res.append(chart.get(const.ASC).lon)
    for i in range(len(res)):
        if res[i] - 23.81 < 0:
            res[i] = 360 + (res[i] - 23.81)
        else:
            res[i] -= 23.81
    return res

#

# hart PERSON-1 AND PERSON-2 SHEETS
#
# Finds the sign for planet (Enter manually table)
def find_sign_for_planet(deg, constant_limits):
    for k, v in constant_limits.items():
        if v[0] < deg < v[1]:
            return k
    else:
        return "Error"

# Obtains ephemeris data for specific date from file ephe.xlsx
def get_ephemeris_for_date(year, monthday):
    pass

# Calculate data for table ENTER MANUALLY on Person sheets
def table_persons_enter_manually(manual_degs_array, conversion_needed=True):
    def convert(deg_string):  # converts a string like 273 27 9 to float degrees
        a = deg_string.split(' ')
        return int(a[0]) + int(a[1]) / 60 + int(a[2]) / 3600
    if conversion_needed:
        degs = [convert(i) for i in manual_degs_array]
    else:
        degs = list(manual_degs_array)
    planets = "Su,Mo,Me,Ma,Ju,Ve,Sa,Ra,Ke,As".split(',')
    signs = [find_sign_for_planet(deg, CONSTANT_LIMITS_FOR_SIGNS) for deg in degs]
    return {planets[i]: {"sign": signs[i], "deg": degs[i]} for i in range(len(planets))}

# Calculate data for table with HOUSES on Person sheets
def table_persons_houses(data_table_enter_manually):
    signs = list(CONSTANT_LIMITS_FOR_SIGNS.keys())
    sign_of_As = data_table_enter_manually["As"]["sign"]
    h1 = [1 if i == sign_of_As else 0 for i in signs]
    h2 = [1 if h1[i] == 1 else 0 for i in (11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)]
    h3 = [1 if h1[i] == 1 else 0 for i in (10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)]
    h4 = [1 if h1[i] == 1 else 0 for i in (9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7, 8)]
    h5 = [1 if h1[i] == 1 else 0 for i in (8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6, 7)]
    h6 = [1 if h1[i] == 1 else 0 for i in (7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5, 6)]
    h7 = [1 if h1[i] == 1 else 0 for i in (6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4, 5)]
    h8 = [1 if h1[i] == 1 else 0 for i in (5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3, 4)]
    h9 = [1 if h1[i] == 1 else 0 for i in (4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2, 3)]
    h10 = [1 if h1[i] == 1 else 0 for i in (3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1, 2)]
    h11 = [1 if h1[i] == 1 else 0 for i in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1)]
    h12 = [1 if h1[i] == 1 else 0 for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0)]
    return {signs[i]: [h1[i], h2[i], h3[i], h4[i], h5[i], h6[i], h7[i], h8[i], h9[i], h10[i], h11[i], h12[i], i + 1] for i in range(len(signs))}

# Calculate data for table SIGN HOUSE Person sheets
def table_persons_sign_house(data_table_persons_houses):
    signs = list(CONSTANT_LIMITS_FOR_SIGNS.keys())
    houses = ["".join([str(j) for j in data_table_persons_houses[i]]).find("1") + 1 for i in signs]
    return {signs[i]: houses[i] for i in range(len(signs))}

# Calculate data for the HOUSE ITS_LORD table (the last on Person sheet)
def table_persons_house_its_lord(data_table_sign_house):
    lords = {data_table_sign_house[k]: v for k, v in CONSTANT_LORDSHIP.items()}
    return lords

def get_sheet_persons(array, conversion_needed=True):
    data_table_enter_manually = table_persons_enter_manually(array, conversion_needed)
    data_table_houses_persons = table_persons_houses(data_table_enter_manually)
    data_table_sign_house = table_persons_sign_house(data_table_houses_persons)
    data_table_persons_house_its_lord = table_persons_house_its_lord(data_table_sign_house)

    return {"table_enter_manually": data_table_enter_manually,
            "table_houses": data_table_houses_persons,
            "table_sign_house": data_table_sign_house,
            "table_house_its_lord": data_table_persons_house_its_lord}

#
# PERSON-1 AND PERSON-2 SHEETS

# P_ASP_P SHEET
#
def table_p_asp_p_main(data_sheet_persons1, data_sheet_persons2):
    # Calculate HOUSE_ORDER
    HOUSE_ORDER.clear()
    for k, v in data_sheet_persons1["table_sign_house"].items():
        HOUSE_ORDER[v] = k
    #
    conjs = ["Conj" for i in range(10)]
    s180 = ["180" for i in range(10)]
    s120less = ["120<" for i in range(10)]
    s120more = [">120" for i in range(10)]
    s90less = ["90<" for i in range(10)]
    s90more = [">90" for i in range(10)]
    s60less = ["60<" for i in range(10)]
    s60more = [">60" for i in range(10)]
    s150more = [">150"]

    pl = ["Su", "Mo", "Me", "Ma", "Ju", "Ve", "Sa", "Ra", "Ke", "As"]
    sp2 = [i["sign"] for i in data_sheet_persons2["table_enter_manually"].values()]
    house_sign = {v: k for k, v in data_sheet_persons1["table_sign_house"].items()}

    # Column Type
    types = conjs + s180 + s120less + s120more + s90less + s90more + s60less + s60more + s150more
    # Column Planet
    planets = [pl[i - 10 * int(i / 10)] for i in range(80)] + ["Ma"]
    # Column In House
    in_house = [data_sheet_persons1["table_sign_house"][data_sheet_persons1["table_enter_manually"][i]["sign"]] for i in planets]
    # Column H with Aspect
    h_with_aspect = in_house[:10] + [P_ASP_P_TABLE_DEGS[in_house[i]][types[i]] for i in range(10, 81)]
    # Column Signs-P1
    signs_p1 = [house_sign[i] for i in h_with_aspect]
    # Column Signs-P2
    signs_p2 = []
    for i in range(8):
        signs_p2.extend(sp2)
    signs_p2.append(signs_p2[73])
    # Columns Su-As-Conc
    def f_column_su_conc(planet="Su", add_k=0):
        su_conc=[]
        fk = 0
        for i in range(81):
            if i != 80:
                k = int(i / 10) * 10 + add_k
            else:
                k = int((i - 1) / 10) * 10 + add_k
            if signs_p1[k] == signs_p2[i]:
                su_conc.append(planet + planets[i])
            else:
                su_conc.append(0)
        return su_conc
    su_as_conc = [f_column_su_conc("Su Mo Me Ma Ju Ve Sa Ra Ke As".split(" ")[i], i) for i in range(10)]
    # Columns Su-As-Issues
    su_as_issues = {i: 0 for i in P_ASP_P_30.keys()}
    for j in range(len(su_as_conc)):
        item = su_as_conc[j]
        for i in range(len(item)):
            if item[i] != 0:
                if j in (7, 8) and types[i] not in ("Conj", "120<", ">120"):
                    k = 0
                else:
                    if "Conj" in types[i]:
                        k = 10
                    elif "180" in types[i]:
                        k = 8
                    elif "120" in types[i]:
                        k = 6
                    elif "90" in types[i]:
                        k = 4
                    elif "60" in types[i]:
                        k = 2
                    elif "150" in types[i]:
                        k = 6
                    else:
                        k = 0
                su_as_issues[P_ASP_P_TABLE_PLANET_CONEXION[item[i]]] += k
    for k in su_as_issues.keys():
        su_as_issues[k] *= P_ASP_P_30[k]
    return su_as_issues
# +-
# P_ASP_P SHEET

# P_ASP_H SHEET
#
def table_p_asp_h_main(data_sheet_persons1, data_sheet_persons2):
    # Column type
    types = ["In" for i in range(9)]
    types.extend(["180" for i in range(7)])
    types.append(">150")
    types.extend(["120<" for i in range(7)])
    types.extend([">120" for i in range(7)])
    types.extend(["90<" for i in range(7)])
    types.extend([">90" for i in range(7)])
    types.extend(["60<" for i in range(7)])
    types.extend([">60" for i in range(7)])
    # Column planet
    planets = "Su,Mo,Me,Ma,Ju,Ve,Sa,Ra,Ke,Su,Mo,Me,Ma,Ju,Ve,Sa,Ma".split(",")
    planets.extend("Su,Mo,Me,Ma,Ju,Ve,Sa,Su,Mo,Me,Ma,Ju,Ve,Sa,Su,Mo,Me,Ma,Ju,Ve,Sa,Su".split(","))
    planets.extend("Mo,Me,Ma,Ju,Ve,Sa,Su,Mo,Me,Ma,Ju,Ve,Sa,Su,Mo,Me,Ma,Ju,Ve,Sa".split(","))
    # Column in house
    in_house = [data_sheet_persons1["table_sign_house"][data_sheet_persons1["table_enter_manually"][p]["sign"]] for p in "Su,Mo,Me,Ma,Ju,Ve,Sa,Ra,Ke".split(",")]
    inh = list(in_house)
    for i in range(5):
        in_house.extend(inh)
    in_house.extend(inh[:5])
    # Column h-aspect-he
    h_aspect_he = in_house[:9]
    for i in range(len(in_house[9:])):
        h_aspect_he.append(P_ASP_P_TABLE_DEGS[in_house[i + 9]][types[i + 9]])
    # Column signs-he-aspect
    signs_he_aspect = [HOUSE_ORDER[i] for i in h_aspect_he]
    # Column h-aspect-she
    h_aspect_she = [data_sheet_persons2["table_sign_house"][i] for i in signs_he_aspect]
    # Column mix-conca
    mix_conca = [planets[i] + str(h_aspect_she[i]) for i in range(len(planets))]
    # Column conexion
    conexion = [P_ASP_H_TABLE_ISSUES[i] for i in mix_conca]
    # Compatibility table
    compatibility = {"Sociable": 0, "Growth": 0, "Communicative": 0, "Family-Oriented": 0,
                     "Adventure": 0, "Domestic": 0, "Conflictive": 0, "Distant": 0,
                     "Spiritual/Travel": 0, "Friendly": 0, "Teamwork": 0, "Complicate": 0}
    for i in range(len(conexion)):
        if types[i] == "In":
            k = 10
        elif "180" in types[i]:
            k = 8
        elif "120" in types[i]:
            k = 6
        elif "90" in types[i]:
            k = 4
        elif "60" in types[i]:
            k = 2
        elif "150" in types[i]:
            k = 6
        else:
            k = 0
        try:
            compatibility[conexion[i]] += k
        except Exception:
            pass
    # Applying k
    for k in compatibility.keys():
        compatibility[k] *= P_ASP_H_30[k]
    return compatibility
#
def table_p_asp_h_total(p_asp_p, p_asp_h):
    d = {"Sociable": 0, "Growth": 0, "Communicative": 0, "Family-Oriented": 0,
         "Adventure": 0, "Domestic": 0, "Conflictive": 0, "Distant": 0,
         "Spiritual/Travel": 0, "Friendly": 0, "Teamwork": 0, "Complicate": 0,
         "Sex": 0, "Love": 0, "Trust": 0}
    for k in d.keys():
        if k in p_asp_p.keys() and k in p_asp_h.keys():
            d[k] = (p_asp_p[k] + p_asp_h[k]) / 2
        elif k in p_asp_p.keys():
            d[k] = p_asp_p[k]
        else:
            d[k] = p_asp_h[k]
    return d
# P_ASP_H SHEET

def match(bdate1, bdate2, time1=None, time2=None, place1=None, place2=None, second_match=False):
    # Get arrays of degrees for both bdates
    if time1 == None:
        array1 = bdate_to_degs(bdate1)
        array2 = bdate_to_degs(bdate2)
    else:
        if not second_match:
            KEY = 'AIzaSyASsKRcBk1D1J_oWy7teTjodHQ5N1uOl1M'
            api = googlemaps.Client(key=KEY)
            array1 = bdate_time_place_to_degs(api, bdate1, time1, place1)
            array2 = bdate_time_place_to_degs(api, bdate2, time2, place2)
            with open('degrees.txt', 'w') as file:
                for i in array1:
                    file.write(str(i) + '\n')
                file.write('\n')
                for i in array2:
                    file.write(str(i) + '\n')
        else:
            with open('degrees.txt', 'r') as file:
                ldata = file.readlines()
                array2 = [float(i) for i in ldata[:10]]
                array1 = [float(i) for i in ldata[11:]]
    # Get tables for Person-1 and Person-2 sheets
    sheet_person1 = get_sheet_persons(array1, False)
    sheet_person2 = get_sheet_persons(array2, False)
    # Get tables for P_asp_P and P_asp_H sheets
    p_asp_p = table_p_asp_p_main(sheet_person1, sheet_person2)
    p_asp_h = table_p_asp_h_main(sheet_person1, sheet_person2)
    # Get the final table with scores
    total = table_p_asp_h_total(p_asp_p, p_asp_h)
    # Pretify values by rounding them
    for k in total.keys():
        total[k] = round(total[k], 1)
    return total

def match_all(bdate1, bdate2, time1=None, time2=None, place1=None, place2=None):
    total_1to2 = match(bdate1, bdate2, time1, time2, place1, place2)
    total_2to1 = match(bdate2, bdate1, time2, time1, place2, place1, second_match=True)

    return {'p1p2': total_1to2,
            'p2p1': total_2to1}
