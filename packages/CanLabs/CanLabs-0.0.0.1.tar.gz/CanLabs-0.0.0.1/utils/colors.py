from colorama import Fore, Back, Style

class TerminalColors:
    RESET = Style.RESET_ALL

    # Texte coloré
    BLACK = Fore.BLACK
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE

    # Fond coloré
    BLACK_BG = Back.BLACK
    RED_BG = Back.RED
    GREEN_BG = Back.GREEN
    YELLOW_BG = Back.YELLOW
    BLUE_BG = Back.BLUE
    MAGENTA_BG = Back.MAGENTA
    CYAN_BG = Back.CYAN
    WHITE_BG = Back.WHITE

    # Styles de texte
    BOLD = Style.BRIGHT
    DIM = Style.DIM
    UNDERLINE = Style.BRIGHT


if __name__ == "__main__":
    # Exemple d'utilisation des couleurs
    print(TerminalColors.RED + "Texte rouge" + TerminalColors.RESET)
    print(TerminalColors.GREEN_BG + TerminalColors.BLACK + "Fond vert, texte noir" + TerminalColors.RESET)
