import random
import math
from board import Board
from piece import get_pieces
import time

class AI:
    """
    Classe que implementa diferentes algoritmos de IA para jogar o jogo.
    Inclui várias implementações do algoritmo minimax e Monte Carlo Tree Search.
    """
    def __init__(self):
        """
        Inicializa a IA com uma tabela de transposição vazia.
        A tabela de transposição é usada para armazenar avaliações
        de estados já analisados para evitar recálculos.
        """
        self.transposition_table = {}  # Inicializa a tabela de transposição

    def compute_hash(self, board):
        """
        Gera uma chave imutável para o estado atual do tabuleiro, baseada nas posições,
        nomes e estados das peças.
        
        Args:
            board (Board): O tabuleiro para o qual gerar a chave
            
        Returns:
            tuple: Uma chave única representando o estado do tabuleiro
        """
        key_parts = []
        # Ordena as chaves para ter consistência (por exemplo, YELLOW e MAGENTA)
        for side in sorted(board.pieces.keys()):
            # Ordena as peças por nome para ter uma ordem fixa
            for piece in sorted(board.pieces[side], key=lambda p: p.name):
                key_parts.append((piece.name, piece.position, piece.state))
        return tuple(key_parts)


    def get_move_easy(self, board, rules, color):
        """
        Implementa uma IA de nível fácil que escolhe movimentos aleatórios.
        
        Args:
            board (Board): O estado atual do tabuleiro
            rules (Rules): As regras do jogo
            color (str): A cor das peças da IA ("YELLOW" ou "MAGENTA")
            
        Returns:
            tuple: (peça, nova_posição) representando o movimento escolhido
        """
        moves = []
        for piece in board.pieces[color]:
            moves += [(piece, rules.move(piece))]
        m = moves[random.randint(0, len(moves) - 1)]
        p = m[0]
        move = m[1][random.randint(0, len(m[1]) - 1)]
        return (p, move)

    def get_move_medium(self, board, rules, color):
        """
        Implementa uma IA de nível médio que usa o algoritmo minimax
        com profundidade 2 para avaliar movimentos.
        
        Args:
            board (Board): O estado atual do tabuleiro
            rules (Rules): As regras do jogo
            color (str): A cor das peças da IA ("YELLOW" ou "MAGENTA")
            
        Returns:
            tuple: (peça, nova_posição) representando o movimento escolhido
        """
        best_move = None
        best_score = float('-inf')
        # Seleciona o melhor movimento utilizando minimax com depth 2.
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
        """
        Implementa uma IA de nível difícil que usa o algoritmo minimax
        com poda alfa-beta e profundidade 4.
        
        Args:
            board (Board): O estado atual do tabuleiro
            rules (Rules): As regras do jogo
            color (str): A cor das peças da IA ("YELLOW" ou "MAGENTA")
            
        Returns:
            tuple: (peça, nova_posição) representando o movimento escolhido
        """
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
        Implementa uma IA que usa iterative deepening (aprofundamento iterativo)
        com minimax e poda alfa-beta.
        
        O método tenta profundidades sucessivas até o tempo limite ser alcançado.
        
        Args:
            board (Board): O estado atual do tabuleiro
            rules (Rules): As regras do jogo
            color (str): A cor das peças da IA ("YELLOW" ou "MAGENTA")
            time_limit (int): Limite de tempo em segundos
            
        Returns:
            tuple: (peça, nova_posição) representando o melhor movimento encontrado
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
        Implementa uma versão do algoritmo Monte Carlo Tree Search (MCTS).
        MCTS é baseado em simulações aleatórias para avaliar estados do jogo.
        
        Args:
            board (Board): O estado atual do tabuleiro
            rules (Rules): As regras do jogo
            color (str): A cor das peças da IA ("YELLOW" ou "MAGENTA")
            iterations (int): Número de iterações de simulação
            simulation_depth (int): Número máximo de movimentos na fase de simulação
            
        Returns:
            tuple: (peça, nova_posição) representando o melhor movimento encontrado
        """

        class Node:
            """
            Classe interna que representa um nó na árvore de busca MCTS.
            Armazena o estado do tabuleiro, estatísticas de visitas/vitórias,
            e gerencia os nós filhos e movimentos não explorados.
            """
            def __init__(self, board, move=None, parent=None, player=None):
                """
                Inicializa um nó da árvore MCTS.
                
                Args:
                    board (Board): Estado do tabuleiro neste nó
                    move (tuple): Movimento que levou a este estado
                    parent (Node): Nó pai na árvore
                    player (str): Jogador que realizou o movimento
                """
                self.board = board
                self.move = move  # Movimento que levou a esse estado (tuple: (piece, move))
                self.parent = parent
                self.player = player  # Jogador que realizou esse movimento
                self.children = []
                self.untried_moves = self.get_all_moves(board, player)
                self.visits = 0
                self.wins = 0

            def get_all_moves(self, board, player):
                """
                Obtém todos os movimentos possíveis para o jogador neste estado.
                
                Args:
                    board (Board): Estado do tabuleiro
                    player (str): Jogador atual
                    
                Returns:
                    list: Lista de movimentos possíveis
                """
                moves = []
                # Para cada peça do jogador, obtém todos os movimentos legais
                for piece in board.pieces[player]:
                    if piece.state != "Dead":
                        for m in rules.move(piece):
                            moves.append((piece, m))
                return moves

            def UCT(self, exploration=1.41):
                """
                Calcula o valor UCT (Upper Confidence Bound for Trees) do nó.
                Este valor balanceia exploração e aproveitamento na busca.
                
                Args:
                    exploration (float): Parâmetro de exploração
                    
                Returns:
                    float: Valor UCT do nó
                """
                # Se não houver visitas, retorne infinito para forçar exploração
                if self.visits == 0:
                    return float('inf')
                return self.wins / self.visits + exploration * math.sqrt(math.log(self.parent.visits) / self.visits)

        def select(node):
            """
            Seleciona um nó para expansão usando UCT.
            Desce na árvore até encontrar um nó com movimentos não explorados
            ou um nó folha.
            
            Args:
                node (Node): Nó raiz para iniciar a seleção
                
            Returns:
                Node: Nó selecionado para expansão
            """
            # Seleciona recursivamente o filho com maior UCT até encontrar um nó com movimentos não explorados
            while node.untried_moves == [] and node.children:
                node = max(node.children, key=lambda child: child.UCT())
            return node

        def expand(node):
            """
            Expande o nó selecionado adicionando um novo filho.
            
            Args:
                node (Node): Nó a ser expandido
                
            Returns:
                Node: Novo nó filho
            """
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
            """
            Realiza uma simulação aleatória a partir do estado do nó.
            
            Args:
                node (Node): Nó a partir do qual simular
                
            Returns:
                int: 1 para vitória, 0 para derrota
            """
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
            """
            Atualiza as estatísticas do nó e de seus ancestrais com o resultado da simulação.
            
            Args:
                node (Node): Nó a partir do qual propagar
                result (int): Resultado da simulação (1 para vitória, 0 para derrota)
            """
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