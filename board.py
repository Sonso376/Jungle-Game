from piece import get_pieces
import copy

class Board:
    def __init__(self):
        self.cols = 8
        self.rows = 10
        self.board = [['_' for _ in range(self.cols)] for _ in range(self.rows)]
        self._initialize_special_cells()
        self.pieces = get_pieces()
        self._initialize_board()
        self._place_pieces()
        self.piece_hash = self._create_piece_hash()  # For fast piece lookup
        
    def _initialize_special_cells(self):
        # Combine river, traps, and dens setup for fewer iterations
        self._initialize_board()
        
        # River
        river_positions = {(4, 2), (4, 3), (4, 5), (4, 6),
                           (5, 2), (5, 3), (5, 5), (5, 6),
                           (6, 2), (6, 3), (6, 5), (6, 6)}
        for r, c in river_positions:
            self.board[r][c] = '~'
        
        # Traps
        traps = {(1, 3), (2, 4), (1, 5), (9, 3), (8, 4), (9, 5)}
        for r, c in traps:
            self.board[r][c] = '%'
        
        # Dens
        dens = {(1, 4), (9, 4)}
        for r, c in dens:
            self.board[r][c] = '&'

    def _initialize_board(self):
        col_labels = [" ", 'A', 'B', 'C', 'D', 'E', 'F', 'G']
        for c in range(self.cols):
            self.board[0][c] = col_labels[c]
        for r in range(1, self.rows):
            self.board[r][0] = str(r)
    
    def _create_piece_hash(self):
        # Create a dictionary for O(1) lookup of pieces by position
        piece_hash = {}
        for color, pieces in self.pieces.items():
            for piece in pieces:
                if piece.state != "Dead":
                    piece_hash[piece.position] = piece
        return piece_hash

    def _place_pieces(self):
        self.board = [['_' for _ in range(self.cols)] for _ in range(self.rows)]
        self._initialize_special_cells()

        for player in self.pieces.values():
            for piece in player:
                if piece.state != "Dead":
                    r, c = piece.position
                    self.board[r][c] = piece.get_colored_model()
        
        # Update piece hash after placing pieces
        self.piece_hash = self._create_piece_hash()

    def display(self):
        for row in self.board:
            print(' '.join(row))

    def clone(self):
        # More efficient cloning by only copying necessary structures
        new_board = Board.__new__(Board)  # Create instance without calling __init__
        new_board.cols = self.cols
        new_board.rows = self.rows
        new_board.board = [row[:] for row in self.board]  # Shallow copy of board array
        
        # Deep copy of pieces dictionary
        new_board.pieces = {
            color: [copy.deepcopy(piece) for piece in pieces]
            for color, pieces in self.pieces.items()
        }
        
        # Copy attributes that might have been added
        if hasattr(self, 'ai_color'):
            new_board.ai_color = self.ai_color
        if hasattr(self, 'human_color'):
            new_board.human_color = self.human_color
        if hasattr(self, 'opponent_color'):
            new_board.opponent_color = self.opponent_color
            
        # Create piece hash for the new board
        new_board.piece_hash = new_board._create_piece_hash()
        
        return new_board

    def make_move(self, piece, new_position):
        # Create a copy of the board for the new state
        new_board = self.clone()
        
        # Find and update the piece in the new board
        for p in new_board.pieces[piece.color]:
            if p.name == piece.name and p.position == piece.position:
                # Check if we're capturing an opponent's piece
                if new_position in new_board.piece_hash:
                    captured_piece = new_board.piece_hash[new_position]
                    if captured_piece.color != p.color:
                        # Mark the captured piece as dead
                        for op in new_board.pieces[captured_piece.color]:
                            if op.position == new_position:
                                op.state = "Dead"
                                break
                
                # Update piece position
                p.position = new_position
                break
                
        # Update the new board's visual representation
        new_board._place_pieces()
        return new_board
        
    def get_piece_at(self, position):
        # O(1) lookup of piece at a position
        return self.piece_hash.get(position, None)