"""Banner and custom help action for RunnerScript"""

import argparse
import colorama

ASCII_BANNER = r"""
    ____                                 _____           _       __ 
   / __ \__  ______  ____  ___  _____   / ___/__________(_)___  / /_
  / /_/ / / / / __ \/ __ \/ _ \/ ___/   \__ \/ ___/ ___/ / __ \/ __/
 / _, _/ /_/ / / / / / / /  __/ /      ___/ / /__/ /  / / /_/ / /_  
/_/ |_|\__,_/_/ /_/_/ /_/\___/_/      /____/\___/_/  /_/ .___/\__/  
                                                      /_/           
"""


class BannerHelpAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        colorama.init(autoreset=True)
        parser.print_help()
        parser.exit()


def print_banner():
    """Print the ASCII banner to console"""
    colorama.init(autoreset=True)
    print(colorama.Fore.CYAN + ASCII_BANNER)
