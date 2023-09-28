import argparse

from . import xy

def main():
    parser = argparse.ArgumentParser(
        description="Plot data from a file.",
        prog="quickplot"
    )

    # Sub-parser for the "plot" command
    subparser = parser.add_subparsers()
    plot_xy_parser = subparser.add_parser(
        "xy", help="Plot x-y data"
    )
    plot_xy_parser.set_defaults(which="xy")

    plot_xy_parser.add_argument(
        "filename", type=str, help="The data file to plot"
    )
    plot_xy_parser.add_argument(
        "--xcol", "-x", type=int, default=0, 
        help="The column containing x values, index starts at 0"
    )
    plot_xy_parser.add_argument(
        "--ycol", "-y", type=int, default=1, 
        help="The column containing y values, index starts at 0"
    )

    args = parser.parse_args()

    if args.which == "xy":
        try:
            xy.plot_xy(args.filename, args.xcol, args.ycol)
        except FileNotFoundError as e:
            print(f"FILE NOT FOUND. Filename: {e.filename}")
            exit(1)
        except IndexError as e:
            print(f"INDEX ERROR. Column: {e.args[0]}")
            exit(2)

if __name__ == "__main__":
    main()