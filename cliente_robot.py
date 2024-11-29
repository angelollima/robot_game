import socket
import time
import logging
from typing import Optional, List, Tuple

class RobotSocketController:
    """
    Controlador de robô utilizando comunicação via socket UDP.
    Gerencia movimentos e comandos de controle através de uma conexão UDP,
    garantindo que os movimentos do robô respeitem os limites da tela.
    """

    def __init__(
        self,
        server_host: str = "127.0.0.1",
        server_port: int = 2024,
        local_port: int = 2025,
        distancia: int = 10,
        altura: int = 10,
        screen_width: int = 800,
        screen_height: int = 600
    ):
        """
        Inicializa o controlador do robô com configurações personalizáveis.

        Args:
            server_host (str): Endereço IP do servidor.
            server_port (int): Porta do servidor.
            local_port (int): Porta local para bind do socket.
            distancia (int): Distância padrão de movimento.
            altura (int): Altura padrão de salto.
            screen_width (int): Largura da tela de simulação.
            screen_height (int): Altura da tela de simulação.
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

        # Limites da tela
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin_x = 25
        self.margin_y = 35

        # Configuração do socket
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(("", local_port))
            self.endereco_servidor = (server_host, server_port)
            self.logger.info(f"Socket configurado para {server_host}:{server_port}")
        except socket.error as e:
            self.logger.error(f"Erro ao configurar socket: {e}")
            raise

        # Posição inicial do robô centralizada na tela
        self.pos_x, self.pos_y = screen_width // 2, screen_height // 1.2

    def _calcular_deslocamento(self, comando: str) -> Tuple[int, int]:
        """
        Calcula o deslocamento com base no comando de movimento.

        Args:
            comando (str): Comando de movimento.

        Returns:
            Tuple[int, int]: Deslocamento nos eixos x e y.
        """
        dx, dy = 0, 0
        if comando == "up":
            dy = -self.distancia
        elif comando == "down":
            dy = self.distancia
        elif comando == "left":
            dx = -self.distancia
        elif comando == "right":
            dx = self.distancia
        return dx, dy

    def _validar_movimento(self, dx: int, dy: int) -> bool:
        """
        Verifica se o movimento é válido, considerando os limites da tela.

        Args:
            dx (int): Deslocamento no eixo X.
            dy (int): Deslocamento no eixo Y.

        Returns:
            bool: True se o movimento está dentro dos limites, False caso contrário.
        """
        novo_x = self.pos_x + dx
        novo_y = self.pos_y + dy
        if (self.margin_x <= novo_x <= (self.screen_width - self.margin_x)) and \
           (self.margin_y <= novo_y <= (self.screen_height - self.margin_y)):
            return True
        else:
            self.logger.warning(
                f"Movimento inválido: Posição calculada ({novo_x}, {novo_y}) fora dos limites."
            )
            return False

    def _send_message(self, mensagem: str) -> None:
        """
        Envia uma mensagem para o servidor, verificando os limites antes.

        Args:
            mensagem (str): Mensagem a ser enviada.
        """
        try:
            # Extrai o comando após o ponto e vírgula
            command = mensagem.split(";")[1]

            # Calcula deslocamento
            dx, dy = self._calcular_deslocamento(command)

            # Verificação de limites
            if self._validar_movimento(dx, dy):
                novo_x = self.pos_x + dx
                novo_y = self.pos_y + dy

                # Atualiza a posição
                self.pos_x, self.pos_y = novo_x, novo_y
                self.sock.sendto(mensagem.encode(), self.endereco_servidor)
                self.logger.debug(f"Mensagem enviada: {mensagem}")
            else:
                self.logger.warning(f"Movimento '{command}' bloqueado por ultrapassar os limites.")
        except (socket.error, IndexError) as e:
            self.logger.error(f"Erro ao enviar mensagem: {e}")

    def _executar_sequencia_movimentos(self, movimentos: List[str], intervalo: float = 0.05) -> None:
        """
        Executa uma sequência de movimentos, verificando os limites antes.

        Args:
            movimentos (List[str]): Lista de mensagens de movimento.
            intervalo (float): Tempo de espera entre movimentos.
        """
        for movimento in movimentos:
            try:
                command = movimento.split(";")[1]

                # Calcula deslocamento
                dx, dy = self._calcular_deslocamento(command)

                # Verificação de limites antes de cada movimento
                if self._validar_movimento(dx, dy):
                    self._send_message(movimento)
                    time.sleep(intervalo)
                else:
                    self.logger.warning(f"Movimento '{command}' bloqueado por ultrapassar os limites.")
            except Exception as e:
                self.logger.error(f"Erro durante sequência de movimentos: {e}")

    def jump(self, direcao: Optional[str] = None) -> None:
        """
        Executa um salto do robô com movimentação lateral opcional.

        Args:
            direcao (Optional[str]): Direção opcional do salto ("right" ou "left").
        """
        # Valida direção se fornecida
        if direcao and direcao not in ["right", "left"]:
            self.logger.error("Direção de salto inválida!")
            return

        # Verifica limite superior da tela
        if self.pos_y <= self.margin_y:
            self.logger.warning("O robô já está no topo da tela, não é possível pular para cima.")
            return

        try:
            # Movimento para cima
            for _ in range(self.altura):
                self._executar_sequencia_movimentos(["controle;up"])
                time.sleep(0.005)

                # Movimento lateral opcional
                if direcao:
                    self._executar_sequencia_movimentos([f"controle;{direcao}"])
                    time.sleep(0.005)

            # Movimento para baixo
            for _ in range(self.altura):
                self._executar_sequencia_movimentos(["controle;down"])
                time.sleep(0.005)

                # Movimento lateral opcional durante descida
                if direcao:
                    self._executar_sequencia_movimentos([f"controle;{direcao}"])
                    time.sleep(0.005)

        except Exception as e:
            self.logger.error(f"Erro durante o salto: {e}")

    def run(self, comando: str, velocidade: float) -> None:
        """
        Executa movimento contínuo em uma direção com velocidade configurável.

        Args:
            comando (str): Direção do movimento.
            velocidade (float): Velocidade do movimento.

        Raises:
            ValueError: Se a velocidade for inválida.
        """
        try:
            velocidade = float(velocidade)
            if velocidade <= 0:
                raise ValueError("Velocidade deve ser maior que zero.")

            movimentos = [f"controle;{comando}"] * self.distancia
            self._executar_sequencia_movimentos(movimentos, intervalo=(1 / velocidade))
        except ValueError as e:
            self.logger.error(f"Erro de execução: {e}")
            raise

    def walk(self, comando: str) -> None:
        """
        Executa movimento contínuo em uma direção em velocidade padrão.

        Args:
            comando (str): Direção do movimento.
        """
        try:
            movimentos = [f"controle;{comando}"] * self.distancia
            self._executar_sequencia_movimentos(movimentos, intervalo=(1 / 5))
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

        direcao_oposta = "left" if direcao == "right" else "right"
        try:
            movimentos_direcao = [f"controle;{direcao}"] * self.distancia
            self._executar_sequencia_movimentos(movimentos_direcao)

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
                    "\nEntre com o comando:\n"
                    "Opções:\n"
                    "- Direcionais: up, down, left, right\n"
                    "- Saltos: [jump], [jump,right], [jump,left]\n"
                    "- Esquivas: [dodge,right], [dodge,left]\n"
                    "- Andar: [walk,right], [walk,left]\n"
                    "- Corrida: [run,right,<velocidade>], [run,left,<velocidade>]\n"
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
                elif acao.startswith("walk,"):
                    try:
                        _, direcao = acao.split(",")
                        controller.walk(direcao)
                    except ValueError:
                        print("Comando inválido. Use: walk,<direcao>")
                elif acao.startswith("jump,"):
                    try:
                        _, direcao = acao.split(",")
                        controller.jump(direcao)
                    except ValueError:
                        print("Comando inválido. Use: jump,<direcao>")
                else:
                    # Comandos simples direcionais
                    controller._send_message(f"controle;{acao}")
            except Exception as e:
                print(f"Erro no comando: {e}")
    finally:
        controller.close()

if __name__ == "__main__":
    main()
