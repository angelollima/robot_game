import socket
from time import sleep

# Configuração do socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 2025))
endereco_servidor = ("127.0.0.1", 2024)
distancia = 10
altura = 10


def jump():
    for _ in range(altura):
        mensagem = "controle;up"
        sock.sendto(mensagem.encode(), endereco_servidor)
        sleep(0.05)

    for _ in range(altura):
        mensagem = "controle;down"
        sock.sendto(mensagem.encode(), endereco_servidor)
        sleep(0.05)


def jump_with_direction(direcao):
    if direcao not in ["right", "left"]:
        print("Direção inválida para jump. Use 'right' ou 'left'.")
        return

    for _ in range(altura):
        mensagem = "controle;up"
        sock.sendto(mensagem.encode(), endereco_servidor)
        sleep(0.05)

    for _ in range(distancia // 2):
        mensagem = f"controle;{direcao}"
        sock.sendto(mensagem.encode(), endereco_servidor)
        sleep(0.05)

    for _ in range(altura):
        mensagem = "controle;down"
        sock.sendto(mensagem.encode(), endereco_servidor)
        sleep(0.05)


def run(comando, velocidade):
    try:
        # Converter velocidade para número
        velocidade = float(velocidade)
        if velocidade <= 0:
            print("Velocidade deve ser maior que zero.")
            return

        # Movimento na direção especificada
        for _ in range(distancia):
            mensagem = f"controle;{comando}"
            sock.sendto(mensagem.encode(), endereco_servidor)
            sleep(
                1 /
                velocidade)  # Ajustar o tempo de espera com base na velocidade
    except ValueError:
        print("Velocidade inválida. Use um número válido.")


def dodge(comando):
    # Validar comando
    if comando not in ["right", "left"]:
        print("Comando inválido para dodge. Use 'right' ou 'left'.")
        return

    # Determinar direção oposta
    direcao_oposta = "left" if comando == "right" else "right"

    # Movimento na direção especificada
    for _ in range(distancia):
        mensagem = f"controle;{comando}"
        sock.sendto(mensagem.encode(), endereco_servidor)
        sleep(0.05)

    # Movimento na direção oposta
    for _ in range(distancia):
        mensagem = f"controle;{direcao_oposta}"
        sock.sendto(mensagem.encode(), endereco_servidor)
        sleep(0.05)


# Enviar comandos
try:
    while True:
        acao = input(
            "Entre com o comando (up, down, left, right, jump, (dodge,right), (dodge,left) ou para sair (q)): "
        ).strip().lower()
        if acao == 'q':
            break

        if acao == 'jump':
            jump(10)
        elif acao.startswith("dodge,"):
            _, direcao = acao.split(",")
            dodge(direcao)
        elif acao.startswith("run,"):
            try:
                _, direcao, velocidade = acao.split(",")
                run(direcao, velocidade)
            except ValueError:
                print("Comando inválido. Use: run,<direcao>,<velocidade>")
        elif acao.startswith("jump,"):
            try:
                _, direcao = acao.split(",")
                jump_with_direction(direcao)
            except ValueError:
                print("Comando inválido. Use: jump,<direcao>")
        else:
            mensagem = f"controle;{acao}"
            sock.sendto(mensagem.encode(), endereco_servidor)
finally:
    print("Fechando socket")
    sock.close()
