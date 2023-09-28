from . import utils
import os

# function that creates a file called saves.csv in the .quickcd/ directory
def create_saves_file():
    if not utils.check_saves_dir():
        utils.create_saves_dir()

    saves_file = os.path.join(utils.QUICKCD_DIR, 'saves.csv')
    if not os.path.isfile(saves_file):
        # Create the file empty
        with open(saves_file, 'w') as f:
            f.write('')

    return

# function that lists all the entries in the saves.csv file
def list_entries() -> dict[str, str]:
    if not utils.check_saves_dir():
        return {}

    saves_file = os.path.join(utils.QUICKCD_DIR, 'saves.csv')
    with open(saves_file, 'r') as f:
        lines = f.readlines()

    entries = {}
    for line in lines:
        name, path = line.split(',')
        entries[name] = path.strip()
    
    return entries

# function that adds a new entry to the saves.csv file
def add_entry(name: str, path: str) -> bool:
    if not utils.check_saves_dir():
        utils.create_saves_dir()

    # Check if the entry already exists
    entries = list_entries()
    if name in entries:
        return False

    saves_file = os.path.join(utils.QUICKCD_DIR, 'saves.csv')
    with open(saves_file, 'a') as f:
        f.write(f'{name},{path}\n')

    return True

# function that removes an entry from the saves.csv file
def remove_entry(name: str) -> bool:
    if not utils.check_saves_dir():
        return False

    saves_file = os.path.join(utils.QUICKCD_DIR, 'saves.csv')
    with open(saves_file, 'r') as f:
        lines = f.readlines()

    found = False
    with open(saves_file, 'w') as f:
        for line in lines:
            if line.split(',')[0] != name:
                f.write(line)
            else:
                found = True

    if not found:
        return False
    
    return True

# function that changes the current working directory to the path of the entry
def change_to_entry(name: str) -> bool:
    if not utils.check_saves_dir():
        return False

    entries = list_entries()
    if name not in entries:
        return False

    utils.change_cwd(entries[name])
    return True