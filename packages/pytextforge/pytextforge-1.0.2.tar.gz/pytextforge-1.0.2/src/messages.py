import shutil
import sys

from colorama import Fore, Back, init

class MessageManager():

    def __init__(self) -> None:
        self.__verbose = 0
        self.__columns, _ = shutil.get_terminal_size((80, 20))
        init(autoreset=True)
    
    @property
    def verbose(self) -> int:
        return self.__verbose
    
    @verbose.setter
    def verbose(self, value: int) -> None:
        self.__verbose = value

    @property
    def columns(self) -> int:
        return self.__columns
    
    def show_banner(self, version: str) -> None:
        p = ' ' * (self.columns // 2 - 27)
        print()
        print(f'{Fore.LIGHTMAGENTA_EX}{p} _____    _______        _   ______')
        print(f'{Fore.LIGHTMAGENTA_EX}{p}|  __ \  |__   __|      | | |  ____|')
        print(f'{Fore.LIGHTMAGENTA_EX}{p}| |__) |   _| | _____  _| |_| |__ ___  _ __ __ _  ___')
        print(f"{Fore.LIGHTMAGENTA_EX}{p}|  ___/ | | | |/ _ \ \/ / __|  __/ _ \| '__/ _` |/ _ \\")
        print(f'{Fore.LIGHTMAGENTA_EX}{p}| |   | |_| | |  __/>  <| |_| | | (_) | | | (_| |  __/')
        print(f'{Fore.LIGHTMAGENTA_EX}{p}|_|    \__, |_|\___/_/\_\\\\__|_|  \___/|_|  \__, |\___|')
        print(f'{Fore.LIGHTMAGENTA_EX}{p}        __/ |          ---(),*              __/ |')
        print(f'{Fore.LIGHTMAGENTA_EX}{p}       |___/            <####^^            |___/')
        print(f'{Fore.LIGHTMAGENTA_EX}{p}                          /\\                    {version}')
        print()
    
    def show_failure(self) -> None:
        print()
        self.show_title_line(title='Failure', corner=' ', line=' ', colortext=f'{Fore.RED}')
        print()
    
    def show_success(self) -> None:
        print()
        self.show_title_line(title='Success', corner=' ', line=' ', colortext=f'{Fore.GREEN}')
        print()

    def show_line(self, line: str='-', corner: str='#') -> None:
        self.show_title_line(title='', line=line, corner=corner)

    def show_title_line(self, title: str='', line: str='-', corner: str='#', \
                        colorline: str=f'{Fore.CYAN}', colortext: str=f'{Fore.LIGHTCYAN_EX}') -> None:
        t = len(title)
        if t >= self.columns:
            print(f'{colorline}{title}')
        else:
            r = l = (self.columns - t - 2) // 2
            if l + r + 2 + t < (self.columns):
                l += 1
            print(f'{colorline}{corner[0]}', end='')
            print(f'{colorline}{line[0] * l}', end='')
            print(f'{colortext}{title}', end='')
            print(f'{colorline}{line[0] * r}', end='')
            print(f'{colorline}{corner[0]}')

    def show_verbose(self, msg: str, level: int=1) -> None:
        if self.verbose < level:
            return
        print(f'{Fore.YELLOW}{Back.BLACK}VERBOSE: {msg}')

    def show_error(self, msg: str) -> None:
        print(f'{Fore.LIGHTRED_EX}{msg}', file=sys.stderr)

    def show_message(self, msg: str) -> None:
        print(f'{msg}')