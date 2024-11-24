import socket

# Set up the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 2025))
endereco_servidor = ("127.0.0.1", 2024)

# Send commands
try:
    while True:
        acao = input("Entre com o comando (up, down, left, right) ou para sair (q): ").strip().lower()
        if acao == 'q':
            break
        mensagem = f"controle;{acao}"
        if mensagem:
            sent = sock.sendto(mensagem.encode(), endereco_servidor)
finally:
    print("Fechando socket")
    sock.close()
