import random
import numpy as np
from functools import lru_cache

class AI:
    def __init__(self):
        # Evaluation weights
        self.piece_value = {
            "Elephant": 8,
            "Lion": 12,  # Lion base value (7) + bonus (5)
            "Tiger": 11,  # Tiger base value (6) + bonus (5)
            "Leopard": 5,
            "Wolf": 4,
            "Dog": 3,
            "Cat": 2,
            "Rat": 7,    # Rat base value (1) + bonus (6)
        }
        self.position_bonus = {}  # Will be initialized based on the board
        self.trap_value = 5
        self.den_approach_value = 10
        self.blocking_value = 4
        
    def get_move_easy(self, board, rules, color):
        """Get a random legal move - for easy difficulty"""
        valid_moves = []
        
        # Collect all valid moves
        for piece in board.pieces[color]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                for move in moves:
                    valid_moves.append((piece, move))
                    
        if not valid_moves:
            return None
            
        # Return a random move
        return random.choice(valid_moves)
    
    def get_move_medium(self, board, rules, color):
        """Get a move using basic evaluation - for medium difficulty"""
        best_move = None
        best_score = float('-inf')
        
        # Set opponent color
        opponent_color = "MAGENTA" if color == "YELLOW" else "YELLOW"
        board.ai_color = color
        board.opponent_color = opponent_color
        
        # Initialize position values based on the board
        self._init_position_values(board)
        
        # Find the best move by checking immediate outcomes
        for piece in board.pieces[color]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                for move in moves:
                    # Simulate the move
                    new_board = board.make_move(piece, move)
                    new_rules = type(rules)(new_board)
                    
                    # Calculate the score after this move
                    score = self.evaluate_position(new_board, new_rules, 0)
                    
                    if score > best_score:
                        best_score = score
                        best_move = (piece, move)
        
        return best_move
    
    def get_move_hard(self, board, rules, color):
        """Get a move using alpha-beta pruning - for hard difficulty"""
        # Set opponent color
        opponent_color = "MAGENTA" if color == "YELLOW" else "YELLOW"
        board.ai_color = color
        board.opponent_color = opponent_color
        
        # Initialize position values
        self._init_position_values(board)
        
        # Use alpha-beta pruning with depth 4
        return self.alpha_beta_search(board, rules, color, 4)
    
    def _init_position_values(self, board):
        """Initialize position value table - higher value for positions closer to opponent's den"""
        opponent_den = (1, 4) if board.ai_color == "YELLOW" else (9, 4)
        
        # Create position bonus table
        self.position_bonus = {}
        for r in range(1, board.rows):
            for c in range(1, board.cols):
                # Manhattan distance to opponent's den
                distance = abs(r - opponent_den[0]) + abs(c - opponent_den[1])
                # Bonus for positions closer to opponent's den (max 5)
                self.position_bonus[(r, c)] = max(0, 5 - distance//2)
    
    def evaluate_position(self, board, rules, difficulty):
        """Evaluate board position from AI's perspective"""
        ai_score = self._evaluate_side(board, rules, board.ai_color)
        opponent_score = self._evaluate_side(board, rules, board.opponent_color)
        
        # Check for win conditions with high priority
        for piece in board.pieces[board.ai_color]:
            if piece.state != "Dead":
                # If AI has a piece on opponent's den, that's a win
                opponent_den = (1, 4) if board.ai_color == "YELLOW" else (9, 4)
                if piece.position == opponent_den:
                    return 10000  # Very high value for winning
        
        for piece in board.pieces[board.opponent_color]:
            if piece.state != "Dead":
                # If opponent has a piece on AI's den, that's a loss
                ai_den = (9, 4) if board.ai_color == "YELLOW" else (1, 4)
                if piece.position == ai_den:
                    return -10000  # Very low value for losing
        
        return ai_score - opponent_score
    
    def _evaluate_side(self, board, rules, side):
        """Evaluate the strength of one side"""
        score = 0
        opponent_side = "MAGENTA" if side == "YELLOW" else "YELLOW"
        opponent_den = (1, 4) if side == "YELLOW" else (9, 4)
        
        # Calculate values for all pieces
        for piece in board.pieces[side]:
            if piece.state == "Dead":
                continue
                
            # Base value from piece type
            value = self.piece_value.get(piece.name, piece.rank)
            
            # Reduce value if piece is under threat
            if piece.state == "under_attack":
                value *= 0.5
                
            # Add position bonus
            pos_bonus = self.position_bonus.get(piece.position, 0)
            value += pos_bonus
            
            # Special cases
            if piece.name == "Elephant":
                # Check if any enemy Rat threatens this Elephant
                for enemy in board.pieces[opponent_side]:
                    if enemy.name == "Rat" and enemy.state != "Dead":
                        enemy_moves = rules.move(enemy)
                        if piece.position in enemy_moves:
                            value *= 0.5  # Reduce Elephant value when threatened by Rat
                            break
            
            # Add to total score
            score += value
        
        # Check for strategic advantages
        
        # 1. Count pieces near opponent's den
        pieces_near_den = 0
        for piece in board.pieces[side]:
            if piece.state != "Dead":
                dist = abs(piece.position[0] - opponent_den[0]) + abs(piece.position[1] - opponent_den[1])
                if dist <= 2:
                    pieces_near_den += 1
        
        score += pieces_near_den * 3  # Bonus for pieces near opponent's den
        
        # 2. Bonus for controlling center
        center_positions = [(4, 3), (4, 4), (5, 3), (5, 4)]
        for pos in center_positions:
            piece = board.get_piece_at(pos)
            if piece and piece.color == side:
                score += 2  # Bonus for controlling central positions
        
        # 3. Bonus for blocking opponent's jumping pieces
        for enemy in board.pieces[opponent_side]:
            if enemy.state != "Dead" and enemy.name in ["Lion", "Tiger"]:
                # Check if this Lion/Tiger is blocked from jumping
                blocked = True
                for dr, dc in rules.directions:
                    r, c = enemy.position
                    jump_r, jump_c = r + dr, c + dc
                    if (1 <= jump_r < board.rows and 1 <= jump_c < board.cols and 
                        board.board[jump_r][jump_c] == '~'):
                        # Found a river direction - check if jump is blocked
                        rat_blocking = False
                        while (1 <= jump_r < board.rows and 1 <= jump_c < board.cols and
                               board.board[jump_r][jump_c] == '~'):
                            p = board.get_piece_at((jump_r, jump_c))
                            if p and p.name == "Rat" and p.color == side:
                                rat_blocking = True
                                break
                            jump_r += dr
                            jump_c += dc
                        
                        if rat_blocking:
                            score += self.blocking_value
                
        return score
    
    def alpha_beta_search(self, board, rules, color, depth=4):
        """Alpha-beta pruning search to find best move"""
        opponent_color = "MAGENTA" if color == "YELLOW" else "YELLOW"
        
        def max_value(board, rules, alpha, beta, depth, transposition_table=None):
            """Find maximum value for AI player"""
            if transposition_table is None:
                transposition_table = {}
                
            # Use string representation of board as hash key
            board_hash = self._hash_board(board)
            
            # Check transposition table
            if board_hash in transposition_table and depth <= transposition_table[board_hash][1]:
                return transposition_table[board_hash][0]
                
            if depth == 0 or rules.check_victory():
                score = self.evaluate_position(board, rules, 1)
                transposition_table[board_hash] = (score, depth)
                return score
                
            v = float('-inf')
            for piece in board.pieces[color]:
                if piece.state != "Dead":
                    moves = rules.move(piece)
                    for move in moves:
                        next_board = board.make_move(piece, move)
                        next_rules = type(rules)(next_board)
                        v = max(v, min_value(next_board, next_rules, alpha, beta, depth-1, transposition_table))
                        if v >= beta:
                            return v  # Beta cutoff
                        alpha = max(alpha, v)
                        
            transposition_table[board_hash] = (v, depth)
            return v
            
        def min_value(board, rules, alpha, beta, depth, transposition_table=None):
            """Find minimum value for opponent"""
            if transposition_table is None:
                transposition_table = {}
                
            board_hash = self._hash_board(board)
            
            if board_hash in transposition_table and depth <= transposition_table[board_hash][1]:
                return transposition_table[board_hash][0]
                
            if depth == 0 or rules.check_victory():
                score = self.evaluate_position(board, rules, 1)
                transposition_table[board_hash] = (score, depth)
                return score
                
            v = float('inf')
            for piece in board.pieces[opponent_color]:
                if piece.state != "Dead":
                    moves = rules.move(piece)
                    for move in moves:
                        next_board = board.make_move(piece, move)
                        next_rules = type(rules)(next_board)
                        v = min(v, max_value(next_board, next_rules, alpha, beta, depth-1, transposition_table))
                        if v <= alpha:
                            return v  # Alpha cutoff
                        beta = min(beta, v)
                        
            transposition_table[board_hash] = (v, depth)
            return v
        
        # Main alpha-beta search logic
        best_score = float('-inf')
        beta = float('inf')
        best_move = None
        transposition_table = {}
        
        # Evaluate all possible moves
        for piece in board.pieces[color]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                for move in moves:
                    next_board = board.make_move(piece, move)
                    next_rules = type(rules)(next_board)
                    
                    # Get value from opponent's perspective (min player)
                    score = min_value(next_board, next_rules, best_score, beta, depth-1, transposition_table)
                    
                    if score > best_score:
                        best_score = score
                        best_move = (piece, move)
                        
        return best_move
    
    def _hash_board(self, board):
        """Create a hash representation of the board state for transposition table"""
        # Simple string representation of piece positions and states
        hash_parts = []
        for color in board.pieces:
            for piece in board.pieces[color]:
                if piece.state != "Dead":
                    hash_parts.append(f"{piece.name}:{piece.position}:{piece.state}")
                    
        return "|".join(sorted(hash_parts))