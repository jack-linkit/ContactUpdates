import csv
import sys
import os
import pprint
from typing import Dict, Generator, Any

from data_processing import create_role_dict, create_acct_dict, read_contact_updates
from communications import get_nav_communication, get_planning_communication, get_additional_responsibilities, NAV_HEADERS, PLANNING_HEADERS, DIST_HEADERS

REPORT_PATH = 'salesforce_contacts.csv'
OUTPUT_PATH = 'new_report.csv'


errors = {
    'Missing Roles':set()
}

    


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
        elif "Principal" in title: 
            role = "Building Level Leadership"
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
