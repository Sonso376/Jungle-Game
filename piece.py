# pieces.py
from colorama import Back, Style

class Piece:
    """
    Classe que representa uma peça (animal) do jogo.
    Cada peça tem um nome, símbolo, posição, rank e outras propriedades.
    """
    def __init__(self, name: str, model_str: str, position: tuple, rank: int, movement: int, side: str):
        """
        Inicializa uma nova peça do jogo.
        
        Args:
            name (str): Nome do animal (ex: "Elephant", "Lion", etc.)
            model_str (str): Emoji ou símbolo que representa o animal
            position (tuple): Posição inicial (linha, coluna) no tabuleiro
            rank (int): Valor numérico da força do animal (1-8)
            movement (int): Tipo de movimento permitido
            side (str): Lado ao qual a peça pertence ("Player1" ou "Player2")
        """
        self.name = name
        self.model_str = model_str
        self.position = position
        self.rank = rank
        self.movement = movement
        self.side = side
        self.hp = rank  # Pontos de vida inicialmente iguais ao rank
        self.state = "Alive"  # Estado inicial (Alive, under_attack, can_attack, Dead)
        self.color = "YELLOW" if self.side == "Player1" else "MAGENTA"  # Cor baseada no lado

    def get_colored_model(self):
        """
        Retorna o símbolo da peça com a coloração apropriada de acordo com o lado.
        
        Returns:
            str: Símbolo da peça colorido
        """
        if not self.state: 
            return " "

        if self.side == "Player1":
            return f"{Back.YELLOW}{self.model_str}{Style.RESET_ALL}"
        elif self.side == "Player2":
            return f"{Back.MAGENTA}{self.model_str}{Style.RESET_ALL}"
        return self.model_str

def get_pieces():
    """
    Cria e retorna todas as peças iniciais do jogo, organizadas por lado.
    
    Returns:
        dict: Dicionário com as peças do jogo, separadas por cor
    """
    return {
        "YELLOW": [  # Peças do Player1 (amarelo)
            Piece("Elephant", "🐘", (3, 7), 8, 1, "Player1"),  # Elefante: rank 8, movimento simples
            Piece("Lion", "🦁", (1, 1), 7, 2, "Player1"),      # Leão: rank 7, pode pular rio
            Piece("Tiger", "🐯", (1, 7), 6, 2, "Player1"),     # Tigre: rank 6, pode pular rio
            Piece("Leopard", "🐆", (3, 3), 5, 1, "Player1"),   # Leopardo: rank 5, movimento simples
            Piece("Wolf", "🐺", (3, 5), 4, 1,"Player1"),       # Lobo: rank 4, movimento simples
            Piece("Dog", "🐶", (2, 2), 3, 1,"Player1"),        # Cão: rank 3, movimento simples
            Piece("Cat", "🐱", (2, 6), 2, 1,"Player1"),        # Gato: rank 2, movimento simples
            Piece("Rat", "🐭", (3, 1), 1, 3,"Player1"),        # Rato: rank 1, pode nadar no rio e derrotar o elefante
        ],
        "MAGENTA": [  # Peças do Player2 (magenta)
            Piece("Elephant", "🐘", (7, 1), 8, 1,"Player2"),   # Elefante: rank 8, movimento simples
            Piece("Lion", "🦁", (9, 7), 7, 2,"Player2"),       # Leão: rank 7, pode pular rio (posição corrigida para 9,7)
            Piece("Tiger", "🐯", (9, 1), 6, 2,"Player2"),      # Tigre: rank 6, pode pular rio
            Piece("Leopard", "🐆", (7, 5), 5, 1,"Player2"),    # Leopardo: rank 5, movimento simples
            Piece("Wolf", "🐺", (7, 3), 4, 1,"Player2"),       # Lobo: rank 4, movimento simples
            Piece("Dog", "🐶", (8, 6), 3, 1,"Player2"),        # Cão: rank 3, movimento simples
            Piece("Cat", "🐱", (8, 2), 2, 1,"Player2"),        # Gato: rank 2, movimento simples
            Piece("Rat", "🐭", (7, 7), 1, 3,"Player2"),        # Rato: rank 1, pode nadar no rio e derrotar o elefante (posição corrigida para 7,7)
        ]
    }