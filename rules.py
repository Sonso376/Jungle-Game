from piece import Piece
from board import Board

class Rules:
    def __init__(self, board):
        self.board = board

    def move(self, piece: Piece) -> list:
        possible_moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        r, c = piece.position
        piece.state = True

        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc

            if 1 <= new_r < self.board.rows and 1 <= new_c < self.board.cols:
                target_cell = self.board.board[new_r][new_c]

                if (piece.side == "Player1" and (new_r, new_c) == (9, 4)) or \
                   (piece.side == "Player2" and (new_r, new_c) == (1, 4)):
                    continue

                # Attempt jump for Lion/Tiger
                if piece.name in ["Lion", "Tiger"]:
                    jump_r, jump_c = r + dr, c + dc
                    rat_in_the_way = False
                    while (1 <= jump_r < self.board.rows and 1 <= jump_c < self.board.cols and
                           self.board.board[jump_r][jump_c] == "~"):
                        for player_pieces in self.board.pieces.values():
                            for p in player_pieces:
                                if p.position == (jump_r, jump_c) and p.name == "Rat":
                                    rat_in_the_way = True
                        jump_r += dr
                        jump_c += dc

                    if (1 <= jump_r < self.board.rows and 1 <= jump_c < self.board.cols and
                        self.board.board[jump_r][jump_c] != "~" and not rat_in_the_way):

                        occupied = False
                        for player_pieces in self.board.pieces.values():
                            for p in player_pieces:
                                if p.position == (jump_r, jump_c):
                                    occupied = True
                                    if self.can_captures(piece, p):
                                        possible_moves.append((jump_r, jump_c))
                                        piece.state = "can_attack"
                                        p.state = "under_attack"
                                    break
                        if not occupied:
                            possible_moves.append((jump_r, jump_c))
                        continue  # Skip normal move if jump was tried

                if piece.name == "Rat" or target_cell != "~":
                    occupied = False
                    for player_pieces in self.board.pieces.values():
                        for p in player_pieces:
                            if p.position == (new_r, new_c):
                                occupied = True
                                if self.can_captures(piece, p):
                                    possible_moves.append((new_r, new_c))
                                    piece.state = "can_attack"
                                    p.state = "under_attack"
                                break
                    if not occupied:
                        possible_moves.append((new_r, new_c))

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

    def can_captures(self, attacker: Piece, defender: Piece):
        if attacker.side == defender.side:
            return False

        r1, c1 = attacker.position
        r2, c2 = defender.position
        terrain_attacker = self.board.board[r1][c1]
        terrain_defender = self.board.board[r2][c2]

        if attacker.name == "Rat":
            if terrain_attacker == "~":
                if defender.name == "Rat" and terrain_defender == "~":
                    return True
                return False
            if terrain_defender == "~":
                return False
            if defender.name == "Elephant":
                return True

        if defender.name == "Rat" and terrain_defender == "~":
            return False

        return attacker.hp >= defender.hp

    def check_victory(self):
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
        for player_pieces in self.board.pieces.values():
            for piece in player_pieces:
                r, c = piece.position
                cell = self.board.board[r][c]
                if cell == '%':
                    piece.hp = 1
                else:
                    piece.hp = piece.rank