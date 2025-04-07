import copy
from piece import get_pieces

class Board:
    """
    Classe que representa o tabuleiro do jogo.
    Gerencia o estado do tabuleiro, incluindo a posição das peças,
    rios, armadilhas e tocas.
    """
    def __init__(self):
        """
        Inicializa um novo tabuleiro com dimensões 8x10.
        Configura os elementos especiais (rios, armadilhas, tocas) e posiciona as peças.
        """
        self.cols = 8  # Número de colunas do tabuleiro
        self.rows = 10  # Número de linhas do tabuleiro
        self.board = [['_' for _ in range(self.cols)] for _ in range(self.rows)]  # Matriz que representa o tabuleiro
        self._river()  # Configura as posições dos rios
        self._traps()  # Configura as posições das armadilhas
        self._dens()   # Configura as posições das tocas
        self.pieces = get_pieces()  # Obtém as peças iniciais do jogo
        self._initialize_board()  # Inicializa o tabuleiro com rótulos
        self._place_pieces()  # Posiciona as peças no tabuleiro

    def _initialize_board(self):
        """
        Inicializa o tabuleiro com rótulos para as linhas e colunas.
        Colunas são rotuladas de A a G e linhas de 1 a 9.
        """
        col_labels = [" ", 'A', 'B', 'C', 'D', 'E', 'F', 'G']
        for c in range(self.cols):
            self.board[0][c] = col_labels[c]
        for r in range(1, self.rows):
            self.board[r][0] = str((r-1) + 1)

    def _river(self):
        """
        Define as posições dos rios no tabuleiro (representados por '~').
        Os rios são áreas especiais que apenas certas peças podem atravessar.
        """
        river_positions = {(4, 2), (4, 3), (4, 5), (4, 6),
                           (5, 2), (5, 3), (5, 5), (5, 6),
                           (6, 2), (6, 3), (6, 5), (6, 6)}
        for r, c in river_positions:
            self.board[r][c] = '~'
        
    def _traps(self):
        """
        Define as posições das armadilhas no tabuleiro (representadas por '%').
        As armadilhas enfraquecem as peças adversárias que entram nelas.
        """
        traps = {
            (1, 3), (2,4), (1, 5),  # Armadilhas próximas à toca do Player1
            (9, 3), (8, 4), (9, 5)  # Armadilhas próximas à toca do Player2
        }
        for r, c in traps:
            self.board[r][c] = '%'
        
    def _dens(self):
        """
        Define as posições das tocas no tabuleiro (representadas por '&').
        O objetivo do jogo é alcançar a toca do adversário.
        """
        dens = {(1, 4), (9, 4)}  # Tocas dos jogadores 1 e 2
        for r, c in dens:
            self.board[r][c] = '&'
    
    def _place_pieces(self):
        """
        Posiciona todas as peças no tabuleiro de acordo com suas posições atuais.
        Recria o tabuleiro e depois coloca cada peça viva em sua posição.
        """
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
        """
        Exibe o estado atual do tabuleiro no console.
        """
        for row in self.board:
            print(' '.join(row))

    def clone(self):
        """
        Cria uma cópia profunda do tabuleiro atual, incluindo todas as peças
        e seus estados. Usado para simular movimentos sem afetar o tabuleiro original.
        
        Returns:
            Board: Uma nova instância de Board com o mesmo estado que a atual
        """
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

    def make_move(self, piece, new_position):
        """
        Cria uma nova instância do tabuleiro com o movimento aplicado.
        
        Args:
            piece (Piece): A peça que será movida
            new_position (tuple): A nova posição (linha, coluna) para a peça
        
        Returns:
            Board: Um novo tabuleiro com o movimento aplicado
        """
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

# Se este arquivo for executado diretamente, cria e exibe um tabuleiro
board = Board()
board.display()