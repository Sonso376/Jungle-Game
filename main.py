from board import Board
from rules import Rules
from string import ascii_uppercase
from minimax import AI
import time

def parse_input(pos_str):
    try:
        col = ord(pos_str[0].upper()) - ord('A') + 1
        row = int(pos_str[1])
        return row, col
    except:
        return None


def format_position(pos):
    row, col = pos
    return (row, ascii_uppercase[col - 1])


def find_piece_by_position(board, position, player):
    for piece in board.pieces[player]:
        if piece.position == position and piece.state != "Dead":
            return piece
    return None


def run_pvp_game(board, rules, player_keys): # Lógica do Jogador vs Jogador
    print("Modo Jogador vs Jogador iniciado!")
    current_player = "Player1"
    opponent = "Player2"

    while True:
        board._place_pieces()
        board.display()
        print(f"\n{current_player}'s turn")

        movable = []
        for piece in board.pieces[player_keys[current_player]]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                if moves:
                    movable.append((piece, moves))

        if not movable:
            print(f"{opponent} wins by immobilization!")
            break

        for i, (piece, moves) in enumerate(movable):
            formatted_moves = [format_position(m) for m in moves]
            print(f"{i + 1}. {piece.name} at {format_position(piece.position)} can move to {formatted_moves}")

        try:
            choice = int(input("Select a piece to move (by number): ")) - 1
            piece, moves = movable[choice]

            print(f"Available moves for {piece.name} at {format_position(piece.position)}:")
            for i, pos in enumerate(moves):
                print(f"{i + 1}. {format_position(pos)}")
            move_choice = int(input("Select destination (by number): ")) - 1
            new_position = moves[move_choice]


            for enemy in board.pieces[player_keys[opponent]]:
                if enemy.position == new_position:
                    print(f"{piece.name} captures {enemy.name}!")
                    enemy.state = "Dead"
                    break

            piece.position = new_position
            rules.trap_effects()

            victory = rules.check_victory()
            if victory:
                return

            current_player, opponent = opponent, current_player

        except Exception as e:
            print(f"Invalid input: {e}")
            continue


def run_pvai_game(board, rules, player_keys,hplayer, aiplayer, ai, dificuldade):
    print("Modo Jogador vs IA iniciado!")
    current_player="Player1"
    opponent="Player2"
    while True:
        board._place_pieces()
        board.display()
        print(f"\n{current_player}'s turn")

        movable = []
        for piece in board.pieces[player_keys[current_player]]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                if moves:
                    movable.append((piece, moves))

        if not movable:
            print(f"{opponent} wins by immobilization!")
            break

        if current_player == hplayer:
            # Turno do jogador humano (semelhante ao que já estava implementado)
            for i, (piece, moves) in enumerate(movable):
                formatted_moves = [format_position(m) for m in moves]
                print(f"{i + 1}. {piece.name} at {format_position(piece.position)} can move to {formatted_moves}")

            try:
                choice = int(input("Select a piece to move (by number): ")) - 1
                piece, moves = movable[choice]

                print(f"Available moves for {piece.name} at {format_position(piece.position)}:")
                for i, pos in enumerate(moves):
                    print(f"{i + 1}. {format_position(pos)}")
                move_choice = int(input("Select destination (by number): ")) - 1
                new_position = moves[move_choice]
            except Exception as e:
                print(f"Input inválido: {e}")
                continue
        else:
            # Turno da IA
            print("Turno da IA:")

            """ 
            Chama o método da IA para calcular o movimento.
            É importante que o método da IA considere apenas as peças da IA.
            """
            if dificuldade=="easy":
                move = ai.get_move_easy(board, rules, player_keys[current_player])
            elif dificuldade=="medium":
                move=ai.get_move_medium(board,rules,player_keys[current_player])
            elif dificuldade=="hard":
                move=ai.get_move_hard(board,rules,player_keys[current_player])
            if move is None:
                print("A IA não tem movimentos disponíveis!")
                break
            piece, new_position = move
            print(
                f"A IA escolheu mover {piece.name} de {format_position(piece.position)} para {format_position(new_position)}")

            # Verifica se o movimento resulta numa captura
        for i, enemy in enumerate(board.pieces[player_keys[opponent]]):
            if enemy.position == new_position:
                print(f"{piece.name} captura {enemy.name}!")
                board.pieces[player_keys[opponent]][i].state = "Dead"
                break

        piece.position = new_position
        rules.trap_effects()

        if rules.check_victory():
            break

        current_player, opponent = opponent, current_player


def run_aivai_game(board, rules, player_keys, ai1, ai2 , dificuldadep1,dificuldadep2):
    print("Modo IA vs IA iniciado!")
    current_player="Player1"
    opponent="Player2"
    while True:
        board._place_pieces()
        board.display()
        print(f"\n{current_player}'s turn")

        movable = []
        for piece in board.pieces[player_keys[current_player]]:
            if piece.state != "Dead":
                moves = rules.move(piece)
                if moves:
                    movable.append((piece, moves))

        if not movable:
            print(f"{opponent} wins by immobilization!")
            break

        if current_player == "Player1":
            print("Turno do Amarelo:")
            if dificuldadep1=="easy":
                move = ai1.get_move_easy(board, rules, player_keys[current_player])
            elif dificuldadep1=="medium":
                move=ai1.get_move_medium(board,rules,player_keys[current_player])
            if move is None:
                print("O Amarelo não tem movimentos disponíveis!")
                break
            piece, new_position = move
            print(f"O Amarelo escolheu mover {piece.name} de {format_position(piece.position)} para {format_position(new_position)}")
        else:
            # Turno da IA
            print("Turno do Magenta:")

            """ 
            Chama o método da IA para calcular o movimento.
            É importante que o método da IA considere apenas as peças da IA.
            """
            if dificuldadep2=="easy":
                move = ai2.get_move_easy(board, rules, player_keys[current_player])
            elif dificuldadep2=="medium":
                move=ai2.get_move_medium(board,rules,player_keys[current_player])
            if move is None:
                print("O Magenta não tem movimentos disponíveis!")
                break
            piece, new_position = move
            print(
                f"O Magenta escolheu mover {piece.name} de {format_position(piece.position)} para {format_position(new_position)}")

            # Verifica se o movimento resulta numa captura
        for i, enemy in enumerate(board.pieces[player_keys[opponent]]):
            if enemy.position == new_position:
                print(f"{piece.name} captura {enemy.name}!")
                board.pieces[player_keys[opponent]][i].state = "Dead"
                break

        piece.position = new_position
        rules.trap_effects()

        if rules.check_victory():
            break

        current_player, opponent = opponent, current_player
        time.sleep(2)

def main():
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
        print("Modo Jogador vs Jogador selecionado.")
        run_pvp_game(board, rules, player_keys)

    elif modo == "2":
        print("Modo Jogador vs IA selecionado.")
        print("Escolhe a dificuldade da IA:")
        print("1 - Fácil")
        print("2 - Médio")
        print("3 - Difícil")

        dificuldade_input = input("Opção: ")

        if dificuldade_input == "1":
            dificuldade = "easy"
        elif dificuldade_input == "2":
            dificuldade = "medium"
        elif dificuldade_input == "3":
            dificuldade = "hard"
        else:
            print("Dificuldade inválida. Selecionando 'Fácil' por padrão.")
            dificuldade = "easy"

        ai = AI()

        print(f"IA de dificuldade {dificuldade} selecionada.")
        print("Escolhe com qual cor quer jogar:")
        print("1. Amarelo")
        print("2. Magenta")
        i=0
        while (i!=1 and i!=2):
            i=int(input("Opção: "))
            if i!=1 and i!=2:
                print("Opção inválida, escolhe denovo!")
            elif i==1:
                board.ai_color = player_keys["Player2"]
                board.human_color = player_keys["Player1"]
                hplayer="Player1"
                aiplayer="Player2"
            else:
                board.ai_color = player_keys["Player1"]
                board.human_color = player_keys["Player2"]
                aiplayer="Player1"
                hplayer="Player2"

        # Define as cores da IA e do jogador humano.
        # Isto já era feito antes, mas pode ser útil para termos acesso direto dentro da lógica da IA.
        board.opponent_color = board.human_color

        run_pvai_game(board, rules, player_keys, hplayer, aiplayer, ai, dificuldade)
    elif modo=="3":
        print("Modo de Ai vs Ai selecionado.")
        print("Escolhe a dificuldade do Amarelo:")
        print("1 - Fácil")
        print("2 - Médio")
        print("3 - Difícil")
        dificuldade_input = input("Opção: ")

        if dificuldade_input == "1":
            dificuldade1 = "easy"
        elif dificuldade_input == "2":
            dificuldade1 = "medium"
        elif dificuldade_input == "3":
            dificuldade1 = "hard"
        else:
            print("Dificuldade inválida. Selecionando 'Fácil' por padrão.")
            dificuldade1 = "easy"
        ai1=AI()
        print(f"Dificuldade {dificuldade1} selecionada para o Amarelo.")
        print("Escolhe a dificuldade do Magenta:")
        print("1 - Fácil")
        print("2 - Médio")
        print("3 - Difícil")
        dificuldade_input = input("Opção: ")

        if dificuldade_input == "1":
            dificuldade2 = "easy"
        elif dificuldade_input == "2":
            dificuldade2 = "medium"
        elif dificuldade_input == "3":
            dificuldade2 = "hard"
        else:
            print("Dificuldade inválida. Selecionando 'Fácil' por padrão.")
            dificuldade2 = "easy"
        ai2=AI()
        print(f"Dificuldade {dificuldade2} selecionada para o Magenta.")
    run_aivai_game(board, rules, player_keys, ai1, ai2, dificuldade1, dificuldade2)

if __name__ == "__main__":
    main()