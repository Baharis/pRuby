import os
import argparse
from uncertainties import ufloat_fromstr
from pruby.constants import R1_0, T_0
from pruby.strategy import Strategy
from pruby import PressureCalculator


class PRubyParser(argparse.ArgumentParser):
    pass

    def add_strategy_argument(self, shortname, longname, strategy_list, help):
        name_list = [s.name for s in strategy_list]
        name_default = name_list[0]
        self.add_argument(shortname, longname, choices=name_list,
                          default=name_default, type=str, help=help)


class PRubyHelpFormatter(argparse.HelpFormatter):
    """Credits to https://stackoverflow.com/questions/18275023"""
    def __init__(self, prog):
        super().__init__(prog, max_help_position=20, width=80)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string


parser = PRubyParser(formatter_class=lambda prog: PRubyHelpFormatter(prog))
parser.add_argument('input',
                    help='Value of R1 in nm OR ruby spectrum filepath')
parser.add_argument('-t', '--temp', default=str(T_0-273.15),
                    help='Sample temperature in \u00B0C')
parser.add_argument('-d', '--draw', action='store_true',
                    help='Should spectrum be drawn on exit?')
parser.add_argument('-r', '--ref', default=str(R1_0),
                    help='Reference R1 in nm OR ref. spectrum filepath')
parser.add_argument('-s', '--reftemp', default=str(T_0-273.15),
                    help='Reference temperature in \u00B0C')

parser.add_strategy_argument('-R', '--readers', Strategy.readers,
                             help='Strategy for reading the spectrum file')
parser.add_strategy_argument('-B', '--backfitter', Strategy.backfitters,
                             help='Strategy for fitting the background')
parser.add_strategy_argument('-P', '--peakfitter', Strategy.peakfitters,
                             help='Strategy for fitting spectrum peaks')
parser.add_strategy_argument('-C', '--corrector', Strategy.correctors,
                            help='Strategy for applying temperature correction')
parser.add_strategy_argument('-T', '--translator', Strategy.translators,
                             help='Strategy for translating R1 to pressure')
parser.add_strategy_argument('-D', '--drawer', Strategy.drawers,
                             help='Strategy for drawing the spectrum')
args = parser.parse_args()


def reformat_r1_or_filepath(value):
    is_filepath = False
    if os.path.isfile(value):
        value = str(value)
        is_filepath = True
    else:
        try:
            value = ufloat_fromstr(value)
        except ValueError:
            parser.error('input should be either numeric (R1) or string (path)')
    return value, is_filepath


calc = PressureCalculator()
calc.strategy.set(reading=args.readers, backfitting=args.backfitter,
                  peakfitting=args.peakfitter, correcting=args.corrector,
                  translating=args.translator, drawing=args.drawer)
# TODO REFERENCE: calculate_offset()
ref_, ref_is_filepath = reformat_r1_or_filepath(args.ref)
if ref_is_filepath:
    calc.filename = ref_
    calc.read_and_fit()
else:
    calc.r1 = ref_
calc.t = ufloat_fromstr(args.reftemp) + 273.15
calc.calculate_p_from_r1()
calc.set_current_as_reference()
calc.calculate_offset_from_reference()
input_, input_is_filepath = reformat_r1_or_filepath(args.input)
if input_is_filepath:
    calc.filename = input_
    calc.read_and_fit()
else:
    calc.r1 = input_
calc.t = ufloat_fromstr(args.temp) + 273.15
calc.calculate_p_from_r1()
print('R1: {0:.2uS}'.format(calc.r1))
print('T: {0:.2uS}'.format(calc.t))
print('p: {0:.2uS}'.format(calc.p))
if args.draw:
    calc.draw()

