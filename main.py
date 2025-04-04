from board import Board
from rules import Rules
from string import ascii_uppercase


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

def main():
    board = Board()
    rules = Rules(board)

    player_keys = {
        "Player1": "YELLOW",
        "Player2": "MAGENTA"
    }

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
            print(f"{i+1}. {piece.name} at {format_position(piece.position)} can move to {formatted_moves}")

        try:
            choice = int(input("Select a piece to move (by number): ")) - 1
            piece, moves = movable[choice]

            print(f"Available moves for {piece.name} at {format_position(piece.position)}:")
            for i, pos in enumerate(moves):
                print(f"{i+1}. {format_position(pos)}")
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

if __name__ == "__main__":
    main()