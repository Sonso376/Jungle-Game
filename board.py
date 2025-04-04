from piece import get_pieces

class Board:
    def __init__(self):
        self.cols = 8
        self.rows = 10
        self.board = [['_' for _ in range(self.cols)] for _ in range(self.rows)]
        self._river() 
        self._traps()
        self._dens()
        self.pieces = get_pieces()
        self._initialize_board()
        self._place_pieces()

    def _initialize_board(self):
        col_labels = [" ", 'A', 'B', 'C', 'D', 'E', 'F', 'G']
        for c in range(self.cols):
            self.board[0][c] = col_labels[c]
        for r in range(1, self.rows):
            self.board[r][0] = str((r-1) + 1)

    def _river(self):
        river_positions = {(4, 2), (4, 3), (4, 5), (4, 6),
                           (5, 2), (5, 3), (5, 5), (5, 6),
                           (6, 2), (6, 3), (6, 5), (6, 6)}
        for r, c in river_positions:
            self.board[r][c] = '~'
        
    def _traps(self):
        traps = {
            (1, 3), (2,4), (1, 5),
            (9, 3), (8, 4), (9, 5)
        }
        for r, c in traps:
            self.board[r][c] = '%'
        
    def _dens(self):
        dens = {(1, 4), (9, 4)}
        for r, c in dens:
            self.board[r][c] = '&'
    
    def _place_pieces(self):
        self.board = [['_' for _ in range(self.cols)] for _ in range(self.rows)]
        self._initialize_board()
        self._river()
        self._traps()
        self._dens()

        for player in self.pieces.values():
            for piece in player:
                if piece.state != "Dead":
                    r, c = piece.position
                    self.board[r][c] = piece.get_colored_model()

    def display(self):
        for row in self.board:
            print(' '.join(row))

board = Board()
board.display()