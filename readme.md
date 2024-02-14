# TODO
- add webscraping capability
- refactor so majority of contact manipulation is done from the main file/function
- Fix issue with empty rows being output to new_report.csv

# Considerations
## Specific Decisions Made
- First and last names were not perfect to extract, but including them allows sorts to be more useful in SalesForce


# Step-By-Step
1. Go through each file in the directory provided as a command-line argument
    - For each file:
        1. Extract the title, email, first name, last name, role (via role dict), nav communication, planning communication and additional responsibilities
