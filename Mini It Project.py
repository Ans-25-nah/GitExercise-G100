# ============================================
# Mini IT Project
# Player Movement + Shooting (Partial)
# ============================================

import pygame
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Player Movement + Shooting")

clock = pygame.time.Clock()

# Player settings
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 5

# Bullet settings (from your shooting code)
bullet_speed = 7
bullets = []

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# --- SHOOTING FUNCTION (same logic) ---
def shoot(player_x, player_y, player_size):
    bullet_x = player_x + player_size // 2
    bullet_y = player_y
    bullets.append([bullet_x, bullet_y])

# --- UPDATE BULLETS (same logic) ---
def update_bullets():
    for bullet in bullets:
        bullet[1] -= bullet_speed

# --- DRAW BULLETS (same logic) ---
def draw_bullets(surface):
    for bullet in bullets:
        pygame.draw.circle(surface, BLACK, (bullet[0], bullet[1]), 5)

# Game loop
running = True
while running:
    clock.tick(60)
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Shooting (SPACE)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shoot(player_x, player_y, player_size)

    # Movement (WASD)
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_s]:
        player_y += player_speed
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed

    # Boundary check
    if player_x < 0:
        player_x = 0
    if player_x > WIDTH - player_size:
        player_x = WIDTH - player_size
    if player_y < 0:
        player_y = 0
    if player_y > HEIGHT - player_size:
        player_y = HEIGHT - player_size

    # Update bullets
    update_bullets()

    # Draw player
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))

    # Draw bullets
    draw_bullets(screen)

    pygame.display.flip()

# Quit game cleanly
pygame.quit()
sys.exit()

   

