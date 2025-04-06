# pieces.py
from colorama import Back, Style

class Piece:
    def __init__(self, name: str, model_str: str, position: tuple, rank: int, movement: int, side: str):
        self.name = name
        self.model_str = model_str
        self.position = position
        self.rank = rank
        self.movement = movement
        self.side = side
        self.hp = rank
        self.state = "Alive" #alive, under attack, can attack, dead
        self.color = "YELLOW" if self.side == "Player1" else "MAGENTA"

    def get_colored_model(self):
                    if not self.state: 
                        return " "

                    if self.side == "Player1":
                        return f"{Back.YELLOW}{self.model_str}{Style.RESET_ALL}"
                    elif self.side == "Player2":
                        return f"{Back.MAGENTA}{self.model_str}{Style.RESET_ALL}"
                    return self.model_str

def get_pieces():
    return {
        "YELLOW": [
            Piece("Elephant", "🐘", (3, 7), 8, 1, "Player1"),
            Piece("Lion", "🦁", (1, 1), 7, 2, "Player1"),
            Piece("Tiger", "🐯", (1, 7), 6, 2, "Player1"),
            Piece("Leopard", "🐆", (3, 3), 5, 1, "Player1"),
            Piece("Wolf", "🐺", (3, 5), 4, 1,"Player1"),
            Piece("Dog", "🐶", (2, 2), 3, 1,"Player1"),
            Piece("Cat", "🐱", (2, 6), 2, 1,"Player1"),
            Piece("Rat", "🐭", (3, 1), 1, 3,"Player1"),
        ],
        "MAGENTA": [
            Piece("Elephant", "🐘", (7, 1), 8, 1,"Player2"),
            Piece("Lion", "🦁", (6, 7), 7, 2,"Player2"), #7,9
            Piece("Tiger", "🐯", (9, 1), 6, 2,"Player2"),
            Piece("Leopard", "🐆", (7, 5), 5, 1,"Player2"),
            Piece("Wolf", "🐺", (7, 3), 4, 1,"Player2"),
            Piece("Dog", "🐶", (8, 6), 3, 1,"Player2"),
            Piece("Cat", "🐱", (8, 2), 2, 1,"Player2"),
            Piece("Rat", "🐭", (6, 6), 1, 3,"Player2"),#7, 7
        ]
    }