import copy
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

    def clone(self):
        new_board = Board.__new__(Board)
        new_board.cols = self.cols
        new_board.rows = self.rows
        # Copia a matriz do tabuleiro (lista de listas)
        new_board.board = [row[:] for row in self.board]

        # Copia o dicionário de peças de forma customizada
        new_board.pieces = {}
        for key, pieces_list in self.pieces.items():
            new_list = []
            for piece in pieces_list:
                # Cria uma nova instância da peça com os atributos necessários
                new_piece = type(piece)(
                    piece.name,
                    piece.model_str,
                    piece.position,
                    piece.rank,
                    piece.movement,
                    piece.side
                )
                new_piece.hp = piece.hp
                new_piece.state = piece.state
                new_piece.color = piece.color
                new_list.append(new_piece)
            new_board.pieces[key] = new_list

        # Copia outros atributos que possam existir (como cores definidas para a IA, etc.)
        new_board.ai_color = getattr(self, 'ai_color', None)
        new_board.opponent_color = getattr(self, 'opponent_color', None)
        new_board.human_color = getattr(self, 'human_color', None)

        return new_board

    def make_move(self, piece, new_position):      # ?????
        # Cria uma cópia do tabuleiro
        new_board = self.clone()
        # Atualiza a posição da peça correspondente no novo tabuleiro.
        # Aqui, assumimos que cada peça tem um atributo 'color' para identificar a qual jogador pertence.
        for p in new_board.pieces[piece.color]:
            # Podemos identificar a peça por nome e posição atual
            if p.name == piece.name and p.position == piece.position:
                p.position = new_position
                break
        # Reposiciona as peças no tabuleiro (reconstrói o estado visual)
        new_board._place_pieces()
        return new_board

board = Board()
board.display()