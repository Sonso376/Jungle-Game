from board import Board
from rules import Rules
from string import ascii_uppercase
from minimax import AI

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
        print(f"\\n{current_player}'s turn")

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


def run_pvai_game(board, rules, player_keys, ai):
    print("Modo Jogador vs IA iniciado!")
    # Vamos assumir que o Player1 é o humano e o player2 é a IA.
    current_player = "Player1"
    opponent = "Player2"

    while True:
        board._place_pieces()
        board.display()
        print(f"\\n{current_player}'s turn")

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
            move = ai.get_move_easy(board, rules, player_keys[current_player])
            if move is None:
                print("A IA não tem movimentos disponíveis!")
                break
            piece, new_position = move
            print(
                f"A IA escolheu mover {piece.name} de {format_position(piece.position)} para {format_position(new_position)}")

            # Verifica se o movimento resulta numa captura
        for enemy in board.pieces[player_keys[opponent]]:
            if enemy.position == new_position:
                print(f"{piece.name} captura {enemy.name}!")
                enemy.state = "Dead"
                break

        piece.position = new_position
        rules.trap_effects()

        if rules.check_victory():
            break

        current_player, opponent = opponent, current_player


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

        # Define as cores da IA e do jogador humano.
        # Isto já era feito antes, mas pode ser útil para termos acesso direto dentro da lógica da IA.
        board.ai_color = player_keys["Player2"]  # Exemplo: "MAGENTA"
        board.human_color = player_keys["Player1"]  # Exemplo: "YELLOW"
        board.opponent_color = board.human_color

        run_pvai_game(board, rules, player_keys, ai)


if __name__ == "__main__":
    main()