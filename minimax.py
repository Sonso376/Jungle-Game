import random
import math
from board import Board
from piece import get_pieces
import time

class AI:
    def __init__(self):
        self.transposition_table = {} # Inicializa a tabela de transposição

    def compute_hash(self,board):
        """
        Gera uma chave imutável para o estado atual do tabuleiro, baseada nas posições,
        nomes e estados das peças.
        """
        key_parts = []
        # Ordena as chaves para ter consistência (por exemplo, YELLOW e MAGENTA)
        for side in sorted(board.pieces.keys()):
            # Ordena as peças por nome para ter uma ordem fixa
            for piece in sorted(board.pieces[side], key=lambda p: p.name):
                key_parts.append((piece.name, piece.position, piece.state))
        return tuple(key_parts)


    def get_move_easy(self, board, rules, color):
        moves = []
        for piece in board.pieces[color]:
            moves += [(piece, rules.move(piece))]
        m = moves[random.randint(0, len(moves) - 1)]
        p = m[0]
        move = m[1][random.randint(0, len(m[1]) - 1)]
        return (p, move)

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
                    # Avalia o estado usando minimax (aqui, depth=2 e turno do adversário)
                    score = self.minimax(new_board, rules, depth=2, maximizingPlayer=False, color=color)
                    if score > best_score:
                        best_score = score
                        best_move = (piece, move)
        return best_move

    def get_move_hard(self, board, rules, color):
        best_move = None
        best_score = float('-inf')

        for piece in board.pieces[color]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                for move in moves:
                    new_board = board.make_move(piece, move)
                    score = self.minimax_ab(new_board, rules, depth=4, maximizingPlayer=False, alpha=float('-inf'), beta=float('inf'), color=color)
                    if score > best_score:
                        best_score = score
                        best_move = (piece, move)
        return best_move

    def get_move_hard_iterative(self, board, rules, color, time_limit=10):
        """
        Realiza iterative deepening para buscar o melhor movimento para a dificuldade 'hard'.
        O mé3t0do tenta profundidades sucessivas até o tempo limite (em segundos) ser alcançado.
        Retorna o melhor movimento encontrado até o momento.
        """
        start_time = time.time()
        best_move = None
        depth = 1

        while True:
            if time.time() - start_time >= time_limit:
                break

            current_best_move = None
            best_score = float('-inf')

            # Percorre todas as peças da cor (da IA)
            for piece in board.pieces[color]:
                if piece.state != "Dead":
                    # Obter os movimentos ordenados para a peça (para maximizador)
                    moves = self.get_ordered_moves(board, rules, piece, color, maximizingPlayer=True)
                    for move in moves:
                        new_board = board.make_move(piece, move)
                        # Avalia usando minimax_ab com a profundidade atual
                        try:
                            score = self.minimax_ab(new_board, rules, depth, maximizingPlayer=False,
                                                    alpha=float('-inf'), beta=float('inf'), color=color,
                                                    start_time=start_time, time_limit=time_limit)
                        except Exception as e:
                            score = self.evaluate_position(new_board, rules, 1)
                        if score > best_score:
                            best_score = score
                            current_best_move = (piece, move)

            print(f"Profundidade {depth} completa: melhor score = {best_score}")

            # Atualiza o melhor movimento se essa iteração foi concluída sem exceder o tempo
            best_move = current_best_move

            depth += 1  # Aumenta a profundidade para a próxima iteração

        return best_move

    def get_move_mcts(self, board, rules, color, iterations=500, simulation_depth=20):
        """
        Implementa uma versão simples do Monte Carlo Tree Search.
        - board: estado atual do tabuleiro
        - rules: instância de Rules
        - color: lado da IA (ex.: "YELLOW" ou "MAGENTA")
        - iterations: número de iterações de simulação
        - simulation_depth: número máximo de movimentos na fase de simulação
        Retorna uma tupla (piece, move) representando o melhor movimento encontrado.
        """

        class Node:
            def __init__(self, board, move=None, parent=None, player=None):
                self.board = board
                self.move = move  # Movimento que levou a esse estado (tuple: (piece, move))
                self.parent = parent
                self.player = player  # Jogador que realizou esse movimento
                self.children = []
                self.untried_moves = self.get_all_moves(board, player)
                self.visits = 0
                self.wins = 0

            def get_all_moves(self, board, player):
                moves = []
                # Para cada peça do jogador, obtém todos os movimentos legais
                for piece in board.pieces[player]:
                    if piece.state != "Dead":
                        for m in rules.move(piece):
                            moves.append((piece, m))
                return moves

            def UCT(self, exploration=1.41):
                # Se não houver visitas, retorne infinito para forçar exploração
                if self.visits == 0:
                    return float('inf')
                return self.wins / self.visits + exploration * math.sqrt(math.log(self.parent.visits) / self.visits)

        def select(node):
            # Seleciona recursivamente o filho com maior UCT até encontrar um nó com movimentos não explorados
            while node.untried_moves == [] and node.children:
                node = max(node.children, key=lambda child: child.UCT())
            return node

        def expand(node):
            # Expande um dos movimentos não explorados
            move = node.untried_moves.pop()
            new_board = board.make_move(move[0], move[1])
            # O próximo jogador é o adversário
            next_player = "MAGENTA" if node.player == "YELLOW" else "YELLOW"
            child = Node(new_board, move, parent=node,
                         player=node.player)  # Mantemos o mesmo jogador para as estatísticas do nó raiz
            node.children.append(child)
            return child

        def simulate(node):
            # Realiza uma simulação (playout) a partir do estado do nó
            sim_board = node.board
            current_player = node.player  # Começamos com o jogador do nó raiz
            for _ in range(simulation_depth):
                victory = rules.check_victory()
                if victory:
                    break
                moves = []
                for piece in sim_board.pieces[current_player]:
                    if piece.state != "Dead":
                        for m in rules.move(piece):
                            moves.append((piece, m))
                if not moves:
                    break
                move = random.choice(moves)
                sim_board = sim_board.make_move(move[0], move[1])
                current_player = "MAGENTA" if current_player == "YELLOW" else "YELLOW"
            # Usa a avaliação simples do estado final para determinar o resultado
            # Se o score for positivo, assume vitória para o lado 'color'
            final_score = self.evaluate_position(sim_board, rules, 1)
            return 1 if final_score > 0 else 0

        def backpropagate(node, result):
            # Atualiza as estatísticas do nó e de seus ancestrais
            while node is not None:
                node.visits += 1
                node.wins += result
                node = node.parent

        # Inicializa a raiz do MCTS com o estado atual do tabuleiro
        root = Node(board, move=None, parent=None, player=color)
        # Executa as iterações de MCTS
        for _ in range(iterations):
            node = select(root)
            if node.untried_moves:
                node = expand(node)
            result = simulate(node)
            backpropagate(node, result)
        # Seleciona o filho da raiz com maior número de visitas
        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.move


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

    def minimax_ab(self, board, rules, depth, maximizingPlayer, alpha, beta, color=None, start_time=None, time_limit=10):
        if start_time is None:
            start_time = time.time()
        # Verifica se o tempo excedeu o limite
        if time.time() - start_time > time_limit:
            # Se o tempo excedeu, retorna uma avaliação rápida do estado atual
            return self.evaluate_position(board, rules, 1)

        if color is None:
            color = "MAGENTA"
        # Calcula a chave para o estado atual do tabuleiro
        key = self.compute_hash(board)
        # Se já avaliamos esse estado com profundidade igual ou maior, reutilizar o valor
        if key in self.transposition_table:
            stored_depth, stored_value = self.transposition_table[key]
            if stored_depth >= depth:
                return stored_value

        victory = rules.check_victory()
        if depth == 0 or victory:
            value = self.evaluate_position(board, rules, 1)
            self.transposition_table[key] = depth, value
            return value
        if maximizingPlayer:
            max_eval = float('-inf')
            for piece in board.pieces[board.ai_color]:
                if piece.state != "Dead":
                    moves = self.get_ordered_moves(board, rules, piece, color, maximizingPlayer=True)
                    for move in moves:
                        new_board = board.make_move(piece, move)
                        eval_value = self.minimax_ab(new_board, rules, depth - 1, False, alpha, beta, color, start_time, time_limit)
                        max_eval = max(max_eval, eval_value)
                        alpha = max(alpha, eval_value)
                        if beta <= alpha:
                            break  # poda beta
            self.transposition_table[key] = (depth, max_eval)
            return max_eval
        else:
            min_eval = float('inf')
            for piece in board.pieces[board.opponent_color]:
                if piece.state != "Dead":
                    moves = self.get_ordered_moves(board, rules, piece, color, maximizingPlayer=False)
                    for move in moves:
                        new_board = board.make_move(piece, move)
                        eval_value = self.minimax_ab(new_board, rules, depth - 1, True, alpha, beta, color, start_time, time_limit)
                        min_eval = min(min_eval, eval_value)
                        beta = min(beta, eval_value)
                        if beta <= alpha:
                            break  # poda alfa
            self.transposition_table[key] = (depth, min_eval)
            return min_eval

    def get_ordered_moves(self, board, rules, piece, color, maximizingPlayer):
        # Obtém os movimentos legais para a peça
        moves = rules.move(piece)
        move_evaluations = []
        for move in moves:
            # Simula o movimento
            new_board = board.make_move(piece, move)
            # Usa uma avaliação rápida (simple_evaluate_side)
            eval_value = self.simple_evaluate_side(new_board, rules, color)
            move_evaluations.append((move, eval_value))
        # Se for maximizador, queremos os maiores valores primeiro; se for minimizador, os menores
        if maximizingPlayer:
            move_evaluations.sort(key=lambda x: x[1], reverse=True)
        else:
            move_evaluations.sort(key=lambda x: x[1])
        # Retorna apenas a lista ordenada de movimentos
        return [move for move, score in move_evaluations]


    def evaluate_position(self, board, rules, difficulty):
        """
        Avalia a posição geral subtraindo a pontuação do adversário
        da pontuação da IA.
        """
        if difficulty == 0:
            ai_score = self.simple_evaluate_side(board, rules, board.ai_color)
            opponent_score = self.simple_evaluate_side(board, rules, board.opponent_color)
        else:
            ai_score = self.complex_evaluate_side(board, rules, board.ai_color)
            opponent_score = self.complex_evaluate_side(board, rules, board.opponent_color)
        return ai_score - opponent_score

    def simple_evaluate_side(self, board, rules, side):
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

    def corrida(self, board, side):
        livre = False
        min_dis = 100
        opponent_side = "MAGENTA" if side == "YELLOW" else "YELLOW"
        for p in board.pieces[side] + board.pieces[opponent_side]:
            if self.man_dis(p, side) < min_dis:
                if p.side == side:
                    livre = True
                else:
                    livre = False
            elif self.man_dis(p, side) == min_dis:
                if p.side == opponent_side:
                    livre = False
        return (livre, min_dis)

    def man_dis(self, piece, side):
        den = (9, 4) if side == "YELLOW" else (1, 4)
        xd, yd = den
        x, y = piece.position
        return abs(xd - x) + abs(yd - y)

    def complex_evaluate_side(self, board, rules, side):
        """
        Percorre todas as peças de um lado (por exemplo, "MAGENTA" ou "YELLOW")
        e soma os seus valores (baseados no rank).

        Se a peça for um Elephant, verifica se algum Rat adversário pode capturá-lo.
        Se estiver ameaçado, reduz o valor efetivo do Elephant (por exemplo, 50% do seu rank).
        """
        bonus_L_T = 5  # Bônus para Lion/Tiger
        bonus_R = 6  # Bônus para Rat (ou penalidade se o Rat adversário for uma ameaça)
        mobility_factor = 0.5  # Fator para cada movimento legal disponível
        positional_weight = 0.2  # Bônus por redução de distância ao den adversário
        trap_penalty = 0.5  # Multiplicador de valor se a peça estiver em armadilha
        capture_bonus = 2  # Bônus multiplicador para cada peça adversária capturada

        score = 0
        possible_moves = set()

        # Define armadilhas, den adversário e lado adversário
        if side == "YELLOW":
            traps = {(1, 3), (2, 4), (1, 5)}
            enemy_den = (1, 4)
            opponent_side = "MAGENTA"
        else:
            traps = {(9, 3), (8, 4), (9, 5)}
            enemy_den = (9, 4)
            opponent_side = "YELLOW"

        # Função para calcular um bônus baseado na distância ao den adversário
        def bonus_dist(pos):
            # Calcula a distância Manhattan até o den adversário
            dist = abs(pos[0] - enemy_den[0]) + abs(pos[1] - enemy_den[1])
            # Quanto menor a distância, maior o bônus (até um máximo quando dist = 0)
            return max(0, 10 - dist) * positional_weight

            # Variável para avaliar "corrida" para o den

        corr = False
        if self.corrida(board, side)[0]:
            if self.corrida(board, opponent_side)[0]:
                if self.corrida(board, side) <= self.corrida(board, opponent_side):
                    corr = True
            else:
                corr = True

        # Avalia cada peça do lado
        for piece in board.pieces[side]:
            if piece.state == "Dead":
                continue

            # Valor base igual ao rank
            value = piece.rank

            # Bônus para peças especiais
            if piece.name in ["Lion", "Tiger"]:
                value += bonus_L_T
            elif piece.name == "Rat":
                value += bonus_R

            # Penalização se a peça estiver sob ataque
            if piece.state == "under_attack":
                value *= 0.5

            # Se a peça estiver numa armadilha, penaliza seu valor
            r, c = piece.position
            if board.board[r][c] == '%':
                value *= trap_penalty

            # Bônus de mobilidade: número de movimentos legais disponíveis
            moves = rules.move(piece)
            mobility_bonus = len(moves) * mobility_factor
            value += mobility_bonus

            # Bônus posicional: mais perto do den adversário é melhor
            value += bonus_dist(piece.position)

            score += value
            possible_moves = possible_moves | set(moves)

        # Bônus adicional se o lado controla alguma posição de armadilha
        if traps & possible_moves:
            score += 5

        # Bônus adicional para cada peça adversária capturada
        for enemy in board.pieces[opponent_side]:
            if enemy.state == "Dead":
                score += enemy.rank * capture_bonus

        # Se a função "corrida" indicar que o lado tem a peça mais próxima do den adversário,
        # atribui uma vantagem decisiva.
        if self.corrida(board, side)[0]:
            total_score = 10000

        return score


