from typing import Dict

NAV_HEADERS = ['Complimen- tary 5 Year State Report', 'District-Level Benchmark Reports', 'School-Level Benchmark Reports', 'Teacher- Level Benchmark Reports', 'College & Career Readiness Reports', 'ELLs/MLs Reports', 'Reading Level Reports', 'Attendance, Grades, Behavior Reports', 'Equity and Demographics Studies', 'Teacher Comparison']
PLANNING_HEADERS = ['Sending Rosters', 'Assessment Calendar', 'Data Locker Management']
DIST_HEADERS = ['MTSS \nTeam', 'Testing Coordinator', 'Data Team']

def get_nav_communication(row: Dict[str, str]) -> list:
    """Gets the navigator communication preferences for the contact"""
    nav_communication = []
    try:
        if row.get(NAV_HEADERS[0]) and row[NAV_HEADERS[0]] == "TRUE":
            nav_communication.append("5 Year State Assessment")

        if row.get(NAV_HEADERS[1]) and row[NAV_HEADERS[1]] == "TRUE":
            nav_communication.append("District-Level Benchmark")

        if row.get(NAV_HEADERS[2]) and row[NAV_HEADERS[2]] == "TRUE":
            nav_communication.append("School-Level Benchmark")

        if row.get(NAV_HEADERS[3]) and row[NAV_HEADERS[3]] == "TRUE":
            nav_communication.append("Teacher-Level Benchmark")

        if row.get(NAV_HEADERS[4]) and row[NAV_HEADERS[4]] == "TRUE":
            nav_communication.append("CCR")

        if row.get(NAV_HEADERS[5]) and row[NAV_HEADERS[5]] == "TRUE":
            nav_communication.append("ELLs/MLs")

        if row.get(NAV_HEADERS[6]) and row[NAV_HEADERS[6]] == "TRUE":
            nav_communication.append("Reading Levels")

        if row.get(NAV_HEADERS[7]) and row[NAV_HEADERS[7]] == "TRUE":
            nav_communication.append("Attendance, Grades, Behavior")

        if row.get(NAV_HEADERS[8]) and row[NAV_HEADERS[8]] == "TRUE":
            nav_communication.append("Equity and Demographics")

        if row.get(NAV_HEADERS[9]) and row[NAV_HEADERS[9]] == "TRUE":
            nav_communication.append("Teacher Comp")

    except KeyError as e:
        raise e

    return nav_communication

def get_planning_communication(row: Dict[str, str]) -> list:
    """Gets the planning communication preferences for the contact"""
    planning_communication = []
    try:
        if row.get(PLANNING_HEADERS[0]) and row[PLANNING_HEADERS[0]] == "TRUE":
            planning_communication.append("SIS")

        if row.get(PLANNING_HEADERS[1]) and row[PLANNING_HEADERS[1]] == "TRUE":
            planning_communication.append("Assessment Calendar")

        if row.get(PLANNING_HEADERS[2]) and row[PLANNING_HEADERS[2]] == "TRUE":
            planning_communication.append("Data Locker")

    except KeyError as e:
        raise e

    return planning_communication

def get_additional_responsibilities(row: Dict[str, str]) -> list:
    """Gets the additional responsibilities for the contact"""
    additional_repsonsibilities = []
    try:
        if row.get(DIST_HEADERS[0]) and row[DIST_HEADERS[0]] == "TRUE":
            additional_repsonsibilities.append("MTSS Team")

        if row.get(DIST_HEADERS[1]) and row[DIST_HEADERS[1]] == "TRUE":
            additional_repsonsibilities.append("Testing Coordinator")

        if row.get(DIST_HEADERS[2]) and row[DIST_HEADERS[2]] == "TRUE":
            additional_repsonsibilities.append("Data Team")

    except KeyError as e:
        # print(row)
        raise e

    return additional_repsonsibilities