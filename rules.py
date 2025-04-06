from piece import Piece

class Rules:
    def __init__(self, board):
        self.board = board
        # Cache common values
        self.directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        self.player1_den = (9, 4)
        self.player2_den = (1, 4)
        self.jump_pieces = {"Lion", "Tiger"}

    def move(self, piece: Piece) -> list:
        """Get all possible moves for a piece"""
        if piece.state == "Dead":
            return []
            
        possible_moves = []
        r, c = piece.position
        piece.state = "Alive"  # Reset state

        for dr, dc in self.directions:
            new_r, new_c = r + dr, c + dc

            # Check if position is within bounds
            if not (1 <= new_r < self.board.rows and 1 <= new_c < self.board.cols):
                continue
                
            # Check if piece is trying to enter opponent's den
            if (piece.side == "Player1" and (new_r, new_c) == self.player2_den) or \
               (piece.side == "Player2" and (new_r, new_c) == self.player1_den):
                continue

            # Handle jumps for Lion/Tiger
            if piece.name in self.jump_pieces:
                jump_result = self._try_jump(piece, r, c, dr, dc)
                if jump_result:
                    possible_moves.append(jump_result)
                    continue  # Skip normal move check if jump was possible

            # Handle normal moves
            self._add_normal_move(piece, new_r, new_c, possible_moves)

        # Check for threats to this piece's potential moves
        self._check_threats(piece, possible_moves)
        
        return possible_moves

    def _try_jump(self, piece, r, c, dr, dc):
        """Try to jump over river with Lion or Tiger"""
        jump_r, jump_c = r + dr, c + dc
        
        # Check if there's a river in this direction
        if self.board.board[jump_r][jump_c] != '~':
            return None
            
        # Look for a rat in the river
        rat_in_the_way = False
        while (1 <= jump_r < self.board.rows and 1 <= jump_c < self.board.cols and
               self.board.board[jump_r][jump_c] == '~'):
            target_piece = self.board.get_piece_at((jump_r, jump_c))
            if target_piece and target_piece.name == "Rat":
                rat_in_the_way = True
                break
            jump_r += dr
            jump_c += dc

        # Check landing position
        if (1 <= jump_r < self.board.rows and 1 <= jump_c < self.board.cols and
            not rat_in_the_way):
            
            target_piece = self.board.get_piece_at((jump_r, jump_c))
            if target_piece and target_piece.state != "Dead":
                if self.can_capture(piece, target_piece):
                    piece.state = "can_attack"
                    target_piece.state = "under_attack"
                    return (jump_r, jump_c)
            else:
                return (jump_r, jump_c)
                
        return None

    def _add_normal_move(self, piece, new_r, new_c, possible_moves):
        """Add normal (non-jump) moves"""
        target_cell = self.board.board[new_r][new_c]
        
        # Rats can enter water, others can't
        if target_cell == '~' and piece.name != "Rat":
            return
            
        target_piece = self.board.get_piece_at((new_r, new_c))
        if target_piece and target_piece.state != "Dead":
            # There's a piece at the target location
            if self.can_capture(piece, target_piece):
                possible_moves.append((new_r, new_c))
                piece.state = "can_attack"
                target_piece.state = "under_attack"
        else:
            # The target location is empty
            possible_moves.append((new_r, new_c))

    def _check_threats(self, piece, possible_moves):
        """Check if piece is under threat in any of its possible moves"""
        for r, c in possible_moves:
            for dr, dc in self.directions:
                nr, nc = r + dr, c + dc
                if 1 <= nr < self.board.rows and 1 <= nc < self.board.cols:
                    enemy = self.board.get_piece_at((nr, nc))
                    if enemy and enemy.side != piece.side and enemy.state != "Dead":
                        if self.can_capture(enemy, piece):
                            piece.state = "under_attack"
                            enemy.state = "can_attack"

    def can_capture(self, attacker: Piece, defender: Piece):
        """Check if attacker can capture defender"""
        # Can't capture allies
        if attacker.side == defender.side:
            return False
            
        # Get terrain information
        r1, c1 = attacker.position
        r2, c2 = defender.position
        terrain_attacker = self.board.board[r1][c1]
        terrain_defender = self.board.board[r2][c2]

        # Special case: Rat
        if attacker.name == "Rat":
            # Rat in water can only capture rat in water
            if terrain_attacker == "~":
                return defender.name == "Rat" and terrain_defender == "~"
            # Rat on land can't capture into water
            if terrain_defender == "~":
                return False
            # Special case: Rat can capture Elephant
            if defender.name == "Elephant":
                return True

        # Elephant can't capture Rat
        if attacker.name == "Elephant" and defender.name == "Rat":
            return False
            
        # Can't capture a Rat in water unless you're a Rat in water
        if defender.name == "Rat" and terrain_defender == "~":
            return False
            
        # Normal rank-based capture
        return attacker.hp >= defender.hp

    def check_victory(self):
        """Check if either player has won"""
        for pieces in self.board.pieces.values():
            for piece in pieces:
                if piece.state != "Dead":
                    if piece.position == self.player2_den and piece.side == "Player1":
                        print("🏆 Player 1 venceu!")
                        return True
                    elif piece.position == self.player1_den and piece.side == "Player2":
                        print("🏆 Player 2 venceu!")
                        return True
        return False

    def trap_effects(self):
        """Apply trap effects to pieces"""
        for pieces in self.board.pieces.values():
            for piece in pieces:
                if piece.state != "Dead":
                    r, c = piece.position
                    if self.board.board[r][c] == '%':
                        piece.hp = 1
                    else:
                        piece.hp = piece.rank