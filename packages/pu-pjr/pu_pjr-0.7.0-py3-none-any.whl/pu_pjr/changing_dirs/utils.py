import os

# Get the home directory
def get_home_dir() -> str:
    return os.path.expanduser('~')

QUICKCD_DIR = os.path.join(get_home_dir(), '.quickcd')

# Get the current working directory
def get_cwd() -> str:
    return os.getcwd()

# Change the current working directory
def change_cwd(path: str):
    os.chdir(path)
    os.system('exec zsh') # Create a new shell to update the prompt
    return

# Check if the home directory has a .quickcd/ directory
def check_saves_dir() -> bool:
    saves_dir = QUICKCD_DIR
    return os.path.isdir(saves_dir)

# Create a .quickcd/ directory in the home directory
def create_saves_dir():
    saves_dir = QUICKCD_DIR
    os.mkdir(saves_dir)
    return

