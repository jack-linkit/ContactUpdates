from dataclasses import dataclass, field
from typing import Dict


class Contact:
    def __init__(self, firstname: str, lastname: str, title: str, email: str, school: str, account_name: str, salutation: str = ""):
        self.firstname = firstname
        self.lastname = lastname
        self.title = title.strip()
        self.email = email.strip().lower()
        self.school = school
        self.account_name = account_name
        self.salutation = salutation

    role: str = ""
    confirmed: str = ""
    nav_communication: str = ""
    planning_communication: str = ""
    additional_responsibilities: str = ""
    
    def create_updated_row(self, acct_dict = None, row: Dict[str, str] = None):
        if row is None and acct_dict is None:
            raise ValueError("Either acct_dict or row must be provided")
        if row is None:
            row = {}
        row['First Name'] = self.firstname
        row['Last Name'] = self.lastname
        row['Title'] = self.title
        row['Role'] = self.role
        row['School'] = self.school
        row['Navigator Communication'] = ';'.join(self.nav_communication)
        row['Planning Communication'] = ';'.join(self.planning_communication)
        row['Additional Responsibilities'] = ';'.join(self.additional_responsibilities)
        row['Confirmed by Customer'] = self.confirmed
        # case when the salesforce contact is being inserted
        if acct_dict is not None:
            row = {}
            row['Account Name'] = self.account_name
            row['Account ID'] = acct_dict[self.account_name]
            row['Contact ID'] = ''
        return row