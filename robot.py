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
        self.base_speed = 10
        self.run_speed = 20

    def update(self, actions):
        speed = self.base_speed
        if "run" in actions:
            speed = self.run_speed
            actions.remove("run")  # Remove 'run' para evitar conflito com direções

        for action in actions:
            if action == "up" and self.rect.top > 0:
                self.rect.y -= speed
            elif action == "down" and self.rect.bottom < screen_height:
                self.rect.y += speed
            elif action == "left" and self.rect.left > 0:
                self.rect.x -= speed
            elif action == "right" and self.rect.right < screen_width:
                self.rect.x += speed

    def dodge(self, direction):
        if direction == "left" and self.rect.left > 50:
            self.rect.x -= 50
        elif direction == "right" and self.rect.right < screen_width - 50:
            self.rect.x += 50


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
                command_parts = data.decode("utf-8").strip().lower().split(";")
                if len(command_parts) == 3 and command_parts[1] == "controle":
                    current_command = command_parts[2].split(",")
                else:
                    current_command = []
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
        current_command = []  # Reset command after using

    # Clear the screen with black
    screen.blit(background_image, (0, 0))
    # Update and draw all sprites
    if command_to_use:
        if "dodge" in command_to_use:
            direction = "left" if "left" in command_to_use else "right"
            robot.dodge(direction)
        else:
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
