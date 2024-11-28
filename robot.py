import pygame
import socket
import sys
import threading

PORT = 2024

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
black = (0, 0, 0)

# Frame rate
clock = pygame.time.Clock()
fps = 60

background_image = pygame.image.load("background.jpg")
background_image = pygame.transform.scale(
    background_image, (screen_width, screen_height)
)


# Robot class
class Robot(pygame.sprite.Sprite):
    def __init__(self):
        super(Robot, self).__init__()
        original_image = pygame.image.load("robot.png")
        self.image = pygame.transform.scale(original_image, (800, 600))
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height // 1.2)
        self.direction = "UP"

    def get_screen_dimensions(self):
        return screen_width, screen_height

    def get_robot_position(self):
        return self.rect.x, self.rect.y

    def update(self, command):
        if command:
            if command == "up":
                self.rect.y -= 10
                self.direction = "up"
            elif command == "down":
                self.rect.y += 10
                self.direction = "down"
            elif command == "left":
                self.rect.x -= 10
                self.direction = "left"
            elif command == "right":
                self.rect.x += 10
                self.direction = "right"


# Initialize robot
robot = Robot()
all_sprites = pygame.sprite.Group()
all_sprites.add(robot)

# UDP Socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))
sock.setblocking(0)  # Set socket to non-blocking mode

# Thread for handling UDP communication
command_lock = threading.Lock()
current_command = None
running = True


def receive_commands():
    global current_command
    while running:
        try:
            data, _ = sock.recvfrom(4096)
            with command_lock:
                print(f"Comando recebido: {data.decode('utf-8')}")
                res = data.decode("utf-8").strip().lower().split(";")
                if res[0] == "controle":
                    current_command = res[1]
                else:
                    current_command = None
        except BlockingIOError:
            continue


# Start the thread
thread = threading.Thread(target=receive_commands)
thread.start()

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the latest command
    with command_lock:
        command_to_use = current_command
        current_command = None  # Reset command after using

    # Clear the screen with black
    screen.blit(background_image, (0, 0))
    # Update and draw all sprites
    if command_to_use:
        robot.update(command_to_use)
    all_sprites.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(fps)

# Wait for the thread to finish
thread.join()

# Clean up
pygame.quit()
sys.exit()
