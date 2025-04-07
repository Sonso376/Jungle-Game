from board import Board
from rules import Rules
from string import ascii_uppercase
from minimax import AI
import time


def parse_input(pos_str):
    """
    Converte uma string de posição (ex: "A1") para coordenadas do tabuleiro (linha, coluna).
    
    Args:
        pos_str (str): String representando a posição no formato letra-número
        
    Returns:
        tuple: (linha, coluna) ou None se o formato for inválido
    """
    try:
        col = ord(pos_str[0].upper()) - ord('A') + 1
        row = int(pos_str[1])
        return row, col
    except:
        return None


def format_position(pos):
    """
    Converte coordenadas do tabuleiro (linha, coluna) para o formato letra-número.
    
    Args:
        pos (tuple): Coordenadas (linha, coluna)
        
    Returns:
        tuple: (linha, letra) representando a posição
    """
    row, col = pos
    return (row, ascii_uppercase[col - 1])


def find_piece_by_position(board, position, player):
    """
    Encontra uma peça na posição especificada para um determinado jogador.
    
    Args:
        board (Board): Tabuleiro do jogo
        position (tuple): Coordenadas (linha, coluna)
        player (str): Identificador do jogador
        
    Returns:
        Piece: A peça encontrada ou None se não houver nenhuma
    """
    for piece in board.pieces[player]:
        if piece.position == position and piece.state != "Dead":
            return piece
    return None


def run_pvp_game(board, rules, player_keys):
    """
    Executa o modo de jogo Jogador vs Jogador.
    
    Args:
        board (Board): Tabuleiro do jogo
        rules (Rules): Regras do jogo
        player_keys (dict): Mapeamento de jogadores para cores
    """
    print("Modo Jogador vs Jogador iniciado!")
    current_player = "Player1"
    opponent = "Player2"

    while True:
        board._place_pieces()
        board.display()
        print(f"{current_player}'s turn:")

        # Encontra todas as peças que podem se mover
        movable = []
        for piece in board.pieces[player_keys[current_player]]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                if moves:
                    movable.append((piece, moves))

        # Verifica se o jogador está imobilizado
        if not movable:
            print(f"{opponent} wins by immobilization!")
            break

        # Mostra as peças que podem se mover e seus possíveis movimentos
        for i, (piece, moves) in enumerate(movable):
            formatted_moves = [format_position(m) for m in moves]
            print(f"{i + 1}. {piece.name} at {format_position(piece.position)} can move to {formatted_moves}")

        try:
            # Solicita ao jogador que escolha uma peça
            choice = int(input("Select a piece to move (by number): ")) - 1
            piece, moves = movable[choice]

            # Mostra os movimentos possíveis para a peça escolhida
            print(f"Available moves for {piece.name} at {format_position(piece.position)}:")
            for i, pos in enumerate(moves):
                print(f"{i + 1}. {format_position(pos)}")
            
            # Solicita ao jogador que escolha um destino
            move_choice = int(input("Select destination (by number): ")) - 1
            new_position = moves[move_choice]

            # Verifica se há uma peça inimiga na posição de destino
            for enemy in board.pieces[player_keys[opponent]]:
                if enemy.position == new_position:
                    print(f"{piece.name} captures {enemy.name}!")
                    enemy.state = "Dead"
                    break

            # Move a peça e aplica os efeitos das armadilhas
            piece.position = new_position
            rules.trap_effects()

            # Verifica se houve vitória
            victory = rules.check_victory()
            if victory:
                return

            # Troca o jogador atual
            current_player, opponent = opponent, current_player

        except Exception as e:
            print(f"Invalid input: {e}")
            continue


def run_pvai_game(board, rules, player_keys, hplayer, aiplayer, ai, dificuldade, hard_type):
    """
    Executa o modo de jogo Jogador vs IA.
    
    Args:
        board (Board): Tabuleiro do jogo
        rules (Rules): Regras do jogo
        player_keys (dict): Mapeamento de jogadores para cores
        hplayer (str): Identificador do jogador humano
        aiplayer (str): Identificador da IA
        ai (AI): Instância da classe AI
        dificuldade (str): Nível de dificuldade da IA
        hard_type (str): Tipo de implementação para dificuldade "hard"
    """
    print("Modo Jogador vs IA iniciado!")
    # Vamos assumir que o Player1 é o humano e o player2 é a IA.
    current_player = "Player1"
    opponent = "Player2"

    while True:
        board._place_pieces()
        board.display()
        print(f"{current_player}'s turn:")

        # Encontra todas as peças que podem se mover
        movable = []
        for piece in board.pieces[player_keys[current_player]]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                if moves:
                    movable.append((piece, moves))

        # Verifica se o jogador está imobilizado
        if not movable:
            print(f"{opponent} wins by immobilization!")
            break

        if current_player == "Player1":
            # Turno do jogador humano
            for i, (piece, moves) in enumerate(movable):
                formatted_moves = [format_position(m) for m in moves]
                print(f"{i + 1}. {piece.name} at {format_position(piece.position)} can move to {formatted_moves}")

            try:
                # Solicita ao jogador que escolha uma peça
                choice = int(input("Select a piece to move (by number): ")) - 1
                piece, moves = movable[choice]

                # Mostra os movimentos possíveis para a peça escolhida
                print(f"Available moves for {piece.name} at {format_position(piece.position)}:")
                for i, pos in enumerate(moves):
                    print(f"{i + 1}. {format_position(pos)}")
                
                # Solicita ao jogador que escolha um destino
                move_choice = int(input("Select destination (by number): ")) - 1
                new_position = moves[move_choice]
            except Exception as e:
                print(f"Input inválido: {e}")
                continue
        else:
            # Turno da IA
            print("Turno da IA:")

            # Chama o método da IA para calcular o movimento de acordo com a dificuldade
            if dificuldade == "easy":
                move = ai.get_move_easy(board, rules, player_keys[current_player])
            elif dificuldade == "medium":
                move = ai.get_move_medium(board, rules, player_keys[current_player])
            elif dificuldade == "hard":
                if dificuldade == "hard":
                    if hard_type == "standard":
                        move = ai.get_move_hard(board, rules, player_keys[current_player])
                    elif hard_type == "iterative":
                        move = ai.get_move_hard_iterative(board, rules, player_keys[current_player], time_limit=10)
            elif dificuldade == "mcts":
                move = ai.get_move_mcts(board, rules, player_keys[current_player])

            if move is None:
                print("A IA não tem movimentos disponíveis!")
                break
            piece, new_position = move
            print(
                f"A IA escolheu mover {piece.name} de {format_position(piece.position)} para {format_position(new_position)}")

        # Verifica se há uma peça inimiga na posição de destino
        for enemy in board.pieces[player_keys[opponent]]:
            if enemy.position == new_position:
                print(f"{piece.name} captura {enemy.name}!")
                enemy.state = "Dead"
                break

        # Move a peça e aplica os efeitos das armadilhas
        piece.position = new_position
        rules.trap_effects()

        # Verifica se houve vitória
        if rules.check_victory():
            break

        # Troca o jogador atual
        current_player, opponent = opponent, current_player

def run_aivai_game(board, rules, player_keys, ai1, ai2, dificuldadep1, dificuldadep2, hard_type):
    """
    Executa o modo de jogo IA vs IA.
    
    Args:
        board (Board): Tabuleiro do jogo
        rules (Rules): Regras do jogo
        player_keys (dict): Mapeamento de jogadores para cores
        ai1 (AI): Instância da IA para o jogador 1
        ai2 (AI): Instância da IA para o jogador 2
        dificuldadep1 (str): Nível de dificuldade da IA 1
        dificuldadep2 (str): Nível de dificuldade da IA 2
        hard_type (str): Tipo de implementação para dificuldade "hard"
    """
    print("Modo IA vs IA iniciado!")
    board.ai_color = player_keys["Player1"]
    board.opponent_color = player_keys["Player2"]
    current_player = "Player1"
    opponent = "Player2"
    
    while True:
        board._place_pieces()
        board.display()
        print(f"{current_player}'s turn:")

        # Encontra todas as peças que podem se mover
        movable = []
        for piece in board.pieces[player_keys[current_player]]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                if moves:
                    movable.append((piece, moves))

        # Verifica se o jogador está imobilizado
        if not movable:
            print(f"{opponent} wins by immobilization!")
            break

        if current_player == "Player1":
            # Turno da IA Amarela
            print("Turno do Amarelo:")
            
            # Chama o método da IA1 para calcular o movimento de acordo com a dificuldade
            if dificuldadep1 == "easy":
                move = ai1.get_move_easy(board, rules, player_keys[current_player])
            elif dificuldadep1 == "medium":
                move = ai1.get_move_medium(board, rules, player_keys[current_player])
            elif dificuldadep1 == "hard":
                if dificuldadep1 == "hard":
                    if hard_type == "standard":
                        move = ai1.get_move_hard(board, rules, player_keys[current_player])
                    elif hard_type == "iterative":
                        move = ai1.get_move_hard_iterative(board, rules, player_keys[current_player], time_limit=10)
            elif dificuldadep1 == "mcts":
                move = ai1.get_move_mcts(board, rules, player_keys[current_player])

            if move is None:
                print("O Amarelo não tem movimentos disponíveis!")
                break
            piece, new_position = move
            print(f"O Amarelo escolheu mover {piece.name} de {format_position(piece.position)} para {format_position(new_position)}")
        else:
            # Turno da IA Magenta
            print("Turno do Magenta:")
            
            # Chama o método da IA2 para calcular o movimento de acordo com a dificuldade
            if dificuldadep2 == "easy":
                move = ai2.get_move_easy(board, rules, player_keys[current_player])
            elif dificuldadep2 == "medium":
                move = ai2.get_move_medium(board, rules, player_keys[current_player])
            elif dificuldadep2 == "hard":
                if dificuldadep2 == "hard":
                    if hard_type == "standard":
                        move = ai2.get_move_hard(board, rules, player_keys[current_player])
                    elif hard_type == "iterative":
                        move = ai2.get_move_hard_iterative(board, rules, player_keys[current_player], time_limit=10)
            elif dificuldadep2 == "mcts":
                move = ai2.get_move_mcts(board, rules, player_keys[current_player])

            if move is None:
                print("O Magenta não tem movimentos disponíveis!")
                break
            piece, new_position = move
            print(
                f"O Magenta escolheu mover {piece.name} de {format_position(piece.position)} para {format_position(new_position)}")

        # Verifica se há uma peça inimiga na posição de destino
        for i, enemy in enumerate(board.pieces[player_keys[opponent]]):
            if enemy.position == new_position:
                print(f"{piece.name} captura {enemy.name}!")
                board.pieces[player_keys[opponent]][i].state = "Dead"
                break

        # Move a peça e aplica os efeitos das armadilhas
        piece.position = new_position
        rules.trap_effects()

        # Verifica se houve vitória
        if rules.check_victory():
            break

        # Troca o jogador atual
        current_player, opponent = opponent, current_player
        
        # Pausa para visualização do estado do jogo
        time.sleep(2)


def main():
    """
    Função principal que inicializa o jogo e gerencia o fluxo principal.
    """
    board = Board()
    rules = Rules(board)

    player_keys = {
        "Player1": "YELLOW",
        "Player2": "MAGENTA"
    }

    print("Bem-vindo ao Jogo!")
    print("Escolhe o modo de jogo:")
    print("1 - Jogador vs Jogador")
    print("2 - Jogador vs IA")
    print("3 - IA vs IA")

    modo = input("Opção: ")

    if modo == "1":
        # Modo Jogador vs Jogador
        print("Modo Jogador vs Jogador selecionado.")
        run_pvp_game(board, rules, player_keys)

    elif modo == "2":
        # Modo Jogador vs IA
        print("Modo Jogador vs IA selecionado.")
        print("Escolhe a dificuldade da IA:")
        print("1 - Fácil")
        print("2 - Médio")
        print("3 - Difícil")
        print("4 - Monte Carlo Tree Search")

        dificuldade_input = input("Opção: ")

        # Define o nível de dificuldade baseado na entrada do usuário
        if dificuldade_input == "1":
            dificuldade = "easy"
        elif dificuldade_input == "2":
            dificuldade = "medium"
        elif dificuldade_input == "3":
            dificuldade = "hard"
        elif dificuldade_input == "4":
            dificuldade = "mcts"
        else:
            print("Dificuldade inválida. Selecionando 'Fácil' por padrão.")
            dificuldade = "easy"

        ai = AI()
        print(f"IA de dificuldade {dificuldade} selecionada.")
        print("Escolhe com qual cor quer jogar:")
        print("1. Amarelo")
        print("2. Magenta")

        # Solicita ao jogador que escolha seu lado
        i = 0
        while i not in [1, 2]:
            try:
                i = int(input("Opção: "))
            except Exception as e:
                print("Opção inválida, escolhe de novo!")
                continue
            if i not in [1, 2]:
                print("Opção inválida, escolhe de novo!")
            elif i == 1:
                # Jogador escolheu Amarelo
                board.ai_color = player_keys["Player2"]
                board.human_color = player_keys["Player1"]
                hplayer = "Player1"
                aiplayer = "Player2"
            else:
                # Jogador escolheu Magenta
                board.ai_color = player_keys["Player1"]
                board.human_color = player_keys["Player2"]
                aiplayer = "Player1"
                hplayer = "Player2"

        # Define o lado adversário da IA
        board.opponent_color = board.human_color

        # Inicia o jogo Jogador vs IA
        run_pvai_game(board, rules, player_keys, hplayer, aiplayer, ai, dificuldade, hard_type="standard")

    elif modo == "3":
        # Modo IA vs IA
        print("Modo de Ai vs Ai selecionado.")
        hard_type = "standard"

        # Configuração da IA Amarela
        print("Escolhe a dificuldade do Amarelo:")
        print("1 - Fácil")
        print("2 - Médio")
        print("3 - Difícil")
        print("4 - Monte Carlo Tree Search")
        dificuldade_input = input("Opção: ")

        if dificuldade_input == "1":
            dificuldade1 = "easy"
        elif dificuldade_input == "2":
            dificuldade1 = "medium"
        elif dificuldade_input == "3":
            dificuldade1 = "hard"
            # Configuração adicional para dificuldade "hard"
            print("Escolha a implementação para 'hard':")
            print("1 - Hard sem iterative deepening")
            print("2 - Hard com iterative deepening")
            hard_opcao = input("Opção: ")
            if hard_opcao == "1":
                hard_type = "standard"
            elif hard_opcao == "2":
                hard_type = "iterative"
            else:
                print("Opção inválida, usando Hard sem iterative deepening por padrão.")
                hard_type = "standard"
        elif dificuldade_input == "4":
            dificuldade1 = "mcts"
        else:
            print("Dificuldade inválida. Selecionando 'Fácil' por padrão.")
            dificuldade1 = "easy"

        # Configuração da IA Magenta
        print("Escolhe a dificuldade do Magenta:")
        print("1 - Fácil")
        print("2 - Médio")
        print("3 - Difícil")
        print("4 - Monte Carlo Tree Search")
        dificuldade_input = input("Opção: ")

        if dificuldade_input == "1":
            dificuldade2 = "easy"
        elif dificuldade_input == "2":
            dificuldade2 = "medium"
        elif dificuldade_input == "3":
            dificuldade2 = "hard"
            # Configuração adicional para dificuldade "hard"
            print("Escolha a implementação para 'hard':")
            print("1 - Hard sem iterative deepening")
            print("2 - Hard com iterative deepening")
            hard_opcao = input("Opção: ")
            if hard_opcao == "1":
                hard_type = "standard"
            elif hard_opcao == "2":
                hard_type = "iterative"
            else:
                print("Opção inválida, usando Hard sem iterative deepening por padrão.")
                hard_type = "standard"
        elif dificuldade_input == "4":
            dificuldade2 = "mcts"
        else:
            print("Dificuldade inválida. Selecionando 'Fácil' por padrão.")
            dificuldade2 = "easy"

        # Inicializa as IAs
        ai1 = AI()
        print(f"Dificuldade {dificuldade1} selecionada para o Amarelo.")
        ai2 = AI()
        print(f"Dificuldade {dificuldade2} selecionada para o Magenta.")

        # Inicia o jogo IA vs IA
        run_aivai_game(board, rules, player_keys, ai1, ai2, dificuldade1, dificuldade2, hard_type)

    else:
        print("Opção de modo inválida.")


if __name__ == "__main__":
    main()