import argparse

from . import utils
from . import xy
from . import stats

def main():
    parser = argparse.ArgumentParser(
        description="Plot data from a file.",
        prog="quickplot",
        epilog="Created by Pedro Juan Royo @UnstrayCato"
    )

    parser.add_argument(
        "--version", "-v", action="version", version="%(prog)s v0.9.0"
    )

    # Sub-parser for the "plot" command
    subparser = parser.add_subparsers()
    plot_xy_parser = subparser.add_parser(
        "xy", help="Plot x-y data",
        epilog="Created by Pedro Juan Royo @UnstrayCato"
    )
    plot_xy_parser.set_defaults(which="xy")

    plot_xy_parser.add_argument(
        "filename", type=str, help="The data file to plot"
    )
    plot_xy_parser.add_argument(
        "--all", "-a", action="store_true",
        help="Plot all columns against the defined x column"
    )
    normalisation_types = [n.name for n in utils.Normalisation]
    plot_xy_parser.add_argument(
        "--normalise", "-n", type=str, 
        choices=normalisation_types, 
        default=utils.Normalisation.NONE.name,
        help="""
        Normalise the data. Choices are:
        (Default) NONE: No normalisation. 
        STANDARD: Standard normalisation
        ZERO_ONE: Normalise to the range [0, 1]
        """
    )
    plot_xy_parser.add_argument(
        "--xcol", "-x", type=int, default=0, 
        help="The column containing x values, index starts at 0. Default is 0"
    )
    plot_xy_parser.add_argument(
        "--ycol", "-y", type=int, default=1, 
        help="The column containing y values, index starts at 0. Default is 1"
    )
    plot_xy_parser.add_argument(
        "--separator", "-s", type=str, default=" ", 
        help="The separator between columns, default is (space)"
    )
    plot_xy_parser.add_argument(
        "--line", "-l", type=str, default='-', 
        help="Line type, default is solid line (-)"
    )
    math_locs = [n.name for n in utils.MathLocs]
    plot_xy_parser.add_argument(
        "--math-loc", "-m", type=str, 
        choices=math_locs, 
        default=utils.MathLocs.X.name,
        help="""
        Where to apply the mathematical transformation. Choices are:
        (Default) X: x-axis only.
        Y: y-axis only
        BOTH: x and y axes
        """
    )
    plot_xy_parser.add_argument(
        "--math-exp", "-M", type=str, default='#', 
        help="""
        The mathematical expression. In the format: {+,-,*,/,^}|{num},...
        {num} can use the special values: MAX, MIN, MEAN, STD
        """
    )

    # Sub-parser for the "plot" command
    plot_stats_parser = subparser.add_parser(
        "stats", help="Violin plot of the data",
        epilog="Created by Pedro Juan Royo @UnstrayCato"
    )
    plot_stats_parser.set_defaults(which="stats")

    plot_stats_parser.add_argument(
        "filename", type=str, help="The data file to plot"
    )
    plot_stats_parser.add_argument(
        "--col", "-c", type=int, default=-1, 
        help="The column to plot starting from 0, default is all columns (-1)"
    )

    args = parser.parse_args()

    if args.which == "xy":
        math_exp = None if args.math_exp == "#" else args.math_exp
        try:
            xy.plot_xy(args.filename, plot_all=args.all, xcol=args.xcol, 
                       ycol=args.ycol, sep=args.separator, line_type=args.line, 
                       normalise=utils.Normalisation[args.normalise],
                       mathematical_expression_location=utils.MathLocs[args.math_loc],
                       mathematical_expression=math_exp)
        except FileNotFoundError as e:
            print(f"FILE NOT FOUND. Filename: {e.filename}")
            exit(1)
        except IndexError as e:
            print(f"INDEX ERROR. Column: {e.args[0]}")
            exit(2)
        except ValueError as e:
            print(f"VALUE ERROR. {e.args[0]}")
            exit(3)
    elif args.which == "stats":
        try:
            stats.violin_plot(args.filename, args.col)
        except FileNotFoundError as e:
            print(f"FILE NOT FOUND. Filename: {e.filename}")
            exit(1)
        except IndexError as e:
            print(f"INDEX ERROR. Column: {e.args[0]}")
            exit(2)

if __name__ == "__main__":
    main()