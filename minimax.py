import random
from rules import Rules
import numpy as np
class AI:
    def __init__(self):
        pass

    def get_move_easy(self, board, rules, color):
        moves=[]
        for piece in board.pieces[color]:
            moves+=[(piece, rules.move(piece))]
        m=moves[random.randint(0,len(moves)-1)]
        p=m[0]
        move=m[1][random.randint(0,len(m[1])-1)]
        return (p,move)
    def get_move_medium(self, board, rules, color):
        best_move = None
        best_score = float('-inf')
        # Seleciona o melhor movimento utilizando minimax com depth 4.
        for piece in board.pieces[color]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                for move in moves:
                    # Simula o movimento num novo estado do tabuleiro
                    new_board = board.make_move(piece, move)
                    # Avalia o estado usando minimax (aqui, depth=4 e turno do adversário)
                    score = self.minimax(new_board, rules, depth=4, maximizingPlayer=False, color=color)
                    if score > best_score:
                        best_score = score
                        best_move = (piece, move)
        return best_move
    def get_move_hard(self, board, rules, color):
        return self.alpha_beta_cutoff_search(board,rules,0,color)
    def minimax(self, board, rules, depth, maximizingPlayer, color=None):
        if color is None:
            color = "MAGENTA" # default
        # Se o depth for 0 ou se o jogo tiver terminado, avalia a posição.
        victory = rules.check_victory()
        if depth == 0 or victory:
            return self.evaluate_position(board, rules, 0)

        if maximizingPlayer:
            max_eval = float('-inf')
            for piece in board.pieces[board.ai_color]:
                if piece.state != "Dead":
                    moves = rules.move(piece)
                    for move in moves:
                        new_board = board.make_move(piece, move)
                        eval = self.minimax(new_board, rules, depth - 1, False)
                        max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for piece in board.pieces[board.opponent_color]:
                if piece.state != "Dead":
                    moves = rules.move(piece)
                    for move in moves:
                        new_board = board.make_move(piece, move)
                        eval = self.minimax(new_board, rules, depth - 1, True)
                        min_eval = min(min_eval, eval)
            return min_eval

    def evaluate_position(self, board, rules, difficulty):
        """
        Avalia a posição geral subtraindo a pontuação do adversário
        da pontuação da IA.
        """
        if difficulty==0:
            ai_score = self.simple_evaluate_side(board, rules, board.ai_color)
            opponent_score = self.simple_evaluate_side(board, rules, board.opponent_color)
        else:
            ai_score = self.complex_evaluate_side(board, rules, board.ai_color)
            opponent_score = self.complex_evaluate_side(board, rules, board.opponent_color)
        return ai_score - opponent_score
    
    
    def simple_evaluate_side(self, board, rules, side):
        score = 0
        # Determina a cor do adversário
        opponent_side = "MAGENTA" if side == "YELLOW" else "YELLOW"
        for piece in board.pieces[side]:
            if piece.state == "Dead":
                continue
            value = piece.rank  # valor base é o rank da peça
            if piece.name == "Elephant":
                threatened = False
                # Verifica se algum Rat adversário ameaça este Elephant
                for enemy in board.pieces[opponent_side]:
                    if enemy.name == "Rat" and enemy.state != "Dead":
                        enemy_moves = rules.move(enemy)
                        if piece.position in enemy_moves:
                            threatened = True
                            break
                if threatened:
                    value *= 0.5  # reduz o valor efetivo do Elephant
            score += value
        return score

    def complex_evaluate_side(self, board, rules, side):
        """
        Percorre todas as peças de um lado (por exemplo, "MAGENTA" ou "YELLOW")
        e soma os seus valores (baseados no rank).

        Se a peça for um Elephant, verifica se algum Rat adversário pode capturá-lo.
        Se estiver ameaçado, reduz o valor efetivo do Elephant (por exemplo, 50% do seu rank).
        """
        bonus_L_T=5
        bonus_R=6
        score = 0
        possible_moves=set()
        traps={(1,3), (2,4), (1,5)} if side=="YELLOW" else {(9,3), (8,4), (9,5)}
        # Determina a cor do adversário
        opponent_side = "MAGENTA" if side == "YELLOW" else "YELLOW"
        corr=False
        if self.corrida(board, side)[0]: # verifica se é possivel correr para o den adversário antes do adversário
            if self.corrida(board, opponent_side)[0]:
                if self.corrida(board, side)<=self.corrida(board, opponent_side):
                    corr=True
            else:
                corr=True            
        for piece in board.pieces[side]:
            if piece.state == "Dead":
                continue
            value = piece.rank  # valor base é o rank da peça
            if piece.name in ["Lion", "Tiger"]: # bonus para peças especiais
                value+=bonus_L_T
            elif piece.name=="Rat":
                if board.pieces[opponent_side][0].state=="Dead": # diminui bonus do rato se elefante adeversário estiver morto
                    bonus_R/=2
                value+=bonus_R
            if piece.state=="under_attack": # diminui valor da peça caso ela esteja em perigo
                value/=2
            score += value
            possible_moves=possible_moves | set(rules.move(piece))

        for piece in [board.pieces[opponent_side][1],board.pieces[opponent_side][2]]: # verifica se peças estão a bloquear saltos adversários
            if rules.try_jump(piece)=="jump blocked":
                score+=4
        if traps in possible_moves:
            score+=5
        if corr:
            score=10000
        return score
    def corrida(self, board, side):
        livre=False
        min_dis=100
        opponent_side="MAGENTA" if side=="YELLOW" else "YELLOW"
        for p in board.pieces[side]+board.pieces[opponent_side]:
            if self.man_dis(p, side)<min_dis:
                if p.side==side:
                    livre=True
                else:
                    livre=False
            elif self.man_dis(p, side)==min_dis:
                if p.side==opponent_side:
                    livre=False
        return (livre, min_dis)    
    def man_dis(self, piece, side):
        den=(9,4) if side=="YELLOW" else (1,4)
        xd, yd=den
        x, y=piece.position
        return abs(xd-x)+abs(yd-y)
    def alpha_beta_cutoff_search(self, board, rules, difficulty, side, d=4):
        """Search game to determine best action; use alpha-beta pruning.
        This version cuts off search and uses an evaluation function."""
        player = side
        opponent_side="MAGENTA" if side=="YELLOW" else "YELLOW"
        # Functions used by alpha_beta
        def max_value(board, rules, difficulty, alpha, beta, depth, verified_boards):
            if cutoff_test(rules, depth):
                return self.evaluate_position(board, rules, difficulty)
            v = -np.inf
            for p in board.pieces[player]:
                for a in rules.move(p):
                    if board.make_move(p,a) not in verified_boards:
                        verified_boards+=[board.make_move(p,a)]
                        v = max(v, min_value(board.make_move(p, a), Rules(board.make_move(p, a)), difficulty, alpha, beta, depth + 1, verified_boards))
                        if v >= beta:
                            return v
                        alpha = max(alpha, v)
            return v

        def min_value (board, rules, difficulty, alpha, beta, depth, verified_boards):
            if cutoff_test(rules, depth):
                return self.evaluate_position(board, rules, difficulty)
            v = np.inf
            for p in board.pieces[opponent_side]:
                for a in rules.move(p):
                    if board.make_move(p,a) not in verified_boards:
                        verified_boards+=[board.make_move(p,a)]
                        v = min(v, max_value(board.make_move(p, a), Rules(board.make_move(p, a)), difficulty, alpha, beta, depth + 1,verified_boards))
                        if v <= alpha:
                            return v
                        beta = min(beta, v)
            return v

        # Body of alpha_beta_cutoff_search starts here:
        # The default test cuts off at depth d or at a terminal state
        cutoff_test =lambda rules, depth: depth > d or rules.check_victory()
        best_score = -np.inf
        beta = np.inf
        best_action = None
        moves=[]
        verified_boards=[]
        for p in board.pieces[side]:
            moves=rules.move(p)
            for a in moves:
                v = min_value(board.make_move(p,a), Rules(board.make_move(p, a)), difficulty, best_score, beta, 1, verified_boards)
                if v > best_score:
                    best_score = v
                    best_action = a
                    best_piece=p
        return (best_piece, best_action)
