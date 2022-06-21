from pruby.cli import Application
from pruby.constants import R1_0, T_0
from pruby.strategy import Strategy
from pruby.cli import PRubyArgumentParser, PRubyHelpFormatter


# MAIN PROGRAM
if __name__ == '__main__':
    def formatter(prog):
        return PRubyHelpFormatter(prog)

    p = PRubyArgumentParser(formatter_class=formatter)
    p.add_argument('input',
                   help='Value of R1 in nm OR ruby spectrum filepath')
    p.add_argument('-t', '--temp', default=str(T_0 - 273.15),
                   help='Sample temperature in \u00B0C')
    p.add_argument('-d', '--draw', action='store_true',
                   help='Should spectrum be drawn on exit?')
    p.add_argument('-r', '--ref', default=str(R1_0),
                   help='Reference R1 in nm OR ref. spectrum filepath')
    p.add_argument('-s', '--reftemp', default=str(T_0 - 273.15),
                   help='Reference temperature in \u00B0C')

    p.add_strategy_argument('-R', '--readers', Strategy.readers,
                            help='Strategy for reading the spectrum file')
    p.add_strategy_argument('-B', '--backfitter', Strategy.backfitters,
                            help='Strategy for fitting the background')
    p.add_strategy_argument('-P', '--peakfitter', Strategy.peakfitters,
                            help='Strategy for fitting spectrum peaks')
    p.add_strategy_argument('-C', '--corrector', Strategy.correctors,
                            help='Strategy for applying temperature correction')
    p.add_strategy_argument('-T', '--translator', Strategy.translators,
                            help='Strategy for translating R1 to pressure')
    p.add_strategy_argument('-D', '--drawer', Strategy.drawers,
                            help='Strategy for drawing the spectrum')

    Application(parser=p).run()


