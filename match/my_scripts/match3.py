import googlemaps
from pprint import pprint
from .logic import bdate_time_place_to_degs

# Input data for the StartPoint is array of degrees
# degs_person1 = [
#     9.02, 326.45, 341.8, 349.03, 96.67, 336.63, 133.73, 143.12, 323.12, 318.27
# ]
#
# degs_person2 = [
#     87.33, 147.73, 67.7, 43.15, 191.18, 129.03, 318.27, 208.08, 28.08, 205.38
# ]

def match3_p_to_p(degs_person1, degs_person2):
    GLOBAL_PLANETS = ['Su', 'Mo', 'Me', 'Ma', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke', 'As']
    GLOBAL_SIGNS = ['Ar', 'Ta', 'Ge', 'Ca', 'Le', 'Vg', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi']

    # Person-12 SHEETS BEGIN #
    # -------------------------------------------
    def sheet_person12(degs):
        TABLE_constant_01 = lambda deg: int(deg // 30) + 1
        sign_nums = [TABLE_constant_01(i) for i in degs]
        sign_names = [GLOBAL_SIGNS[i - 1] for i in sign_nums]
        last_deg_to_sign = sign_nums[-1] - 1
        TABLE_04 = {GLOBAL_SIGNS[i if i <= 11 else i - 12]: i - last_deg_to_sign + 1 for i in range(last_deg_to_sign, last_deg_to_sign + 12)}
        TABLE_05_houses = [TABLE_04[i] for i in sign_names]
        TABLE_05 = dict(zip(GLOBAL_PLANETS, TABLE_05_houses))
        return TABLE_04, TABLE_05, sign_names
    # -------------------------------------------
    # Person-12 SHEETS END #

    # P_asp_P SHEET BEGIN #
    # -------------------------------------------
    TABLE_04_P1, TABLE_05_P1, sign_names_p1 = sheet_person12(degs_person1)
    TABLE_04_P2, TABLE_05_P2, sign_names_p2 = sheet_person12(degs_person2)


    TABLE_constant_03 = {
        '180': lambda x: 6 + x if 6 + x <= 12 else x - 6,
        '150': lambda x: 7 + x if 7 + x <= 12 else x - 5,
        '120<': lambda x: 4 + x if 4 + x <= 12 else x - 8,
        '>120': lambda x: 8 + x if 8 + x <= 12 else x - 4,
        '90<': lambda x: 3 + x if 3 + x <= 12 else x - 9,
        '>90': lambda x: 9 + x if 9 + x <= 12 else x - 3,
        '60<': lambda x: 2 + x if 2 + x <= 12 else x - 10,
        '>60': lambda x: 10 + x if 10 + x <= 12 else x - 2
    }

    TABLE_15_type = []
    for i in ['Conj', '180', '120<', '>120', '90<', '>90', '60<', '>60']:
        TABLE_15_type.extend([i for j in range(10)])
    TABLE_15_type += ['150']

    TABLE_15_planet = GLOBAL_PLANETS * 8 + ['Ma']

    TABLE_15_in_house = list(TABLE_05_P1.values()) * 8 + [list(TABLE_05_P1.values())[3]]

    TABLE_15_h_with_aspect = list(TABLE_05_P1.values()) + [TABLE_constant_03[TABLE_15_type[i]](TABLE_15_in_house[i]) for i in range(10, len(TABLE_15_type))]

    TABLE_15_signs_p1 = [dict(zip(TABLE_04_P1.values(), TABLE_04_P1.keys()))[i] for i in TABLE_15_h_with_aspect]

    TABLE_15_signs_p2 = sign_names_p2 * 8 + [sign_names_p2[3]]

    TABLE_15_concs, TABLE_15_concs_add = dict(), dict()

    for i in range(len(GLOBAL_PLANETS)):
        TABLE_15_concs[GLOBAL_PLANETS[i]] = list()
        TABLE_15_concs_add[GLOBAL_PLANETS[i]] = list()
        if TABLE_15_signs_p1[i - 11] == TABLE_15_signs_p2[-1]:
            TABLE_15_concs_add[GLOBAL_PLANETS[i]].append(TABLE_15_type[-1] + '_' + TABLE_15_planet[-1] + TABLE_15_planet[i - 11])
        for j in range(len(TABLE_15_signs_p1) - 1):
            if TABLE_15_signs_p1[int(j // 10) * 10 + i] == TABLE_15_signs_p2[j]:
                if GLOBAL_PLANETS[i] in 'Ra,Ke' and TABLE_15_type[j] in '>90 90< >60 60< >180 180<':
                    pass
                else:
                    TABLE_15_concs[GLOBAL_PLANETS[i]].append(TABLE_15_type[j] + '_' + TABLE_15_planet[int(j // 10) * 10 + i] + TABLE_15_planet[j])

    TABLE_15_concs = {i: TABLE_15_concs[i] + TABLE_15_concs_add[i] for i in TABLE_15_concs}

    TABLE_conca_01_conexion = [
        'Fr3', 'Fr2', 'Comm3', 'Team3', 'Soc3', 'Fr1', 'Di3', 'Conf3', 'Conf3', 'Soc3',
        'Fr2', 'Tru3', 'Comm3', 'Team2', 'Tru3', 'Lo3', 'Di1', 'Comp3', 'Conf3', 'Lo3',
        'Comm3', 'Comm3', 'Comm3', 'Team3', 'Fr2', 'Lo2', 'Comm1', 'Comp2', 'Comp3',
        'Fr3', 'Team3', 'Team2', 'Team3', 'Team3', 'Team2', 'Sex3', 'Conf2', 'Conf3',
        'Conf3', 'Team3', 'Soc3', 'Tru3', 'Comm2', 'Team2', 'Fr2', 'Lo1', 'Di1', 'Comp2',
        'Comp3', 'Tru2', 'Soc1', 'Lo3', 'Lo1', 'Sex3', 'Fr1', 'Lo3', 'Fr2', 'Comp3', 'Comp3',
        'Lo3', 'Di3', 'Di1', 'Comm2', 'Conf2', 'Soc1', 'Fr2', 'Di3', 'Comp2', 'Conf3', 'Di2',
        'Conf3', 'Conf3', 'Comp2', 'Conf3', 'Comp2', 'Sex2', 'Comp2', 'Comp3', 'Conf3', 'Comp3',
        'Comp3', 'Conf3', 'Comp2', 'Conf3', 'Comp3', 'Sex2', 'Conf3', 'Conf3', 'Conf3', 'Conf3',
        'Soc3', 'Tru3', 'Fr3', 'Team3', 'Tru2', 'Lo3', 'Di2', 'Comp3', 'Conf3', 'Fr2'
    ]
    TABLE_conca_01 = {GLOBAL_PLANETS[i] + GLOBAL_PLANETS[j]: TABLE_conca_01_conexion[i * 10 + j] for i in range(len(GLOBAL_PLANETS)) for j in range(len(GLOBAL_PLANETS))}

    #TABLE_15_issues = [j.split('_')[0] + '_' + TABLE_conca_01[j.split('_')[1]] for j in TABLE_15_concs[i] for i in TABLE_15_concs]
    TABLE_15_issues = [j.split('_')[0] + '_' + TABLE_conca_01[j.split('_')[1]] for i in TABLE_15_concs.values() for j in i]

    TABLE_26 = {i: 0 for i in ['Fr', 'Conf', 'Di', 'Comp', 'Lo', 'Sex', 'Soc', 'Team', 'Tru', 'Comm']}
    TABLE_26_mults = {'Conj': 10, '180': 8, '120': 6, '90': 4, '60': 2, '150': 6}

    items_fix = {
        'Soc': 'Sociable',
        'Gro': 'Growth',
        'Comm': 'Communicative',
        'FO': 'Family-Oriented',
        'Adve': 'Adventure',
        'Dome': 'Domestic',
        'Conf': 'Conflictive',
        'Di': 'Distant',
        'Spi': 'Spiritual/Travel',
        'Fr': 'Friendly',
        'Team': 'Teamwork',
        'Comp': 'Complicate',
        'Lo': 'Love',
        'Sex': 'Sex',
        'Tru': 'Trust'
    }

    TABLE_owr_1 = [j.split('_')[0] + j.split('_')[1] + '_' + TABLE_conca_01[j.split('_')[1]] for i in TABLE_15_concs.values() for j in i]
    TABLE_owr = {items_fix[i] + j: [n.split('_')[0] for n in TABLE_owr_1 if i + j in n] for i in ['Fr', 'Conf', 'Di', 'Comp', 'Lo', 'Sex', 'Soc', 'Team', 'Tru', 'Comm'] for j in ['1', '2', '3']}

    for i in TABLE_26:
        for j in ['1', '2', '3']:
            for n in ['Conj', '180', '120', '90', '60', '150']:
                TABLE_26[i] += sum([1 for issue in TABLE_15_issues if i + j in issue and n in issue]) * TABLE_26_mults[n] * int(j)

    TABLE_26_how_much = {i: sum([TABLE_conca_01_conexion.count(i + j) for j in ['1', '2', '3']]) for i in ['Fr', 'Conf', 'Di', 'Comp', 'Lo', 'Sex', 'Soc', 'Team', 'Tru', 'Comm']}

    TABLE_14 = {i: round(TABLE_26[i] * 30 / TABLE_26_how_much[i], 1) for i in TABLE_26}
    # TABLE_14 is the final table for this sheet and it takes part in the calculation of final charts
    # -------------------------------------------
    # P_asp_P SHEET END #

    # P_asp_H SHEET BEGIN #
    # -------------------------------------------
    TABLE_6_type = ['In' for i in range(9)] + ['180' for i in range(7)] + ['150'] + [i for i in ['120<', '>120', '90<', '>90', '60<', '>60'] for j in range(7)]

    TABLE_6_planet = GLOBAL_PLANETS[:-1] + GLOBAL_PLANETS[:-3] + ['Ma'] + [j for i in range(6) for j in GLOBAL_PLANETS[:-3]]

    # Fix from Vladimir, 12.08.2019
    TABLE_6_in_house_dict = {i: TABLE_05_P1[i] for i in TABLE_6_planet[:9]}
    TABLE_6_in_house = [TABLE_6_in_house_dict[i] for i in TABLE_6_planet]
    #for i in range(len(TABLE_6_planet) - 9):
    #    TABLE_6_in_house.append(TABLE_6_in_house[i])

    TABLE_6_aspect_he = TABLE_6_in_house[:9] + [TABLE_constant_03['180'](i) for i in TABLE_6_in_house[9:16]] + [TABLE_constant_03['150'](TABLE_6_in_house[16])]
    TABLE_6_aspect_he += [TABLE_constant_03['120<'](i) for i in TABLE_6_in_house[17:24]] + [TABLE_constant_03['>120'](i) for i in TABLE_6_in_house[24:31]]
    TABLE_6_aspect_he += [TABLE_constant_03['90<'](i) for i in TABLE_6_in_house[31:38]] + [TABLE_constant_03['>90'](i) for i in TABLE_6_in_house[38:45]]
    TABLE_6_aspect_he += [TABLE_constant_03['60<'](i) for i in TABLE_6_in_house[45:52]] + [TABLE_constant_03['>60'](i) for i in TABLE_6_in_house[52:59]]

    TABLE_04_P1_reversed = dict(zip(TABLE_04_P1.values(), TABLE_04_P1.keys()))
    TABLE_6_aspect_he_signs = [TABLE_04_P1_reversed[i] for i in TABLE_6_aspect_he]

    TABLE_6_aspect_she = [TABLE_04_P2[i] for i in TABLE_6_aspect_he_signs]

    TABLE_6_mix_conca = [TABLE_6_type[i] + '_' + TABLE_6_planet[i] + str(TABLE_6_aspect_she[i]) for i in range(len(TABLE_6_aspect_she))]

    TABLE_7_PH = [i + str(j + 1) for i in GLOBAL_PLANETS[:-1] for j in range(12)]
    TABLE_7_issues = 'Soc3,Gro1,Team3,FO1,Adve2,Dome1,Soc1,Di2,Spi2,Team3,Spi3,'
    TABLE_7_issues += 'Di2,Lo2,Gro2,Comm2,FO3,Adve3,Dome3,Lo3,Di3,Spi3,Team2,Fr3,'
    TABLE_7_issues += 'Di3,Comm3,Gro2,Comm3,FO1,Adve3,Dome1,Fr3,Di2,Spi2,Team3,Fr3,'
    TABLE_7_issues += 'Di2,Team2,Gro2,Team3,FO1,Adve3,Dome1,Conf2,Conf3,Spi1,Team3,'
    TABLE_7_issues += 'Fr1,Conf3,Tru2,Gro3,Comm1,FO3,Adve2,Dome3,Lo2,Di2,Spi3,Team2,'
    TABLE_7_issues += 'Fr2,Di1,Lo3,Gro2,Comm2,FO3,Adve3,Dome2,Lo3,Di2,Spi3,Team2,'
    TABLE_7_issues += 'Fr3,Di1,Di2,Gro1,Di1,Di1,Di1,Di2,Di3,Di3,Spi1,Team1,Di1,Di3,'
    TABLE_7_issues += 'Comp3,Comp2,Comp2,Comp3,Comp1,Comp3,Conf2,Comp3,Comm1,Comp1,'
    TABLE_7_issues += 'Comp1,Comp2,Conf3,Conf2,Conf1,Conf2,Conf2,Conf3,Conf3,Conf3,Conf2,Conf2,Conf1,Conf1'
    TABLE_7_issues = TABLE_7_issues.split(',')

    TABLE_7 = {TABLE_7_PH[i]:TABLE_7_issues[i] for i in range(len(TABLE_7_issues))}

    TABLE_6_conexion = [i.split('_')[0] + '_' + TABLE_7[i.split('_')[1]] for i in TABLE_6_mix_conca]

    TABLE_owr_2 = [i.split('_')[0] + i.split('_')[1] + '_' + TABLE_7[i.split('_')[1]] for i in TABLE_6_mix_conca]
    TABLE_owr_3 = list(set(TABLE_7_issues))
    TABLE_owr_pasph = {items_fix[i[:-1]] + i[-1]: [j.split('_')[0] for j in TABLE_owr_2 if i in j] for i in TABLE_owr_3}

    TABLE_141328 = {i: 0 for i in 'Soc,Gro,Comm,FO,Adve,Dome,Conf,Di,Spi,Fr,Team,Comp,Lo'.split(',')}
    TABLE_141328_mults = {'In': 10,'180': 8,'120': 6,'90': 4,'60': 2,'150': 6}
    for i in TABLE_141328:
        for j in ['1', '2', '3']:
            for n in ['In', '180', '120', '90', '60', '150']:
                TABLE_141328[i] += sum([1 for issue in TABLE_6_conexion if i + j in issue and n in issue]) * TABLE_141328_mults[n] * int(j)

    TABLE_141328_how_much = {i: sum([TABLE_7_issues.count(i + j) for j in ['1', '2', '3']]) for i in 'Soc,Gro,Comm,FO,Adve,Dome,Conf,Di,Spi,Fr,Team,Comp,Lo'.split(',')}

    TABLE_1413 = {i: round(TABLE_141328[i] * 15 / TABLE_141328_how_much[i], 1) for i in TABLE_141328}

    TABLE_8 = {}
    for i in TABLE_1413:
        if i not in TABLE_14:
            TABLE_8[i] = round(TABLE_1413[i], 1)
        else:
            TABLE_8[i] = round((TABLE_1413[i] + TABLE_14[i]) / 2, 1)
    for i in TABLE_14:
        if i not in TABLE_8:
            TABLE_8[i] = round(TABLE_14[i], 1)
    TABLE_8['Spi'] += round(TABLE_8['Tru'] / 2, 1)
    # TABLE_8 is the final result for the whole function
    # -------------------------------------------
    # P_asp_H SHEET END #
    return [TABLE_8, TABLE_owr, TABLE_owr_pasph, [TABLE_04_P1, TABLE_05_P1], degs_person1, [TABLE_04_P2, TABLE_05_P2], degs_person2]

def match3(bdate1, bdate2, btime1, btime2, bplace1, bplace2, degs=None):
    KEY = 'AIzaSyASsKRcBk1D1J_oWy7teTjodHQ5N1uOl1M'
    api = googlemaps.Client(key=KEY)
    if not degs:
        degs_person1 = bdate_time_place_to_degs(api, bdate1, btime1, bplace1)
        degs_person2 = bdate_time_place_to_degs(api, bdate2, btime2, bplace2)
    else:
        degs_person1 = degs
        degs_person2 = degs
    pprint(degs_person1)
    return match3_p_to_p(degs_person1, degs_person2)

#match3_p_to_p(degs_person1, degs_person2)
