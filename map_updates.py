import csv
import sys
import os
import pprint
from typing import Dict, Generator, Any

REPORT_PATH = 'salesforce_contacts.csv'
OUTPUT_PATH = 'new_report.csv'

NAV_HEADERS = ['Complimen- tary 5 Year State Report', 'District-Level Benchmark Reports', 'School-Level Benchmark Reports', 'Teacher- Level Benchmark Reports', 'College & Career Readiness Reports', 'ELLs/MLs Reports', 'Reading Level Reports', 'Attendance, Grades, Behavior Reports', 'Equity and Demographics Studies', 'Teacher Comparison']
PLANNING_HEADERS = ['Sending Rosters', 'Assessment Calendar', 'Data Locker Management']
DIST_HEADERS = ['MTSS \nTeam', 'Testing Coordinator', 'Data Team']

errors = {
    'Missing Roles':set()
}

def create_role_dict(path: str):
    """Creates a dictionary of roles and their associated permissions"""
    role_dict = {}
    with open(path, 'r') as f:
        reader = csv.reader(f, quotechar='"')
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
            if len(row['Email']) > 0 and len(row['Title']) > 0 and row['Email'] != 'N/A':
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
    # check if there is a salutation in the name
    salutations = ["Mr.", "Ms.", "Mrs.", "Dr.", "Mr", "Ms", "Mrs", "Dr"]
    try:
        if row['Name'].split()[0] in salutations:
            row['Name'] = row['Name'].split(maxsplit=1)[1].strip()
    except Exception:
        print(row)
        print(row['Name'].split(maxsplit=1).strip())
        raise ValueError(f"Could not split name: {row['Name']} ({row['Email']})")
    
    try:
        firstname, lastname = row['Name'].split(maxsplit=1)
    except ValueError:
        raise ValueError(f"Could not split name: {row['Name']} ({row['Email']})")

    title = row['Title'].strip()
    try:
        role = role_dict[title].strip()
    except KeyError as e:
        if "Supervisor" in title:
            role = "Student Services Leadership"
        else:
            errors['Missing Roles'].add(title)
            role = 'Error'
    email = row['Email'].strip()
    email = ''.join(email.split())
    school = row['Central Office or School Name(s)']

    nav_communication = get_nav_communication(row)

    planning_communication = get_planning_communication(row)

    additional_responsibilities = get_additional_responsibilities(row)

    user['firstname'] = firstname
    user['lastname'] = lastname
    user['title'] = title
    user['role'] = role
    user['email'] = email.lower()
    user['school'] = school
    user['nav_communication'] = ';'.join(nav_communication)
    user['planning_communication'] = ';'.join(planning_communication)
    user['additional_responsibilities'] = ';'.join(additional_responsibilities)
    user['confirmed'] = '1'

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
    new_user['school'] = u2['school']
    new_user['nav_communication'] = merge_values(u1['nav_communication'], u2['nav_communication'])
    new_user['planning_communication'] = merge_values(u1['planning_communication'], u2['planning_communication'])
    new_user['additional_responsibilities'] = merge_values(u1['additional_responsibilities'], u2['additional_responsibilities'])
    new_user['confirmed'] = '1'

    return new_user

def test_all_headers(row: Dict[str, str]):
    """Tests that all headers are present in the row"""
    for header in NAV_HEADERS + PLANNING_HEADERS + DIST_HEADERS:
        if header not in row:
            raise ValueError(f"Header {header} not found")
    return True    

def match_contact(contact_row, contacts_dict):
    contact_match = None
    if contact_row['Email'].lower() in contacts:
        contact_match = contacts_dict[contact_row['Email']]
    return contact_match

def update_report(report_path: str, contacts: Dict[str, Dict[str, str]]) -> set:
    """Creates a report of the updates to be made."""
    # for now we'll just create a new report file instead of updating the existing one
    # only rows that were updated are written to the new file
    existing_contacts = set()
    with open(report_path, 'r', encoding='UTF-8') as report_file:
        file_existed = os.path.exists(OUTPUT_PATH)
        with open(OUTPUT_PATH, 'a', encoding='UTF-8') as new_report_file:
            reader = csv.DictReader(report_file)
            writer = csv.DictWriter(new_report_file, fieldnames=reader.fieldnames, quoting=csv.QUOTE_NONNUMERIC)
            if not file_existed:
                writer.writeheader()

            for row in reader:
                contact_match = match_contact(row, contacts) 
                if contact_match is not None:
                    contact = contacts[row['Email']]
                    row['First Name'] = contact['firstname']
                    row['Last Name'] = contact['lastname']
                    row['Title'] = contact['title']
                    row['Role'] = contact['role']
                    row['School'] = contact['school']
                    row['Navigator Communication'] = contact['nav_communication']
                    row['Planning Communication'] = contact['planning_communication']
                    row['Additional Responsibilities'] = contact['additional_responsibilities']
                    row['Confirmed by Customer'] = contact['confirmed']
                    writer.writerow(row)
                    existing_contacts.add(row['Email'])
    
    new_contacts_to_add = set(contacts.keys()) - existing_contacts
    return new_contacts_to_add

def add_new_contacts(district_name: str, report_path: str, contacts: Dict[str, Dict[str, str]], acct_dict: Dict[str, str]):
    """Adds new contacts to the report"""
    with open(report_path, 'r', encoding='UTF-8') as report_file:
        reader = csv.DictReader(report_file)
        existing_headers = reader.fieldnames

    with open(OUTPUT_PATH, 'a', encoding='UTF-8') as report_file:
        writer = csv.DictWriter(report_file, fieldnames=existing_headers, quoting=csv.QUOTE_NONNUMERIC)

	# TODO need to figure out how new accts can be added (Contact ID = null?)
        for contact in contacts.values():
            row = {}
            row['Account Name'] = district_name
            row['Account ID'] = acct_dict[district_name]
            row['Contact ID'] = ''
            row['First Name'] = contact['firstname']
            row['Last Name'] = contact['lastname']
            row['Title'] = contact['title']
            row['Role'] = contact['role']
            row['School'] = contact['school']
            row['Email'] = contact['email']
            row['Navigator Communication'] = contact['nav_communication']
            row['Planning Communication'] = contact['planning_communication']
            row['Additional Responsibilities'] = contact['additional_responsibilities']
            row['Confirmed by Customer'] = contact['confirmed']
            writer.writerow(row)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python map_updates.py <district_folder_path>")
        sys.exit(1)
    
    try:
        os.remove(OUTPUT_PATH)
    except FileNotFoundError:
        pass

    acct_dict = create_acct_dict(REPORT_PATH)
    role_dict = create_role_dict('role_dictionary.csv')

    districts_folder_path = sys.argv[1]

    # go through each file in the folder and add them to the contacts dictionary

    for filename in os.listdir(districts_folder_path):
        contacts = {}
        district_path = os.path.join(districts_folder_path, filename)
        district_name = filename.split('.')[0]

        for row in read_contact_updates(district_path):
            user = create_updates(row, role_dict)
            if user['email'] in contacts:
                user = merge_duplicates(contacts[user['email']], user)
            contacts[user['email']] = user
        

        new_contact_emails = update_report(REPORT_PATH, contacts)

        new_contacts = {email: contacts[email] for email in new_contact_emails}

        add_new_contacts(district_name, REPORT_PATH, new_contacts, acct_dict)
    
    print('Updates Completed.')

    for error_type in errors.keys():
        if len(errors[error_type]) > 0:
            print(f'{error_type}:')
            for err in errors[error_type]:
                print(f'\t{err}')
        else:
            print(f'0 {error_type} errors.')
