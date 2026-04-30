import pygame
import sys
import math

pygame.init()

# =========================
# SCREEN SETUP
# =========================
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Superhot Concept Game")

clock = pygame.time.Clock()

# =========================
# COLORS
# =========================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# =========================
# FONT
# =========================
font = pygame.font.Font(None, 48)

# =========================
# GAME STATE SYSTEM
# =========================
game_state = "START"
score = 0

# =========================
# PLAYER
# =========================
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 5

# =========================
# ENEMY
# =========================
enemy_size = 50
enemy_x = 100
enemy_y = 100
enemy_speed = 2

# =========================
# BULLETS (NEW - YOU NEED THIS FOR SHOOTING)
# =========================
bullets = []
bullet_speed = 6
shoot_timer = 0
shoot_delay = 60   # every 1 second (60 FPS)

# =========================
# RESET FUNCTION
# =========================
def reset_game():
    global player_x, player_y, enemy_x, enemy_y, score, bullets, shoot_timer

    player_x = WIDTH // 2
    player_y = HEIGHT // 2

    enemy_x = 100
    enemy_y = 100

    score = 0
    bullets = []
    shoot_timer = 0

# =========================
# MAIN LOOP
# =========================
while True:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if game_state == "START":
                if event.key == pygame.K_SPACE:
                    game_state = "PLAYING"

            elif game_state == "GAME_OVER":
                if event.key == pygame.K_r:
                    reset_game()
                    game_state = "START"

    # =========================
    # START SCREEN
    # =========================
    if game_state == "START":
        text = font.render("Press SPACE to Start", True, WHITE)
        screen.blit(text, (200, 250))

    # =========================
    # PLAYING STATE
    # =========================
    elif game_state == "PLAYING":

        keys = pygame.key.get_pressed()

        # time system
        if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
            time_scale = 1.0
        else:
            time_scale = 0.0

        # =========================
        # PLAYER MOVEMENT
        # =========================
        if keys[pygame.K_w]:
            player_y -= player_speed
        if keys[pygame.K_s]:
            player_y += player_speed
        if keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_d]:
            player_x += player_speed

        player_x = max(0, min(WIDTH - player_size, player_x))
        player_y = max(0, min(HEIGHT - player_size, player_y))

        # =========================
        # ENEMY AI MOVEMENT
        # =========================
        dx = player_x - enemy_x
        dy = player_y - enemy_y
        distance = math.sqrt(dx*dx + dy*dy)

        if distance > 0:
            enemy_x += (dx / distance) * enemy_speed * time_scale
            enemy_y += (dy / distance) * enemy_speed * time_scale

        # =========================
        # ENEMY SHOOTING (NEW PART - SIMPLE VERSION)
        # =========================
        shoot_timer += 1 * time_scale

        if shoot_timer >= shoot_delay:
            shoot_timer = 0

            dx = player_x - enemy_x
            dy = player_y - enemy_y
            distance = math.sqrt(dx*dx + dy*dy)

            if distance > 0:
                bullets.append([
                    enemy_x + enemy_size // 2,
                    enemy_y + enemy_size // 2,
                    dx / distance * bullet_speed,
                    dy / distance * bullet_speed
                ])

        # =========================
        # BULLET UPDATE
        # =========================
        for bullet in bullets:
            bullet[0] += bullet[2] * time_scale
            bullet[1] += bullet[3] * time_scale

        # remove bullets out of screen
        bullets = [b for b in bullets if 0 < b[0] < WIDTH and 0 < b[1] < HEIGHT]

        # =========================
        # COLLISION (PLAYER vs ENEMY)
        # =========================
        if abs(player_x - enemy_x) < 50 and abs(player_y - enemy_y) < 50:
            game_state = "GAME_OVER"

        # =========================
        # COLLISION (PLAYER vs BULLET)
        # =========================
        for bullet in bullets:
            if abs(player_x - bullet[0]) < 10 and abs(player_y - bullet[1]) < 10:
                game_state = "GAME_OVER"

        # =========================
        # SCORE
        # =========================
        score += 1 * time_scale

        # =========================
        # DRAW
        # =========================
        pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))
        pygame.draw.rect(screen, RED, (enemy_x, enemy_y, enemy_size, enemy_size))

        # draw bullets
        for bullet in bullets:
            pygame.draw.rect(screen, YELLOW, (bullet[0], bullet[1], 8, 8))

        # UI
        text = font.render(f"Score: {int(score)}", True, WHITE)
        screen.blit(text, (10, 10))

    # =========================
    # GAME OVER
    # =========================
    elif game_state == "GAME_OVER":
        text1 = font.render("GAME OVER", True, RED)
        text2 = font.render("Press R to Restart", True, WHITE)

        screen.blit(text1, (250, 200))
        screen.blit(text2, (200, 300))

    pygame.display.flip()