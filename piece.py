# pieces.py
from colorama import Back, Style

YELLOW_SCORE = 0
MAGENTA_SCORE = 0

class Piece:
    """Represents a piece in the Jungle (Dou Shou Qi) game."""

    def __init__(self, name: str, model_str: str, position: tuple, rank: int, movement: int, side: str):
        self.name = name
        self.model_str = model_str
        self.position = position
        self.rank = rank
        self.movement = movement
        self.side = side
        self.state = True  # True means the piece is active, False means it is captured

    def move(self, new_position: tuple, board):
        x0, y0 = self.position
        x1, y1 = new_position

        if not (1 <= x1 < len(board.layout) and 1 <= y1 < len(board.layout[0])):
            print(f"Invalid move! {self.name} tried to move out of the board.")
            return False
        if (abs(x1 - x0) == 1 and abs(y1 - y0) == 1) or abs(x1 - x0) > 1 or abs(y1 - y0) > 1:
            valido=False
            if Piece.name in ["Lion","Tiger"] and new_position=="_" and new_position!=self.position and (x0-x1==0 or y0-y1==0):
                xa=min(x0,x1)
                xb=max(x0,x1)
                ya=min(y0,y1)
                yb=max(y0,y1)
                for x in range(xa,xb+1):
                    for y in range(ya,yb+1):
                        position=(x,y)
                        if position!=self.position and position!=new_position:
                            if position=="~":
                                valido=True
                            else:
                                if x==xa+1 or x==xb or y==ya+1 or y==yb:
                                    print(f"Invalid move! {self.name} can only jump from one margin to another")
                                else:
                                    print(f"invalid move! There was land on the way of the jump")
                                return False
            if not valido:           
                print(f"Invalid move! {self.name} tried to move more than one space, to the same space or diagonally")
                return False
        
        # Check the type of terrain at the new position
        target_terrain = board.layout[x1][y1]

        # Movement rules
        
        if target_terrain == '~' and Piece.name != "Rat":
            print("Movimento inválido: Apenas o rato pode entrar no rio!")
            return False

        # Leão e Tigre podem saltar o rio
        if target_terrain == '~' and Piece.name in ["Lion", "Tiger"]:
            print("Movimento inválido: Leão e Tigre só podem saltar o rio se estiverem na margem!")
            return False

        # Restrições de tocas
        if new_position == (1, 4) and Piece.side == "YELLOW":
            print("Movimento inválido: Não pode entrar na própria toca!")
            return False
        if  new_position == (9, 4) and Piece.side == "MAGENTA" :
            print("Movimento inválido: Não pode entrar na própria toca!")
            return False

        # If all checks pass, move the piece
        board.pieces.pop(self.position, None)  # Remove from the old position
        self.position = new_position
        board.pieces[self.position] = self  # Update to the new position
        print(f"{self.name} ({self.side}) moved to {new_position}")

        return True

    def get_colored_model(self):
                #Returns the colored model for display, unless the piece is captured.
                if not self.state:  # If the piece is captured, do not display it
                    return " "

                if self.side == "YELLOW":
                    return f"{Back.YELLOW}{self.model_str}{Style.RESET_ALL}"
                elif self.side == "MAGENTA":
                    return f"{Back.MAGENTA}{self.model_str}{Style.RESET_ALL}"
                return self.model_str


"""
    def move(self, new_position: tuple, board):
        #move piece is still in play
        if not self.state:  # Check if the piece has been captured
            print(f"Invalid move! {self.name} has been captured and cannot be played.")
            return False

        x0, y0 = self.position
        x1, y1 = new_position


        y_dict = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}
        if y1 not in y_dict:
            print(f"Invalid move! Column '{y1}' is out of range. Use A-G.")
            return False
        y1 = y_dict[y1]

        if not (1 <= x1 <= len(board.layout) and 1 <= y1 <= len(board.layout[0])):
            print(f"Invalid move! {self.name} tried to move out of the board.")
            return False

        # Ensure valid movement (no diagonals, only one space unless jumping)
        if (abs(x1 - x0) == 1 and abs(y1 - y0) == 1) or abs(x1 - x0) > 1 or abs(y1 - y0) > 1:
            print(f"Invalid move! {self.name} tried to move more than one space, to the same space, or diagonally.")
            return False

        # Check the type of terrain at the new position
        target_terrain = board.layout[x1][y1]

        # Only Rat can enter water
        if self.name != "Rat" and target_terrain == '~':
            print("Invalid move: Only the Rat can enter the river!")
            return False

        # Lion and Tiger can jump over water, but only from correct positions
        if self.name in ["Lion", "Tiger"] and target_terrain == '~':
            if (x0, y0) in [(3, 2), (3, 4), (3, 6), (7, 2), (7, 4), (7, 6)]:  # Start jump positions
                if (x1, y1) in [(3, 6), (3, 2), (7, 6), (7, 2)]:  # Landing positions
                    print(f"{self.name} jumped over the river!")
                else:
                    print(f"Invalid move: {self.name} can only jump over water from specific positions!")
                    return False
            else:
                print(f"Invalid move: {self.name} can only jump over water from the riverbank!")
                return False

        # Cannot enter own den
        if self.side == "YELLOW" and new_position == (1, 4):
            print("Invalid move: You cannot enter your own den!")
            return False
        if self.side == "MAGENTA" and new_position == (9, 4):
            print("Invalid move: You cannot enter your own den!")
            return False

        # Move the piece
        board.pieces.pop(self.position, None)  # Remove from old position
        self.position = (x1, y1)  # Update position
        board.pieces[self.position] = self  # Place in new position
        print(f"{self.name} ({self.side}) moved to {new_position}")

        return True
 """
"""
        def can_capture(self, other_piece, board):
            #Checks if this piece can capture another piece and updates the game state accordingly.
            global YELLOW_SCORE, MAGENTA_SCORE  # Access global variables

            if not self.state:  # Check if the piece is already captured
                print(f"{self.name} has been captured and cannot capture other pieces.")
                return False

            # Rat can capture Elephant, but not in water
            if self.name == "Rat" and other_piece.name == "Elephant":
                if board.layout[self.position[0]][self.position[1]] == '~':  # If Rat is in water
                    print("Invalid capture: The Rat cannot capture the Elephant while in water!")
                    return False

            # General rule: Can only capture pieces of equal or lower rank
            if self.rank >= other_piece.rank:
                print(f"{self.name} captured {other_piece.name}!")

                # Update global scores
                if self.side == "YELLOW":
                    YELLOW_SCORE += other_piece.rank
                else:
                    MAGENTA_SCORE += other_piece.rank

                # Remove the captured piece from the board and mark as captured
                board.pieces.pop(other_piece.position, None)
                other_piece.state = False  # Mark piece as inactive
                return True

            print(f"{self.name} cannot capture {other_piece.name} due to lower rank!")
            return False
"""
   

def get_pieces():
    return {
        "YELLOW": [
            Piece("Elephant", "🐘", (3, 7), 8, 1, "YELLOW"),
            Piece("Lion", "🦁", (1, 1), 7, 2, "YELLOW"),
            Piece("Tiger", "🐯", (1, 7), 6, 2, "YELLOW"),
            Piece("Leopard", "🐆", (3, 3), 5, 1, "YELLOW"),
            Piece("Wolf", "🐺", (3, 5), 4, 1,"YELLOW"),
            Piece("Dog", "🐶", (2, 2), 3, 1,"YELLOW"),
            Piece("Cat", "🐱", (2, 6), 2, 1,"YELLOW"),
            Piece("Rat", "🐭", (3, 1), 1, 3,"YELLOW"),
        ],
        "MAGENTA": [
            Piece("Elephant", "🐘", (7, 1), 8, 1,"MAGENTA"),
            Piece("Lion", "🦁", (6, 7), 7, 2,"MAGENTA"),
            Piece("Tiger", "🐯", (9, 1), 6, 2,"MAGENTA"),
            Piece("Leopard", "🐆", (7, 5), 5, 1,"MAGENTA"),
            Piece("Wolf", "🐺", (7, 3), 4, 1,"MAGENTA"),
            Piece("Dog", "🐶", (8, 6), 3, 1,"MAGENTA"),
            Piece("Cat", "🐱", (8, 2), 2, 1,"MAGENTA"),
            Piece("Rat", "🐭", (7, 7), 1, 3,"MAGENTA"),
        ]
    }