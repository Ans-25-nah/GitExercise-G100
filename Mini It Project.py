import pygame
import sys
import random

pygame.init()

# =========================
# SCREEN
# =========================
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2 Player Shooter")

clock = pygame.time.Clock()

# =========================
# LOAD IMAGES
# =========================
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

player1_img = pygame.image.load("player1.png").convert_alpha()
player1_img = pygame.transform.scale(player1_img, (50, 50))

player2_img = pygame.image.load("player2.png").convert_alpha()
player2_img = pygame.transform.scale(player2_img, (50, 50))

enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (50, 50))

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

font = pygame.font.Font(None, 36)

GROUND_Y = 500

# =========================
# PLAYER CLASS
# =========================
class Soldier:
    def __init__(self, x, y, image, controls):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 5

        self.vel_y = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False

        self.health = 3
        self.grenades = 5

        self.controls = controls

    def move(self, keys):

        # ✅ STOP EVERYTHING IF DEAD
        if self.health <= 0:
            return

        if keys[self.controls["left"]]:
            self.rect.x -= self.speed

        if keys[self.controls["right"]]:
            self.rect.x += self.speed

        if keys[self.controls["jump"]] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def draw(self):
        # ✅ PLAYER DISAPPEARS WHEN DEAD
        if self.health > 0:
            screen.blit(self.image, self.rect)


# =========================
# BULLET
# =========================
class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 10, 5)
        self.speed = 10
        self.direction = direction

    def move(self):
        self.rect.x += self.speed * self.direction

    def draw(self):
        pygame.draw.rect(screen, BLACK, self.rect)


# =========================
# GRENADE
# =========================
class Grenade:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 15, 15)
        self.speed_x = 7 * direction
        self.speed_y = -10
        self.gravity = 0.5

    def move(self):
        self.rect.x += self.speed_x
        self.speed_y += self.gravity
        self.rect.y += self.speed_y

    def draw(self):
        pygame.draw.circle(screen, RED, self.rect.center, 8)


# =========================
# ENEMY
# =========================
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.speed = 2

    def move(self):
        self.rect.x -= self.speed

    def draw(self):
        screen.blit(enemy_img, self.rect)


# =========================
# PLAYERS
# =========================
player1 = Soldier(80, 450, player1_img, {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "jump": pygame.K_SPACE
})

player2 = Soldier(180, 450, player2_img, {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "jump": pygame.K_UP
})

bullets = []
grenades = []
enemies = []

level = 1

def spawn_enemies():
    enemies.clear()
    for i in range(level + 2):
        enemies.append(Enemy(random.randint(700, 950), 450))

spawn_enemies()

# =========================
# ACTIONS
# =========================
def shoot(player):
    bullets.append(Bullet(player.rect.centerx, player.rect.centery, 1))

def throw_grenade(player):
    if player.grenades > 0:
        grenades.append(Grenade(player.rect.centerx, player.rect.centery, 1))
        player.grenades -= 1


# =========================
# GAME LOOP
# =========================
running = True
while running:
    clock.tick(60)

    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                shoot(player1)
            if event.key == pygame.K_q:
                throw_grenade(player1)

            if event.key == pygame.K_RCTRL:
                shoot(player2)
            if event.key == pygame.K_RSHIFT:
                throw_grenade(player2)

    keys = pygame.key.get_pressed()
    player1.move(keys)
    player2.move(keys)

    for enemy in enemies:
        enemy.move()

    # BULLETS
    for bullet in bullets[:]:
        bullet.move()
        if bullet.rect.x > WIDTH:
            bullets.remove(bullet)

        for enemy in enemies[:]:
            if bullet.rect.colliderect(enemy.rect):
                bullets.remove(bullet)
                enemies.remove(enemy)
                break

    # GRENADES
    for grenade in grenades[:]:
        grenade.move()
        if grenade.rect.y > HEIGHT:
            grenades.remove(grenade)

        for enemy in enemies[:]:
            if grenade.rect.colliderect(enemy.rect):
                grenades.remove(grenade)
                enemies.remove(enemy)
                break

    # ENEMY DAMAGE
    for enemy in enemies[:]:
        if enemy.rect.colliderect(player1.rect):
            if player1.health > 0:
                player1.health -= 1
            enemies.remove(enemy)
            continue

        if enemy.rect.colliderect(player2.rect):
            if player2.health > 0:
                player2.health -= 1
            enemies.remove(enemy)

    # NEXT LEVEL
    if len(enemies) == 0:
        level += 1
        spawn_enemies()

    # DRAW
    pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

    player1.draw()
    player2.draw()

    for enemy in enemies:
        enemy.draw()

    for bullet in bullets:
        bullet.draw()

    for grenade in grenades:
        grenade.draw()

    # UI
    screen.blit(font.render(f"Level: {level}", True, WHITE), (20, 20))
    screen.blit(font.render(f"P1 Hearts: {player1.health}", True, WHITE), (20, 60))
    screen.blit(font.render(f"P2 Hearts: {player2.health}", True, WHITE), (20, 100))
    screen.blit(font.render(f"P1 Grenades: {player1.grenades}", True, WHITE), (20, 140))
    screen.blit(font.render(f"P2 Grenades: {player2.grenades}", True, WHITE), (20, 180))

    # GAME OVER
    if player1.health <= 0 and player2.health <= 0:
        game_over = font.render("GAME OVER", True, RED)
        rect = game_over.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(game_over, rect)
        pygame.display.update()
        pygame.time.delay(3000)
        running = False

    pygame.display.update()

pygame.quit()
sys.exit()