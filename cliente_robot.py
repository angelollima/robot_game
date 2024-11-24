import socket

# Set up the socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
endereco_servidor = ("127.0.0.1", 2024)


def enviar_comando(acao):
    mensagem = f"token;controle;{acao}"
    sock.sendto(mensagem.encode(), endereco_servidor)


try:
    while True:
        print("Escolha uma ação:")
        print("1 - Mover (up, down, left, right)")
        print("2 - Correr (run + direção)")
        print("3 - Pular (up + direção)")
        print("4 - Esquivar (dodge)")
        print("5 - Sair")
        opcao = input("Digite a opção: ").strip()

        if opcao == "1":
            direcao = input("Entre com a direção (up, down, left, right): ").strip().lower()
            enviar_comando(direcao)
        elif opcao == "2":
            direcao = input("Entre com a direção (left, right): ").strip().lower()
            enviar_comando(f"run,{direcao}")
        elif opcao == "3":
            direcao = input("Entre com a direção adicional (left, right ou vazio): ").strip().lower()
            comando = f"up,{direcao}" if direcao else "up"
            enviar_comando(comando)
        elif opcao == "4":
            direcao = input("Entre com a direção para esquivar (left, right): ").strip().lower()
            enviar_comando(f"dodge,{direcao}")
        elif opcao == "5":
            break
        else:
            print("Opção inválida!")
finally:
    print("Fechando socket")
    sock.close()
