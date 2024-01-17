import csv

from typing import Generator, Dict

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