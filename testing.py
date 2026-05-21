import pygame
import sys
import math
import random

pygame.init()

# =========================
# SCREEN SETUP
# =========================
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SUPERHOT Prototype")

clock = pygame.time.Clock()

# =========================
# COLORS
# =========================
WHITE = (255, 255, 255)
BLACK = (15, 15, 15)
BLUE = (50, 150, 255)
RED = (255, 60, 60)
YELLOW = (255, 220, 50)
GREEN = (50, 255, 120)
GRAY = (100, 100, 100) # button

# =========================
# FONT
# =========================
font = pygame.font.Font(None, 42)
small_font = pygame.font.Font(None, 28)

# =========================
# GAME STATE
# =========================
game_state = "START"

# =========================
# PLAYER
# =========================
player_size = 40
player_speed = 5

# =========================
# ENEMY
# =========================
enemy_size = 40

# =========================
# BULLETS
# =========================
bullets = []
bullet_speed = 7

# =========================
# LEVEL SYSTEM VARIABLES
# =========================
level = 1
score = 0
score_multiplier = 1

enemy_speed = 2
shoot_delay = 90

# enemy list
enemies = []


# button
# (X坐标, Y坐标, 宽度, 高度)
start_btn_rect = pygame.Rect(300, 320, 200, 50)

# =========================
# FUNCTIONS
# =========================

def create_enemy():
    side = random.choice(["top", "bottom", "left", "right"])

    if side == "top":
        x = random.randint(0, WIDTH)
        y = -50

    elif side == "bottom":
        x = random.randint(0, WIDTH)
        y = HEIGHT + 50

    elif side == "left":
        x = -50
        y = random.randint(0, HEIGHT)

    else:
        x = WIDTH + 50
        y = random.randint(0, HEIGHT)

    return {
        "x": x,
        "y": y,
        "shoot_timer": random.randint(0, shoot_delay)
    }


def start_level(current_level):
    global enemies

    enemies = []

    # number of enemies increases every level
    enemy_count = current_level + 1

    for _ in range(enemy_count):
        enemies.append(create_enemy())


def reset_game():
    global player_x
    global player_y
    global bullets
    global level
    global score
    global enemy_speed
    global shoot_delay
    global score_multiplier

    player_x = WIDTH // 2
    player_y = HEIGHT // 2

    bullets = []

    level = 1
    score = 0

    enemy_speed = 2
    shoot_delay = 90
    score_multiplier = 1

    start_level(level)


# =========================
# INITIALIZE GAME
# =========================
reset_game()

# =========================
# MAIN LOOP
# =========================
while True:

    clock.tick(60)
    screen.fill(BLACK)

    # =========================
    # EVENTS
    # =========================
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # 1 left click
                
                
                mouse_pos = pygame.mouse.get_pos()
                
                # START menu，mouse click start
                if game_state == "START":
                    if start_btn_rect.collidepoint(mouse_pos):
                        reset_game()
                        game_state = "PLAYING"

        if event.type == pygame.KEYDOWN:
            # RESTART
            if game_state == "GAME_OVER":
                if event.key == pygame.K_r:
                    reset_game()
                    game_state = "PLAYING"

    # =========================
    # START SCREEN
    # =========================
    if game_state == "START":

        title = font.render("TESTING", True, WHITE)
        screen.blit(title, (220, 220))

        # draw button
        pygame.draw.rect(screen, GRAY, start_btn_rect)

        #button text
        btn_text = small_font.render("Start Game", True, WHITE)
        # text at mid
        screen.blit(btn_text, (start_btn_rect.x + 50, start_btn_rect.y + 15))

    # =========================
    # PLAYING
    # =========================
    elif game_state == "PLAYING":

        keys = pygame.key.get_pressed()

        # =========================
        # TIME SYSTEM
        # =========================
        if (
            keys[pygame.K_w]
            or keys[pygame.K_s]
            or keys[pygame.K_a]
            or keys[pygame.K_d]
        ):
            time_scale = 1.0
        else:
            time_scale = 0.08

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

        # keep inside screen
        player_x = max(0, min(WIDTH - player_size, player_x))
        player_y = max(0, min(HEIGHT - player_size, player_y))

        # =========================
        # ENEMY UPDATE
        # =========================
        for enemy in enemies:

            dx = player_x - enemy["x"]
            dy = player_y - enemy["y"]

            distance = math.sqrt(dx * dx + dy * dy)

            # movement
            if distance > 0:
                enemy["x"] += (
                    dx / distance
                ) * enemy_speed * time_scale

                enemy["y"] += (
                    dy / distance
                ) * enemy_speed * time_scale

            # =========================
            # ENEMY SHOOTING
            # =========================
            enemy["shoot_timer"] += 1 * time_scale

            if enemy["shoot_timer"] >= shoot_delay:

                enemy["shoot_timer"] = 0

                dx = player_x - enemy["x"]
                dy = player_y - enemy["y"]

                distance = math.sqrt(dx * dx + dy * dy)

                if distance > 0:

                    bullets.append([
                        enemy["x"] + enemy_size // 2,
                        enemy["y"] + enemy_size // 2,
                        dx / distance * bullet_speed,
                        dy / distance * bullet_speed
                    ])

        # =========================
        # BULLET UPDATE
        # =========================
        for bullet in bullets:
            bullet[0] += bullet[2] * time_scale
            bullet[1] += bullet[3] * time_scale

        # remove bullets outside screen
        bullets = [
            b for b in bullets
            if 0 < b[0] < WIDTH and 0 < b[1] < HEIGHT
        ]

        # =========================
        # COLLISION
        # =========================

        # player vs enemy
        for enemy in enemies:

            if (
                abs(player_x - enemy["x"]) < 35
                and abs(player_y - enemy["y"]) < 35
            ):
                game_state = "GAME_OVER"

        # player vs bullet
        for bullet in bullets:

            if (
                abs(player_x - bullet[0]) < 20
                and abs(player_y - bullet[1]) < 20
            ):
                game_state = "GAME_OVER"

        # =========================
        # SCORE SYSTEM
        # =========================

        # score only increases while moving
        score += 0.1 * time_scale * score_multiplier

        # =========================
        # LEVEL SYSTEM
        # =========================

        # every 100 score -> next level
        if score >= level * 100:

            level += 1

            # increase difficulty
            enemy_speed += 0.4

            # faster shooting
            if shoot_delay > 25:
                shoot_delay -= 8

            # bonus multiplier
            score_multiplier += 0.2

            # clear bullets
            bullets.clear()

            # start new level
            start_level(level)

        # =========================
        # DRAW PLAYER
        # =========================
        pygame.draw.rect(
            screen,
            BLUE,
            (player_x, player_y, player_size, player_size)
        )

        # =========================
        # DRAW ENEMIES
        # =========================
        for enemy in enemies:

            pygame.draw.rect(
                screen,
                RED,
                (
                    enemy["x"],
                    enemy["y"],
                    enemy_size,
                    enemy_size
                )
            )

        # =========================
        # DRAW BULLETS
        # =========================
        for bullet in bullets:

            pygame.draw.rect(
                screen,
                YELLOW,
                (bullet[0], bullet[1], 10, 10)
            )

        # =========================
        # UI
        # =========================
        score_text = small_font.render(
            f"Score: {int(score)}",
            True,
            WHITE
        )

        level_text = small_font.render(
            f"Level: {level}",
            True,
            GREEN
        )

        enemy_text = small_font.render(
            f"Enemies: {len(enemies)}",
            True,
            WHITE
        )

        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 40))
        screen.blit(enemy_text, (10, 70))

    # =========================
    # GAME OVER
    # =========================
    elif game_state == "GAME_OVER":

        over_text = font.render("GAME OVER", True, RED)

        score_text = small_font.render(
            f"Final Score: {int(score)}",
            True,
            WHITE
        )

        level_text = small_font.render(
            f"Reached Level: {level}",
            True,
            WHITE
        )

        restart_text = small_font.render(
            "Press R to Restart",
            True,
            WHITE
        )

        screen.blit(over_text, (280, 180))
        screen.blit(score_text, (290, 260))
        screen.blit(level_text, (285, 300))
        screen.blit(restart_text, (260, 380))

    pygame.display.flip()