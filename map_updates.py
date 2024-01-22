import csv
import sys
import os
import logging

from typing import Dict

from contact import Contact

from progressbar import progressbar
from data_processing import create_role_dict, create_acct_dict, read_contact_updates, role_from_title, extract_contact_name
from communications import get_nav_communication, get_planning_communication, get_additional_responsibilities, NAV_HEADERS, PLANNING_HEADERS, DIST_HEADERS
from duplicate_rules import standard_duplicate_rule

REPORT_PATH = 'salesforce_contacts.csv'
OUTPUT_PATH = 'new_report.csv'
ROLE_PATH = 'role_dictionary.csv'
 

def create_updates(row: Dict[str, str], district_name: str, role_dict: Dict[str, str]) -> Contact:
    first_name, last_name, salutation = extract_contact_name(row['Name'])
    contact = Contact(first_name, last_name, row['Title'], row['Email'], row['Central Office or School Name(s)'], district_name, salutation)
    contact.role = role_from_title(contact.title, role_dict)
    contact.confirmed = '1'
    # email = ''.join(email.split()).lower()
    contact.nav_communication = get_nav_communication(row)
    contact.planning_communication = get_planning_communication(row)
    contact.additional_responsibilities = get_additional_responsibilities(row)

    return contact

def merge_values(l1: str, l2: str) -> list:
    return list(set(l1 + l2))

def merge_duplicates(c1: Contact, c2: Contact):
    merged_nav_communication = merge_values(c1.nav_communication, c2.nav_communication)
    c1.nav_communication = merged_nav_communication

    merged_planning_communication = merge_values(c1.planning_communication, c2.planning_communication)
    c1.planning_communication = merged_planning_communication

    merged_additional_responsibilities = merge_values(c1.additional_responsibilities, c2.additional_responsibilities)
    c1.additional_responsibilities = merged_additional_responsibilities

    return c1

def test_all_headers(row: Dict[str, str]):
    """Tests that all headers are present in the row"""
    for header in NAV_HEADERS + PLANNING_HEADERS + DIST_HEADERS:
        if header not in row:
            raise ValueError(f"Header {header} not found")
    return True    

def match_contact(contact: Contact, contacts_dict: Dict[str, Contact]) -> Contact:
    standard_rule = lambda c: standard_duplicate_rule(contact, c)
    contact_matches = list(filter(standard_rule, contacts_dict.values()))
    if len(contact_matches) == 0:
        return None
    elif len(contact_matches) == 1:
        return contact_matches[0]
    elif len(contact_matches) > 1:
        logging.debug('Multiple Duplicates: %s', contact_matches)
        return contact_matches[0]

def update_report(report_path: str, contacts: Dict[str, Contact]) -> set:
    existing_contacts = set()

    with open(report_path, 'r', encoding='UTF-8') as report_file:
        file_existed = os.path.exists(OUTPUT_PATH)

        with open(OUTPUT_PATH, 'a', encoding='UTF-8') as new_report_file:
            reader = csv.DictReader(report_file)
            writer = csv.DictWriter(new_report_file, fieldnames=reader.fieldnames, quoting=csv.QUOTE_NONNUMERIC)
            if not file_existed:
                writer.writeheader()

            for row in reader:
                # TODO add salutation
                curr_contact = Contact(row['First Name'], row['Last Name'], row['Title'], row['Email'], row['School'], row['Account Name'])
                curr_contact.nav_communication = row['Navigator Communication'].split(';')
                curr_contact.planning_communication = row['Planning Communication'].split(';')
                curr_contact.additional_responsibilities = row['Additional Responsibilities'].split(';')

                contact_match = match_contact(curr_contact, contacts) 
                if contact_match is not None:
                    row = contact_match.create_updated_row(row=row)
                    writer.writerow(row)
                    existing_contacts.add(contact_match.email)
    
    new_contacts_to_add = set(contacts.keys()) - existing_contacts
    return new_contacts_to_add

def add_new_contacts(report_path: str, contacts: Dict[str, Contact], acct_dict: Dict[str, str]):
    with open(report_path, 'r', encoding='UTF-8') as report_file:
        reader = csv.DictReader(report_file)
        existing_headers = reader.fieldnames

    with open(OUTPUT_PATH, 'a', encoding='UTF-8') as report_file:
        writer = csv.DictWriter(report_file, fieldnames=existing_headers, quoting=csv.QUOTE_NONNUMERIC)

        for contact in contacts.values():
            row = contact.create_updated_row(acct_dict=acct_dict)
            writer.writerow(row)

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python map_updates.py <district_folder_path>")
        sys.exit(1)
    
    try:
        os.remove(OUTPUT_PATH)
    except FileNotFoundError:
        pass

    districts_folder_path = sys.argv[1]

    logging.basicConfig(filename='log.txt', encoding='UTF-8', level=logging.DEBUG)

    acct_dict = create_acct_dict(REPORT_PATH)
    role_dict = create_role_dict(ROLE_PATH)

    for filename in progressbar(os.listdir(districts_folder_path)):
        contacts = {}
        district_file_path = os.path.join(districts_folder_path, filename)
        district_name = filename.split('.')[0]

        for row in read_contact_updates(district_file_path):
            contact = create_updates(row, district_name, role_dict)
            if contact.email in contacts:
                try:
                    # TODO rename merge_duplicates to contact.update()?
                    contact = merge_duplicates(contacts[contact.email], contact)
                except AttributeError as e:
                    print(contact.email, contact.account_name)
                    exit(1)
            contacts[contact.email] = contact

        new_contact_emails = update_report(REPORT_PATH, contacts)

        new_contacts = {email: contacts[email] for email in new_contact_emails}

        add_new_contacts(REPORT_PATH, new_contacts, acct_dict)
    
    print('Updates Completed.')
