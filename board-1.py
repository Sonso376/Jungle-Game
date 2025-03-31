import pygame
from piece import Piece
import random
import math


class JungleGame:
    def __init__(self):
        pygame.init()
        self.cols = 7
        self.rows = 9
        self.base_cell_size = 70
        self.min_width = self.base_cell_size * self.cols
        self.min_height = self.base_cell_size * self.rows
        self.screen = pygame.display.set_mode((self.min_width, self.min_height), pygame.RESIZABLE)
        pygame.display.set_caption("Jungle Game")
        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.running = True
        self.selected_piece = None
        self.current_turn = "Player1"  # Player1 começa jogando
        self.game_mode = "Human vs AI"  # Modo de jogo padrão (pode ser alterado futuramente)
        self.difficulty = "medium"  # Pode ser "easy", "medium" ou "hard"
        self.emojis = self.load_emojis()
        self.river_cells = self.define_river()
        self.traps, self.dens = self.define_special_cells()
        self.setup_pieces()
        self.clock = pygame.time.Clock()
        self.needs_redraw = True
        self.ai_pending_move = False  # Flag para garantir que a IA joga apenas uma vez por turno
        self.move_history = []  # Armazena movimentos para desfazer corretamente
        self.main_loop()

    def load_emojis(self):
        return {
            "Elephant_Player1": "🐘",
            "Elephant_Player2": "🐘",
            "Lion_Player1": "🦁",
            "Lion_Player2": "🦁",
            "Tiger_Player1": "🐯",
            "Tiger_Player2": "🐯",
            "Leopard_Player1": "🐆",
            "Leopard_Player2": "🐆",
            "Wolf_Player1": "🐺",
            "Wolf_Player2": "🐺",
            "Dog_Player1": "🐶",
            "Dog_Player2": "🐶",
            "Cat_Player1": "🐱",
            "Cat_Player2": "🐱",
            "Rat_Player1": "🐭",
            "Rat_Player2": "🐭"
        }

    def define_river(self):
        return {(3, 1), (3, 2), (3, 4), (3, 5),
                (4, 1), (4, 2), (4, 4), (4, 5),
                (5, 1), (5, 2), (5, 4), (5, 5)}

    def define_special_cells(self):
        traps = {
            "Player1": {(0, 2), (1, 3), (0, 4)},
            "Player2": {(8, 2), (7, 3), (8, 4)}
        }
        dens = {
            "Player1": (0, 3),
            "Player2": (8, 3)
        }
        return traps, dens

    def setup_pieces(self):
        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]  # Reset do tabuleiro
        positions = {
            "Elephant": [(0, 6), (8, 0)],
            "Lion": [(0, 0), (8, 6)],
            "Tiger": [(0, 5), (8, 1)],
            "Leopard": [(2, 2), (6, 4)],
            "Wolf": [(2, 4), (6, 2)],
            "Dog": [(2, 6), (6, 0)],
            "Cat": [(1, 1), (7, 5)],
            "Rat": [(2, 0), (6, 6)]
        }

        for name, positions_list in positions.items():
            for i, pos in enumerate(positions_list):
                player = "Player1" if i == 0 else "Player2"
                self.board[pos[0]][pos[1]] = Piece(name, self.get_piece_rank(name), pos, player)

        print("✅ Peças inicializadas corretamente!")  # Depuração para verificar se as peças foram colocadas
        self.print_board_state()

    def get_piece_rank(self, name):
        ranks = {
            "Rat": 1, "Cat": 2, "Dog": 3, "Wolf": 4,
            "Leopard": 5, "Tiger": 6, "Lion": 7, "Elephant": 8
        }
        return ranks[name]

    def check_victory(self):
        print("✅ Verificando vitória...")
        if not self.running:
            return
        for player, den in self.dens.items():
            if self.board[den[0]][den[1]] is not None:
                print(f"🏆 {self.board[den[0]][den[1]].player} venceu entrando na toca do adversário!")
                self.running = False
                return

        player1_pieces = sum(1 for row in self.board for piece in row if piece and piece.player == "Player1")
        player2_pieces = sum(1 for row in self.board for piece in row if piece and piece.player == "Player2")

        if player1_pieces == 0:
            print("🏆 Player2 venceu! Todas as peças do Player1 foram eliminadas.")
            self.running = False
        elif player2_pieces == 0:
            print("🏆 Player1 venceu! Todas as peças do Player2 foram eliminadas.")
            self.running = False

    def is_valid_move(self, piece, start, end):
        r_start, c_start = start
        r_end, c_end = end

        if abs(r_start - r_end) + abs(c_start - c_end) > 1:
            print(f"⚠️ Movimento inválido detectado: {piece.name} tentou mover de {start} para {end}")
            return False

        if abs(r_start - r_end) + abs(c_start - c_end) == 1:
            if (r_end, c_end) in self.river_cells and piece.name != "Rat":
                return False
            return True

        if piece.name in ["Lion", "Tiger"]:
            if (r_start, c_start) in self.river_cells or (r_end, c_end) in self.river_cells:
                return False

            if r_start == r_end and abs(c_start - c_end) > 1:
                if all((r_start, c) in self.river_cells for c in range(min(c_start, c_end) + 1, max(c_start, c_end))):
                    if not any(self.board[r_start][c] and self.board[r_start][c].name == "Rat" for c in range(min(c_start, c_end) + 1, max(c_start, c_end))):
                        return True
            if c_start == c_end and abs(r_start - r_end) > 1:
                if all((r, c_start) in self.river_cells for r in range(min(r_start, r_end) + 1, max(r_start, r_end))):
                    if not any(self.board[r][c_start] and self.board[r][c_start].name == "Rat" for r in range(min(r_start, r_end) + 1, max(r_start, r_end))):
                        return True

        return False

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or not self.running:
            return self.evaluate_board()

        possible_moves = self.get_all_possible_moves("Player2" if maximizing_player else "Player1")
        if not possible_moves:
            return self.evaluate_board()

        if maximizing_player:
            max_eval = -math.inf
            for start, end in possible_moves:
                piece = self.board[start[0]][start[1]]
                if piece and self.is_valid_move(piece, start, end):
                    self.move_piece(start, end)
                    evaluation = self.minimax(depth - 1, alpha, beta, False)
                    self.undo_move(start, end)
                    max_eval = max(max_eval, evaluation)
                    alpha = max(alpha, evaluation)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = math.inf
            for start, end in possible_moves:
                piece = self.board[start[0]][start[1]]
                if piece and self.is_valid_move(piece, start, end):
                    self.move_piece(start, end)
                    evaluation = self.minimax(depth - 1, alpha, beta, True)
                    self.undo_move(start, end)
                    min_eval = min(min_eval, evaluation)
                    beta = min(beta, evaluation)
                    if beta <= alpha:
                        break
            return min_eval

    def ai_move(self):
        """Corrigido: Agora a IA avalia corretamente os movimentos."""
        if not self.running:
            return
        best_move = None
        best_value = -math.inf
        depth = {"easy": 1, "medium": 3, "hard": 5}[self.difficulty]

        possible_moves = self.get_all_possible_moves("Player2")
        if not possible_moves:
            return

        for start, end in possible_moves:
            piece = self.board[start[0]][start[1]]
            if piece and self.is_valid_move(piece, start, end):
                captured_piece = self.board[end[0]][end[1]]
                self.move_piece(start, end)
                move_value = self.minimax(depth - 1, -math.inf, math.inf, False)
                self.undo_move(start, end, captured_piece)

                if move_value > best_value:
                    best_value = move_value
                    best_move = (start, end)

        if best_move and self.running:
            piece = self.board[best_move[0][0]][best_move[0][1]]
            if piece:
                self.move_piece(best_move[0], best_move[1])
                self.ai_pending_move = False

    def evaluate_board(self):
        score = 0
        for row in self.board:
            for piece in row:
                if piece:
                    score += piece.rank if piece.player == "Player2" else -piece.rank
        return score

    def undo_move(self, start, end, captured_piece):
        """Corrigido: Restaura corretamente um movimento desfeito."""
        self.board[start[0]][start[1]] = self.board[end[0]][end[1]]
        self.board[end[0]][end[1]] = captured_piece
        self.board[start[0]][start[1]].position = start

    def get_all_possible_moves(self, player):
        moves = []
        for row in range(self.rows):
            for col in range(self.cols):
                piece = self.board[row][col]
                if piece and piece.player == player:
                    for r in range(self.rows):
                        for c in range(self.cols):
                            if self.is_valid_move(piece, piece.position, (r, c)):
                                moves.append(((row, col), (r, c)))
        return moves


    def move_piece(self, start, end):
        piece = self.board[start[0]][start[1]]
        target = self.board[end[0]][end[1]]

        if piece is None:
            print("⚠️ ERRO: Tentando mover uma peça inexistente!")
            return

        if target is not None and target.player == piece.player:
            print("⚠️ ERRO: Tentando capturar peça do mesmo jogador!")
            return

        if target is None or self.can_capture(piece, target):
            self.board[end[0]][end[1]] = piece
            self.board[start[0]][start[1]] = None
            piece.position = end

            if end in self.traps["Player1"] or end in self.traps["Player2"]:
                piece.rank = 0  # Reduz o rank para 0 enquanto estiver na armadilha
            else:
                piece.rank = self.get_piece_rank(piece.name)  # Recupera o rank original

            print("📌 Peça movida:", piece.name, "de", start, "para", end)
            self.print_board_state()  # Exibir o estado do tabuleiro após cada movimento
            self.check_victory()
            self.switch_turn()
            self.needs_redraw = True


    def switch_turn(self):
        if not self.running:
            return
        self.current_turn = "Player2" if self.current_turn == "Player1" else "Player1"
        print(f"🔄 Agora é a vez de {self.current_turn}")

        if self.current_turn == "Player2" and self.game_mode == "Human vs AI" and not self.ai_pending_move:
            self.ai_pending_move = True  # Marca que a IA precisa jogar


    def can_capture(self, attacker, defender):
        """Corrigido: Ajusta as regras de captura corretamente."""
        if attacker.player == defender.player:
            return False
        if attacker.name == "Rat" and defender.name == "Elephant":
            return attacker.position not in self.river_cells
        if attacker.name == "Elephant" and defender.name == "Rat":
            return False
        return attacker.rank >= defender.rank

    def handle_click(self, pos):
        """Corrigido: Garante que a seleção da peça seja feita corretamente."""
        window_width, window_height = self.screen.get_size()
        self.cell_size = min(window_width // self.cols, window_height // self.rows)
        col = pos[0] // self.cell_size
        row = pos[1] // self.cell_size

        if 0 <= row < self.rows and 0 <= col < self.cols:
            clicked_piece = self.board[row][col]

            if self.selected_piece:
                if self.is_valid_move(self.selected_piece, self.selected_piece.position, (row, col)):
                    self.move_piece(self.selected_piece.position, (row, col))
                self.selected_piece = None
            elif clicked_piece and clicked_piece.player == self.current_turn:
                self.selected_piece = clicked_piece

            self.needs_redraw = True

    def draw_board(self):
        """Corrigido: Melhora a exibição para evitar falhas gráficas."""
        window_width, window_height = self.screen.get_size()
        self.cell_size = min(window_width // self.cols, window_height // self.rows)
        self.screen.fill((0, 128, 0))

        try:
            font = pygame.font.SysFont("Segoe UI Emoji", int(self.cell_size * 0.8))
        except:
            font = pygame.font.SysFont("Arial", int(self.cell_size * 0.8))  # Fallback

        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)

                if (row, col) in self.river_cells:
                    pygame.draw.rect(self.screen, (0, 0, 255), rect)
                elif (row, col) in self.traps["Player1"] or (row, col) in self.traps["Player2"]:
                    pygame.draw.rect(self.screen, (255, 165, 0), rect)
                elif (row, col) in self.dens.values():
                    pygame.draw.rect(self.screen, (255, 0, 0), rect)

                if self.board[row][col]:
                    piece = self.board[row][col]
                    emoji_key = f"{piece.name}_{piece.player}"
                    emoji = self.emojis.get(emoji_key, "?")
                    text_surface = font.render(emoji, True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=(col * self.cell_size + self.cell_size // 2,
                                                              row * self.cell_size + self.cell_size // 2))
                    self.screen.blit(text_surface, text_rect)

        pygame.display.flip()

    def print_board_state(self):
        print("📌 Estado atual do tabuleiro:")
        for row in self.board:
            row_state = [piece.name if piece else "-" for piece in row]
            print(" ".join(row_state))

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_turn == "Player1":  # Apenas aceita jogadas humanas no turno correto
                        self.handle_click(event.pos)

            if self.ai_pending_move and self.current_turn == "Player2":
                self.ai_move()
                self.ai_pending_move = False  # Reseta a flag após a IA jogar

            self.draw_board()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    JungleGame()

