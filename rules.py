from piece import Piece
from board import Board

class Rules:
    """
    Classe que implementa as regras do jogo, incluindo movimentos válidos,
    capturas e condições de vitória.
    """
    def __init__(self, board):
        """
        Inicializa o objeto de regras com um tabuleiro.
        
        Args:
            board (Board): O tabuleiro do jogo
        """
        self.board = board

    def move(self, piece: Piece) -> list:
        """
        Calcula todos os movimentos possíveis para uma peça.
        
        Args:
            piece (Piece): A peça para a qual calcular os movimentos
            
        Returns:
            list: Lista de tuplas (linha, coluna) representando posições válidas para movimento
        """
        possible_moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Direções possíveis: baixo, cima, direita, esquerda
        r, c = piece.position
        piece.state = "Alive"  # Reseta o estado da peça para "Alive"

        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc

            if 1 <= new_r < self.board.rows and 1 <= new_c < self.board.cols:
                target_cell = self.board.board[new_r][new_c]

                # Uma peça não pode entrar na sua própria toca
                if (piece.side == "Player1" and (new_r, new_c) == (1, 4)) or \
                   (piece.side == "Player2" and (new_r, new_c) == (9, 4)):
                    continue

                # Regras especiais para Leões e Tigres (salto sobre o rio)
                if piece.name in ["Lion", "Tiger"]:
                    jump_r, jump_c = r + dr, c + dc
                    rat_in_the_way = False
                    
                    # Continua na direção enquanto estiver sobre o rio
                    while (1 <= jump_r < self.board.rows and 1 <= jump_c < self.board.cols and
                           self.board.board[jump_r][jump_c] == "~"):
                        # Verifica se há um rato bloqueando o caminho
                        for player_pieces in self.board.pieces.values():
                            for p in player_pieces:
                                if p.position == (jump_r, jump_c) and p.name == "Rat":
                                    rat_in_the_way = True
                        jump_r += dr
                        jump_c += dc

                    # Se chegou a uma posição válida após o rio e não há rato bloqueando
                    if (1 <= jump_r < self.board.rows and 1 <= jump_c < self.board.cols and
                        self.board.board[jump_r][jump_c] != "~" and not rat_in_the_way):

                        occupied = False
                        for player_pieces in self.board.pieces.values():
                            for p in player_pieces:
                                # Verifica apenas peças vivas (não mortas)
                                if p.position == (jump_r, jump_c) and p.state != "Dead":
                                    occupied = True
                                    # Verifica se pode capturar a peça nesta posição
                                    if self.can_captures(piece, p):
                                        possible_moves.append((jump_r, jump_c))
                                        piece.state = "can_attack"
                                        p.state = "under_attack"
                                    break
                        if not occupied:
                            possible_moves.append((jump_r, jump_c))
                        continue  # Pula o movimento normal se o salto foi tentado

                # Movimentos normais (ou Rato no rio)
                if piece.name == "Rat" or target_cell != "~":
                    occupied = False
                    for player_pieces in self.board.pieces.values():
                        for p in player_pieces:
                            # Verifica apenas peças vivas (não mortas)
                            if p.position == (new_r, new_c) and p.state != "Dead":
                                occupied = True
                                # Verifica se pode capturar a peça nesta posição
                                if self.can_captures(piece, p):
                                    possible_moves.append((new_r, new_c))
                                    piece.state = "can_attack"
                                    p.state = "under_attack"
                                break
                    if not occupied:
                        possible_moves.append((new_r, new_c))

        # Verifica se a peça está sob ameaça após fazer um movimento
        for move in possible_moves:
            r, c = move
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 1 <= nr < self.board.rows and 1 <= nc < self.board.cols:
                    for player_pieces in self.board.pieces.values():
                        for p in player_pieces:
                            if p.position == (nr, nc) and p.side != piece.side:
                                if self.can_captures(p, piece):
                                    piece.state = "under_attack"
                                    p.state = "can_attack"

        return possible_moves
        
    def try_jump(self, piece: Piece):
        """
        Verifica especificamente se um Leão ou Tigre pode realizar um salto sobre o rio.
        Útil para determinar se um caminho está bloqueado.
        
        Args:
            piece (Piece): A peça (Leão ou Tigre) para verificar
            
        Returns:
            str: "jump blocked" se o salto estiver bloqueado, None se o salto for possível
        """
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Direções possíveis
        r, c = piece.position
        piece.state = "Alive"  # Reseta o estado da peça

        for dr, dc in directions:
            # Apenas Leão e Tigre podem saltar
            if piece.name in ["Lion", "Tiger"]:
                jump_r, jump_c = r + dr, c + dc
                rat_in_the_way = False
                
                # Continua na direção enquanto estiver sobre o rio
                while (1 <= jump_r < self.board.rows and 1 <= jump_c < self.board.cols and
                       self.board.board[jump_r][jump_c] == "~"):
                    # Verifica se há um rato bloqueando o caminho
                    for player_pieces in self.board.pieces.values():
                        for p in player_pieces:
                            if p.position == (jump_r, jump_c) and p.name == "Rat":
                                rat_in_the_way = True
                                return "jump blocked"  # Salto bloqueado por um rato
                    jump_r += dr
                    jump_c += dc

                # Se chegou a uma posição válida após o rio e não há rato bloqueando
                if (1 <= jump_r < self.board.rows and 1 <= jump_c < self.board.cols and
                    self.board.board[jump_r][jump_c] != "~" and not rat_in_the_way):
                    # Verifica se há uma peça no destino que não pode ser capturada
                    for player_pieces in self.board.pieces.values():
                        for p in player_pieces:
                            if p.position == (jump_r, jump_c) and p.state != "Dead":
                                if not self.can_captures(piece, p):
                                    return "jump blocked"  # Salto bloqueado por uma peça que não pode ser capturada
                                break
                    continue
        return None  # Salto é possível

    def can_captures(self, attacker: Piece, defender: Piece):
        """
        Verifica se uma peça pode capturar outra baseado nas regras do jogo.
        
        Args:
            attacker (Piece): Peça atacante
            defender (Piece): Peça defensora
            
        Returns:
            bool: True se a captura for válida, False caso contrário
        """
        if attacker.side == defender.side:
            return False  # Não pode capturar peças do mesmo lado

        r1, c1 = attacker.position
        r2, c2 = defender.position
        terrain_attacker = self.board.board[r1][c1]
        terrain_defender = self.board.board[r2][c2]

        # Regras especiais para o Rato
        if attacker.name == "Rat":
            if terrain_attacker == "~":  # Rato na água
                if defender.name == "Rat" and terrain_defender == "~":  # Ambos ratos na água
                    return True
                return False  # Rato na água só pode atacar outro rato na água
            if terrain_defender == "~":  # Alvo na água, mas atacante em terra
                return False
            if defender.name == "Elephant":  # Rato pode derrotar o Elefante
                return True

        # Regras gerais
        if defender.name == "Rat" and terrain_defender == "~":  # Rato na água está protegido
            return False
        if attacker.name == "Elephant" and defender.name == "Rat":  # Elefante não pode derrotar o Rato
            return False
        return attacker.hp >= defender.hp  # Geralmente, peças de rank maior ou igual podem capturar

    def check_victory(self):
        """
        Verifica se algum jogador alcançou a vitória.
        Vitória ocorre quando uma peça chega à toca do adversário.
        
        Returns:
            bool/tuple: False se não houver vencedor, ou (True, posição) se houver
        """
        for player_pieces in self.board.pieces.values():
            for piece in player_pieces:
                if piece.position in {(1, 4)} and piece.side == "Player2":
                    print("🏆 Player 2 venceu!")
                    return True, piece.position
                elif piece.position in {(9, 4)} and piece.side == "Player1":
                    print("🏆 Player 1 venceu!")
                    return True, piece.position
        return False

    def trap_effects(self):
        """
        Aplica os efeitos das armadilhas nas peças.
        Peças em armadilhas têm seu hp reduzido a 1.
        """
        for player_pieces in self.board.pieces.values():
            for piece in player_pieces:
                r, c = piece.position
                cell = self.board.board[r][c]
                if cell == '%':  # Se a peça está em uma armadilha
                    piece.hp = 1  # Reduz os pontos de vida para 1
                else:
                    piece.hp = piece.rank  # Restaura os pontos de vida normal