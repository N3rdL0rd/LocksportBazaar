"""
Command-line script to add a new field to the user objects.
"""

import json
import argparse

def add_user_field(users, field, default):
    for user in users.values():
        if field not in user:
            user[field] = json.loads(default)
    return users

def main():
    parser = argparse.ArgumentParser(description="Add a new field to the user objects.")
    parser.add_argument("field", help="The name of the field to add.")
    parser.add_argument("default", help="The default value for the field - JSON object.")
    args = parser.parse_args()

    users = json.load(open('data/users.json'))
    users = add_user_field(users, args.field, args.default)
    with open('data/users.json', 'w') as f:
        json.dump(users, f, indent=4)

if __name__ == "__main__":
    main()