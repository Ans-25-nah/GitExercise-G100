import pygame
import sys

pygame.init()

# -------------------------
# SCREEN
# -------------------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2 Player Shooter")

clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# -------------------------
# PLAYER CLASS
# -------------------------
class Soldier:
    def __init__(self, x, y, color, controls):
        self.image = pygame.Surface((50, 50))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.grenades = 100
        self.controls = controls

    def move(self, keys):
        if keys[self.controls["up"]]:
            self.rect.y -= self.speed
        if keys[self.controls["down"]]:
            self.rect.y += self.speed
        if keys[self.controls["left"]]:
            self.rect.x -= self.speed
        if keys[self.controls["right"]]:
            self.rect.x += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)


# -------------------------
# BULLET
# -------------------------
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 7

    def move(self):
        self.y -= self.speed

    def draw(self):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 5)


# -------------------------
# GRENADE
# -------------------------
class Grenade:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_y = -6
        self.gravity = 0.5

    def move(self):
        self.vel_y += self.gravity
        self.y += self.vel_y

    def draw(self):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 8)


# -------------------------
# ENEMY
# -------------------------
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)


# -------------------------
# PLAYERS
# -------------------------
player1 = Soldier(200, 500, (0, 0, 255), {
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d
})

player2 = Soldier(600, 500, (0, 255, 0), {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT
})

bullets = []
grenades = []
enemies = [Enemy(300, 100), Enemy(500, 150), Enemy(400, 200)]

# -------------------------
# FUNCTIONS
# -------------------------
def shoot(player):
    bullets.append(Bullet(player.rect.centerx, player.rect.top))


def throw_grenade(player):
    if player.grenades > 0:
        grenades.append(Grenade(player.rect.centerx, player.rect.top))
        player.grenades -= 1


# -------------------------
# GAME LOOP
# -------------------------
running = True
while running:
    clock.tick(60)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Player 1 shoot / grenade
            if event.key == pygame.K_SPACE:
                shoot(player1)
            if event.key == pygame.K_q:
                throw_grenade(player1)

            # Player 2 shoot / grenade
            if event.key == pygame.K_RETURN:
                shoot(player2)
            if event.key == pygame.K_RSHIFT:
                throw_grenade(player2)

    keys = pygame.key.get_pressed()
    player1.move(keys)
    player2.move(keys)

    # Update bullets
    for bullet in bullets[:]:
        bullet.move()
        if bullet.y < 0:
            bullets.remove(bullet)

    # Update grenades
    for grenade in grenades[:]:
        grenade.move()
        if grenade.y > HEIGHT:
            grenades.remove(grenade)

    # Collision (bullets)
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if enemy.rect.collidepoint(bullet.x, bullet.y):
                bullets.remove(bullet)
                enemies.remove(enemy)
                break

    # Collision (grenades)
    for grenade in grenades[:]:
        for enemy in enemies[:]:
            if enemy.rect.collidepoint(grenade.x, grenade.y):
                grenades.remove(grenade)
                enemies.remove(enemy)
                break

    # Draw everything
    player1.draw()
    player2.draw()

    for bullet in bullets:
        bullet.draw()

    for grenade in grenades:
        grenade.draw()

    for enemy in enemies:
        enemy.draw()

    pygame.display.update()

pygame.quit()
sys.exit()