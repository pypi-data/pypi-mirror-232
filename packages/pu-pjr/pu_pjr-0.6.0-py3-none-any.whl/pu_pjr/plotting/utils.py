import pandas as pd

# Load to a pandas dataframe from a file
def load_data(filename: str, sep: str=' ', comment: str='#'):
    df = pd.read_csv(filename, sep=sep, comment=comment, header=None)
    return df