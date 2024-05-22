import common.sheet_import.sheet_to_listings as sheet_to_listings

imports = {}

def sheet_import(data, id):
    try:
        listings, errors = sheet_to_listings.get_data(data["sheet_id"], data)
        imports[id] = (listings, errors)
        print('Done with import (success)')
    except Exception as e:
        imports[id] = ([], [None, "Error with input data: " + str(e)])
        print('Done with import (error)')