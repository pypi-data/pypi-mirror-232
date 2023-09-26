# Console
# ################
USE_COLORS = False
ANSI_START = '\033['
ANSI_END = 'm'

COLOR_MAPPING = { 
    'black': 0,
    'red': 1,
    'green': 2,
    'yellow': 3,
    'blue': 4,
    'magenta': 5,
    'cyan': 6,
    'white': 7
} 

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class color_numbers:
    RESET = 0
    BOLD = 1
    UNDERLINE = 4
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35 
    CYAN = 36
    WHITE = 37
    BGBLACK = 40
    BGRED = 41
    BGGREEN = 42
    BGYELLOW = 43
    BGBLUE = 44
    BGMAGENTA = 45 
    BGCYAN = 46
    BGWHITE = 47

class Console:
    _instance = None
    def __new__(cls, use_colors=USE_COLORS):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.use_colors = use_colors
        return cls._instance

    #Dynamically tur on/off console colors
    def set_colors(self, use_colors=False):
        self.use_colors = use_colors

    def is_colors(self):
        return self.use_colors
    
    def bgcolor(self, color='black'):
        return COLOR_MAPPING.get(color.lower(), 0) + 40
    
    def fgcolor(self, color='white'):
        return COLOR_MAPPING.get(color.lower(), 7) + 30

    def print(self, message:str, fgcolor:str=None, bgcolor:str=None, bold:bool=False, underline:bool=False):
        start_string=""
        end_string=""
        if self.use_colors:
            if bold:
                start_string += (";" if len(start_string) > 0 else "") + str(color_numbers.BOLD)
            if underline:
                start_string += (";" if len(start_string) > 0 else "") + str(color_numbers.UNDERLINE)
            if fgcolor is not None:
                start_string += (";" if len(start_string) > 0 else "") + str(self.fgcolor(fgcolor))
            if bgcolor is not None:
                start_string += (";" if len(start_string) > 0 else "") + str(self.bgcolor(bgcolor))
            start_string = f"{ANSI_START}{start_string}{ANSI_END}" if len(start_string) > 0 else ""
            end_string = f"{ANSI_START}{color_numbers.RESET}{ANSI_END}"
        print(f"{start_string}{message}{end_string}")

    def red(self, message, bold=False, underline=False):
        self.print(message=message, fgcolor='red', bold=bold, underline=underline)
    def black_on_red(self, message, bold=False, underline=False):
        self.print(message=message, fgcolor='black', bgcolor='red', bold=bold, underline=underline)
    def yellow(self, message, bold=False, underline=False):
        self.print(message=message, fgcolor='yellow', bold=bold, underline=underline)
    def green(self, message, bold=False, underline=False):
        self.print(message=message, fgcolor='green', bold=bold, underline=underline)
    def blue(self, message, bold=False, underline=False):
        self.print(message=message, fgcolor='blue', bold=bold, underline=underline)

    def critical(self, message):
        self.print(message=message, fgcolor='white', bgcolor='red', bold=True, underline=False)
    def error(self, message):
        self.print(message=message, fgcolor='red', bold=True, underline=False)
    def warning(self, message):
        self.print(message=message, fgcolor='yellow', bold=True, underline=False)
    def debug(self, message):
        self.print(message=message, fgcolor='cyan', bold=False, underline=False)
    def info(self, message):
        self.print(message=message, fgcolor='blue', bold=False, underline=False)
