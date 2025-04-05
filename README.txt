Implementar loading screen ou o screen inicial
Implementar draw mechanic

Sistema de pontos
    -> Negamax, num sentido em que podem começar todos com 36 pontos. Há medidade que vao perdendo peças, um lado diminui, enquanto o outro aumenta.
        -> Supondo que a nossa peça fica underattack, podemos colocar que o adversario ganha pontos com isso e nos perdemos!

AI - Minimax, com alphabeta cuts
Threading() -> Modulo de python que podemos implementar caso o IA esta muito lento
    pip install threading -> para instalar, depois a documentação e exemplos podem ir docs do module/stackoverflow!

#penso que esta tudo certo, just to be sure
Verificar se está tudo correto, com as regras certas. link para verificar ->
(https://www.ymimports.com/pages/how-to-play-jungle?srsltid=AfmBOorSocHdPQB5nCIHHi1vHE3hzO0u7GbzqFv83jI46SHxSAi1-UeG)

As peças tem states, por exemplo, se eu me mover neste turno para perto de uma peça inimiga de rank maior, a nossa peça vai ficar com o state under_attack
    -> pfv verifiquem se essa lógica está correta!

