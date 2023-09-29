from matplotlib import pyplot as plt
from . import utils

# Plotting x-y data from files
def plot_xy(
        filename: str, xcol: int=0, ycol: int=1, sep: str=' ', 
        testing: bool = False, **kwargs
        ):
    df = utils.load_data(filename, sep=sep)
    x = df.iloc[:, xcol]
    y = df.iloc[:, ycol]
    plt.plot(x, y, **kwargs)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(filename)
    plt.grid()
    plt.show(block=not testing)
    
    return