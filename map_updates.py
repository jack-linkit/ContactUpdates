import csv
import sys
from typing import Dict, Generator, Any

REPORT_PATH = 'salesforce_contacts.csv'

NAV_HEADERS = ['Complimen- tary 5 Year State Report', 'District-Level Benchmark Reports', 'School-Level Benchmark Reports', 'Teacher- Level Benchmark Reports', 'College & Career Readiness Reports', 'ELLs/MLs Reports', 'Reading Level Reports', 'Attendance, Grades, Behavior Reports', 'Equity and Demographics Studies', 'Teacher Comparison']
PLANNING_HEADERS = ['Sending Rosters', 'Assessment Calendar', 'Data Locker Management']
DIST_HEADERS = ['MTSS \nTeam', 'Testing Coordinator', 'Data Team']

def create_role_dict(path: str):
    """Creates a dictionary of roles and their associated permissions"""
    role_dict = {}
    with open(path, 'r') as f:
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            role_dict[row[0]] = row[1]
    return role_dict

def create_acct_dict(path: str):
    acct_dict = {}
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        next(reader)

        for row in reader:
            if row['Account Name'] not in acct_dict:
                acct_dict[row['Account Name']] = row['Account ID']
    return acct_dict

def read_contact_updates(district_file_path: str) -> Generator[Dict[str, str], None, None]:
    """Reads in the updates from the district's provided contact management file"""
    with open(district_file_path, 'r') as district_file:
        reader = csv.DictReader(district_file)
        for row in reader:
            yield row
    
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
        # print(row)
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


def create_updates(row: Dict[str, str], role_dict: Dict[str, str]) -> dict:
    """Creates the updates for each contact."""
    user = {}
    # TODO might be worth removing firstname and lastname
    try:
        firstname, lastname = row['Name'].split()
    except ValueError:
        raise ValueError(f"Could not split name: {row[1]}")

    title = row['Title'].strip()
    role = role_dict[title].strip()
    email = row['Email'].strip()

    nav_communication = get_nav_communication(row)

    planning_communication = get_planning_communication(row)

    additional_responsibilities = get_additional_responsibilities(row)

    user['firstname'] = firstname
    user['lastname'] = lastname
    user['title'] = title
    user['role'] = role
    user['email'] = email
    user['nav_communication'] = ';'.join(nav_communication)
    user['planning_communication'] = ';'.join(planning_communication)
    user['additional_responsibilities'] = ';'.join(additional_responsibilities)

    return user

def merge_values(s1: str, s2: str) -> list:
    """Merges two lists, removing duplicates"""
    if len(s1) == 0:
        return s2
    if len(s2) == 0:
        return s1

    l1 = s1.split(';')
    l2 = s2.split(';')
    new_list = list(set(l1 + l2))
    return ';'.join(new_list)

def merge_duplicates(u1, u2):
    # if there are duplicates, merge their preferences and choose the most recent other data
    # user the same fields as those in create_updates
    new_user = {}
    new_user['firstname'] = u1['firstname']
    new_user['lastname'] = u1['lastname']
    new_user['title'] = u1['title']
    new_user['role'] = u1['role']
    new_user['email'] = u1['email']
    new_user['nav_communication'] = merge_values(u1['nav_communication'], u2['nav_communication'])
    new_user['planning_communication'] = merge_values(u1['planning_communication'], u2['planning_communication'])
    new_user['additional_responsibilities'] = merge_values(u1['additional_responsibilities'], u2['additional_responsibilities'])

    return new_user

def test_all_headers(row: Dict[str, str]):
    """Tests that all headers are present in the row"""
    for header in NAV_HEADERS + PLANNING_HEADERS + DIST_HEADERS:
        if header not in row:
            raise ValueError(f"Header {header} not found")
    return True    

def update_report(report_path: str, contacts: Dict[str, Dict[str, str]]) -> set:
    """Creates a report of the updates to be made."""
    # for now we'll just create a new report file instead of updating the existing one
    # only rows that were updated are written to the new file
    existing_contacts = set()
    with open(report_path, 'r', encoding='UTF-8') as report_file:
        with open('new_report.csv', 'w', encoding='UTF-8') as new_report_file:
            reader = csv.DictReader(report_file)
            writer = csv.DictWriter(new_report_file, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                if row['Email'] in contacts:
                    contact = contacts[row['Email']]
                    row['First Name'] = contact['firstname']
                    row['Last Name'] = contact['lastname']
                    row['Title'] = contact['title']
                    row['Role'] = contact['role']
                    row['Navigator Communication'] = contact['nav_communication']
                    row['Planning Communication'] = contact['planning_communication']
                    row['Additional Responsibilities'] = contact['additional_responsibilities']
                    writer.writerow(row)
                    existing_contacts.add(row['Email'])
    
    new_contacts_to_add = set(contacts.keys()) - existing_contacts
    return new_contacts_to_add

def add_new_contacts(district_name: str, report_path: str, contacts: Dict[str, Dict[str, str]], acct_dict: Dict[str, str]):
    """Adds new contacts to the report"""
    with open(report_path, 'r', encoding='UTF-8') as report_file:
        reader = csv.DictReader(report_file)
        existing_headers = reader.fieldnames

    with open(report_path, 'a', encoding='UTF-8') as report_file:
        writer = csv.DictWriter(report_file, fieldnames=existing_headers)

        for contact in contacts.values():
            row = {}
            row['Account Name'] = district_name
            row['Account ID'] = acct_dict[district_name]
            row['First Name'] = contact['firstname']
            row['Last Name'] = contact['lastname']
            row['Title'] = contact['title']
            row['Role'] = contact['role']
            row['Email'] = contact['email']
            row['Navigator Communication'] = contact['nav_communication']
            row['Planning Communication'] = contact['planning_communication']
            row['Additional Responsibilities'] = contact['additional_responsibilities']
            writer.writerow(row)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python map_updates.py <district_file_path>")
        sys.exit(1)

    acct_dict = create_acct_dict(REPORT_PATH)
    role_dict = create_role_dict('role_dictionary.csv')

    district_path = sys.argv[1]
    district_name = district_path.split('/')[-1].split('.')[0]

    contacts = {}
    for row in read_contact_updates(district_path):
        user = create_updates(row, role_dict)
        if user['email'] in contacts:
            user = merge_duplicates(contacts[user['email']], user)
        contacts[user['email']] = user

    new_contact_emails = update_report(REPORT_PATH, contacts)

    new_contacts = {email: contacts[email] for email in new_contact_emails}

    add_new_contacts(district_name, REPORT_PATH, new_contacts, acct_dict)

    
