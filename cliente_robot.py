import socket
from time import sleep

# Configuração do socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 2025))
endereco_servidor = ("127.0.0.1", 2024)

def pular(altura):
    for _ in range(altura):
        mensagem = "controle;up"
        sock.sendto(mensagem.encode(), endereco_servidor)
        sleep(0.05)  # Pequena pausa para simular movimento

    for _ in range(altura):
        mensagem = "controle;down"
        sock.sendto(mensagem.encode(), endereco_servidor)
        sleep(0.05)

# Enviar comandos
try:
    while True:
        acao = input("Entre com o comando (up, down, left, right, jump, (jump,right), (jump,left) ou para sair (q): ").strip().lower()
        if acao == 'q':
            break

        if acao == 'jump':
            pular(10)
        else:
            mensagem = f"controle;{acao}"
            sock.sendto(mensagem.encode(), endereco_servidor)
finally:
    print("Fechando socket")
    sock.close()
