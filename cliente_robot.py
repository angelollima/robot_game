import socket
import time
import logging
from typing import Optional, List

class RobotSocketController:
    """
    Controlador de robô utilizando comunicação via socket UDP.

    Gerencia movimentos e comandos de controle através de uma conexão UDP.
    """

    def __init__(
        self,
        server_host: str = "127.0.0.1",
        server_port: int = 2024,
        local_port: int = 2025,
        distancia: int = 10,
        altura: int = 10
    ):
        """
        Inicializa o controlador do robô.

        Args:
            server_host (str): Endereço IP do servidor.
            server_port (int): Porta do servidor.
            local_port (int): Porta local para bind do socket.
            distancia (int): Distância padrão de movimento.
            altura (int): Altura padrão de salto.
        """
        # Configuração de logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Configurações de movimento
        self.distancia = distancia
        self.altura = altura

        # Configuração do socket
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(("", local_port))
            self.endereco_servidor = (server_host, server_port)
            self.logger.info(f"Socket configurado para {server_host}:{server_port}")
        except socket.error as e:
            self.logger.error(f"Erro ao configurar socket: {e}")
            raise

    def _send_message(self, mensagem: str) -> None:
        """
        Envia uma mensagem para o servidor.

        Args:
            mensagem (str): Mensagem a ser enviada.
        """
        try:
            self.sock.sendto(mensagem.encode(), self.endereco_servidor)
            self.logger.debug(f"Mensagem enviada: {mensagem}")
        except socket.error as e:
            self.logger.error(f"Erro ao enviar mensagem: {e}")

    def _executar_sequencia_movimentos(
        self,
        movimentos: List[str],
        intervalo: float = 0.05
    ) -> None:
        """
        Executa uma sequência de movimentos.

        Args:
            movimentos (List[str]): Lista de mensagens de movimento.
            intervalo (float): Tempo de espera entre movimentos.
        """
        for movimento in movimentos:
            self._send_message(movimento)
            time.sleep(intervalo)

    def jump(self, direcao: Optional[str] = None) -> None:
        """
        Executa um salto do robô.

        Args:
            direcao (Optional[str]): Direção opcional do salto.
        """
        # Movimentos de salto para cima
        movimentos_up = ["controle;up"] * self.altura

        # Movimentos de salto para baixo
        movimentos_down = ["controle;down"] * self.altura

        # Movimentos horizontais opcionais
        movimentos_horizontais = []
        if direcao:
            if direcao not in ["right", "left"]:
                self.logger.error("Direção de salto inválida!")
                return

            movimentos_horizontais = [f"controle;{direcao}"] * (self.distancia // 2)

        # Executa sequência de movimentos
        try:
            self._executar_sequencia_movimentos(movimentos_up)

            if movimentos_horizontais:
                self._executar_sequencia_movimentos(movimentos_horizontais)

            self._executar_sequencia_movimentos(movimentos_down)

        except Exception as e:
            self.logger.error(f"Erro durante o salto: {e}")

    def run(self, comando: str, velocidade: float) -> None:
        """
        Executa movimento contínuo em uma direção.

        Args:
            comando (str): Direção do movimento.
            velocidade (float): Velocidade do movimento.

        Raises:
            ValueError: Se velocidade for inválida.
        """
        try:
            velocidade = float(velocidade)
            if velocidade <= 0:
                raise ValueError("Velocidade deve ser maior que zero.")

            # Gera lista de mensagens de movimento
            movimentos = [f"controle;{comando}"] * self.distancia

            for movimento in movimentos:
                self._send_message(movimento)
                time.sleep(1 / velocidade)

        except ValueError as e:
            self.logger.error(f"Erro de execução: {e}")
            raise

    def dodge(self, direcao: str) -> None:
        """
        Executa uma esquiva em uma direção.

        Args:
            direcao (str): Direção da esquiva.

        Raises:
            ValueError: Se direção for inválida.
        """
        if direcao not in ["right", "left"]:
            error_msg = "Comando inválido para dodge. Use 'right' ou 'left'."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Determinar direção oposta
        direcao_oposta = "left" if direcao == "right" else "right"

        try:
            # Movimento na direção especificada
            movimentos_direcao = [f"controle;{direcao}"] * self.distancia
            self._executar_sequencia_movimentos(movimentos_direcao)

            # Movimento na direção oposta
            movimentos_oposto = [f"controle;{direcao_oposta}"] * self.distancia
            self._executar_sequencia_movimentos(movimentos_oposto)

        except Exception as e:
            self.logger.error(f"Erro durante dodge: {e}")

    def close(self) -> None:
        """
        Fecha a conexão do socket.
        """
        try:
            self.sock.close()
            self.logger.info("Socket fechado com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao fechar socket: {e}")

def main():
    """
    Função principal para execução interativa do controlador.
    """
    controller = RobotSocketController()

    try:
        while True:
            try:
                acao = input(
                    "Entre com o comando:\n"
                    "Opções:\n"
                    "- Direcionais: up, down, left, right\n"
                    "- Saltos: jump, jump,right, jump,left\n"
                    "- Esquivas: dodge,right, dodge,left\n"
                    "- Corrida: run,right,<velocidade>, run,left,<velocidade>\n"
                    "'q' para sair: "
                ).strip().lower()

                if acao == 'q':
                    break

                if acao == 'jump':
                    controller.jump()
                elif acao.startswith("dodge,"):
                    _, direcao = acao.split(",")
                    controller.dodge(direcao)
                elif acao.startswith("run,"):
                    try:
                        _, direcao, velocidade = acao.split(",")
                        controller.run(direcao, velocidade)
                    except ValueError:
                        print("Comando inválido. Use: run,<direcao>,<velocidade>")
                elif acao.startswith("jump,"):
                    try:
                        _, direcao = acao.split(",")
                        controller.jump(direcao)
                    except ValueError:
                        print("Comando inválido. Use: jump,<direcao>")
                else:
                    # Comandos simples direcionais
                    controller._send_message(f"controle;{acao}")

            except ValueError as e:
                print(f"Erro de entrada: {e}")

    except KeyboardInterrupt:
        print("\nOperação interrompida pelo usuário.")
    finally:
        controller.close()

main()
