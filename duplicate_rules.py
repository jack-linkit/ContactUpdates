from contact import Contact

def standard_duplicate_rule(contact1 : Contact, contact2: Contact) -> int:
    """Returns 1 if the contacts are duplicates, 0 otherwise"""
    if contact1.email == contact2.email:
        return 1
    elif contact1.firstname == contact2.firstname and contact1.lastname == contact2.lastname and contact1.account_name == contact2.account_name:
        return 1
    else:
        return 0


