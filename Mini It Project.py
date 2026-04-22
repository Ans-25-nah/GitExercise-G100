# ============================================
# Mini IT Project
# [Player-Movement] Implement Player Movement System
# ============================================

import pygame
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Player Movement System")

clock = pygame.time.Clock()

# Player settings
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 5

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Game loop
running = True
while running:
    clock.tick(60)
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key input (WASD movement)
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_s]:
        player_y += player_speed
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed

    # Boundary check (keep player inside screen)
    if player_x < 0:
        player_x = 0
    if player_x > WIDTH - player_size:
        player_x = WIDTH - player_size
    if player_y < 0:
        player_y = 0
    if player_y > HEIGHT - player_size:
        player_y = HEIGHT - player_size

    # Draw player
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))

    # Update display
    pygame.display.flip()

# Quit game cleanly
pygame.quit()
sys.exit()


   

