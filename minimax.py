import random
import numpy
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

    def minimax(self, board, rules, depth, maximizingPlayer, color=None):
        if color is None:
            color = "MAGENTA" # default
        # Se o depth for 0 ou se o jogo tiver terminado, avalia a posição.
        victory = rules.check_victory()
        if depth == 0 or victory:
            return self.evaluate_position(board, rules)

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

    def evaluate_position(self, board, rules):
        """
        Avalia a posição geral subtraindo a pontuação do adversário
        da pontuação da IA.
        """
        ai_score = self.evaluate_side(board, rules, board.ai_color)
        opponent_score = self.evaluate_side(board, rules, board.opponent_color)
        return ai_score - opponent_score

    def evaluate_side(self, board, rules, side):
        """
        Percorre todas as peças de um lado (por exemplo, "MAGENTA" ou "YELLOW")
        e soma os seus valores (baseados no rank).

        Se a peça for um Elephant, verifica se algum Rat adversário pode capturá-lo.
        Se estiver ameaçado, reduz o valor efetivo do Elephant (por exemplo, 50% do seu rank).
        """
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

