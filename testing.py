import pygame
import sys
import math
import random
import os

pygame.init()

# ============================================
# SCREEN SETUP
# ============================================

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SUPERHOT Prototype")

clock = pygame.time.Clock()
FPS = 60

# ============================================
# COLORS
# ============================================

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (255, 60, 60)
GREEN = (50, 255, 120)
GRAY = (120, 120, 120)

# ============================================
# GAME VARIABLES
# ============================================

game_state = "START"

level = 1
score = 0
score_multiplier = 1

enemy_speed = 1
shoot_delay = 90

# ============================================
# FONT
# ============================================

font = pygame.font.Font(None, 42)
small_font = pygame.font.Font(None, 28)

# ============================================
# LOAD IMAGES
# ============================================

bg_img = pygame.image.load(
    'img/background1/background.png'
).convert()

bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

bullet_img = pygame.image.load(
    'img/icons/bullet.png'
).convert_alpha()

bullet_img = pygame.transform.scale(
    bullet_img,
    (20, 20)
)

enemy_bullet_img = pygame.image.load(
    'img/icons/enemy_bullet.png'
).convert_alpha()

enemy_bullet_img = pygame.transform.scale(
    enemy_bullet_img,
    (20, 20)
)

health_box_img = pygame.image.load(
    'img/icons/health_box.png'
).convert_alpha()

health_box_img = pygame.transform.scale(
    health_box_img,
    (35, 35)
)

item_boxes = {
    'Health': health_box_img
}

# ============================================
# BUTTON
# ============================================

start_btn_rect = pygame.Rect(300, 320, 200, 50)

# ============================================
# DRAW TEXT
# ============================================

def draw_text(text, font, text_col, x, y):

    img = font.render(text, True, text_col)

    screen.blit(img, (x, y))

# ============================================
# PLAYER CLASS
# ============================================

class Player(pygame.sprite.Sprite):

    def __init__(self, x, y, speed, health):

        pygame.sprite.Sprite.__init__(self)

        self.alive = True

        self.speed = speed

        self.health = health
        self.max_health = health

        self.direction = 1
        self.flip = False

        self.animation_list = []

        self.frame_index = 0

        # 0 idle
        # 1 run
        # 2 death
        self.action = 0

        self.update_time = pygame.time.get_ticks()

        animation_types = ['Idle', 'Run', 'Death']

        for animation in animation_types:

            temp_list = []

            num_of_frames = len(
                os.listdir(f'img/player1/{animation}')
            )

            for i in range(num_of_frames):

                img = pygame.image.load(
                    f'img/player1/{animation}/{i}.png'
                ).convert_alpha()

                img = pygame.transform.scale(
                    img,
                    (80, 80)
                )

                temp_list.append(img)

            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]

        self.rect = self.image.get_rect()

        self.rect.center = (x, y)

    def update(self):

        self.update_animation()

        self.check_alive()

    def move(self, keys):

        moving = False

        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            moving = True

        if keys[pygame.K_s]:
            self.rect.y += self.speed
            moving = True

        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.flip = True
            self.direction = -1
            moving = True

        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.flip = False
            self.direction = 1
            moving = True

        self.rect.x = max(
            0,
            min(WIDTH - self.rect.width, self.rect.x)
        )

        self.rect.y = max(
            0,
            min(HEIGHT - self.rect.height, self.rect.y)
        )

        if moving:
            self.update_action(1)
        else:
            self.update_action(0)

    def shoot(self):

        bullet = Bullet(
            self.rect.centerx,
            self.rect.centery,
            self.direction
        )

        bullet_group.add(bullet)

    def update_animation(self):

        ANIMATION_COOLDOWN = 100

        self.image = self.animation_list[
            self.action
        ][
            self.frame_index
        ]

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:

            self.update_time = pygame.time.get_ticks()

            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):

            if self.action == 2:
                self.frame_index = len(
                    self.animation_list[self.action]
                ) - 1

            else:
                self.frame_index = 0

    def update_action(self, new_action):

        if new_action != self.action:

            self.action = new_action

            self.frame_index = 0

            self.update_time = pygame.time.get_ticks()

    def check_alive(self):

        if self.health <= 0:

            self.health = 0

            self.alive = False

            self.update_action(2)

    def draw(self):

        screen.blit(
            pygame.transform.flip(
                self.image,
                self.flip,
                False
            ),
            self.rect
        )

# ============================================
# ENEMY CLASS
# ============================================

class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y):

        pygame.sprite.Sprite.__init__(self)

        self.alive = True

        self.health = 100

        self.direction = 1
        self.flip = False

        self.animation_list = []

        self.frame_index = 0

        self.action = 0

        self.update_time = pygame.time.get_ticks()

        self.shoot_timer = random.randint(0, shoot_delay)

        animation_types = ['Idle', 'Run', 'Death']

        for animation in animation_types:

            temp_list = []

            num_of_frames = len(
                os.listdir(f'img/enemy1/{animation}')
            )

            for i in range(num_of_frames):

                img = pygame.image.load(
                    f'img/enemy1/{animation}/{i}.png'
                ).convert_alpha()

                img = pygame.transform.scale(
                    img,
                    (80, 80)
                )

                temp_list.append(img)

            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]

        self.rect = self.image.get_rect()

        self.rect.center = (x, y)

    def update(self, time_scale):

        self.update_animation()

        self.check_alive()

        if not self.alive:
            return

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:

            self.rect.x += (
                dx / distance
            ) * enemy_speed * time_scale

            self.rect.y += (
                dy / distance
            ) * enemy_speed * time_scale

        if dx < 0:
            self.flip = True
        else:
            self.flip = False

        self.update_action(1)

        self.shoot_timer += 1 * time_scale

        if self.shoot_timer >= shoot_delay:

            self.shoot_timer = 0

            if distance > 0:

                bullet = EnemyBullet(
                    self.rect.centerx,
                    self.rect.centery,
                    dx / distance,
                    dy / distance
                )

                enemy_bullet_group.add(bullet)

    def update_animation(self):

        ANIMATION_COOLDOWN = 100

        self.image = self.animation_list[
            self.action
        ][
            self.frame_index
        ]

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:

            self.update_time = pygame.time.get_ticks()

            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):

            if self.action == 2:
                self.frame_index = len(
                    self.animation_list[self.action]
                ) - 1

            else:
                self.frame_index = 0

    def update_action(self, new_action):

        if new_action != self.action:

            self.action = new_action

            self.frame_index = 0

            self.update_time = pygame.time.get_ticks()

    def check_alive(self):

        if self.health <= 0:

            self.health = 0

            self.alive = False

            self.update_action(2)

            global score

            score += 25

            if random.randint(1, 3) == 1:

                item_box = ItemBox(
                    'Health',
                    self.rect.centerx,
                    self.rect.centery
                )

                item_box_group.add(item_box)

    def draw(self):

        screen.blit(
            pygame.transform.flip(
                self.image,
                self.flip,
                False
            ),
            self.rect
        )

# ============================================
# PLAYER BULLET
# ============================================

class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction):

        pygame.sprite.Sprite.__init__(self)

        self.speed = 10

        self.image = bullet_img

        self.rect = self.image.get_rect()

        self.rect.center = (x, y)

        self.direction = direction

    def update(self):

        self.rect.x += self.direction * self.speed

        if (
            self.rect.right < 0
            or self.rect.left > WIDTH
        ):
            self.kill()

        for enemy in enemy_group:

            if pygame.sprite.collide_rect(self, enemy):

                if enemy.alive:

                    enemy.health -= 50

                    self.kill()

# ============================================
# ENEMY BULLET
# ============================================

class EnemyBullet(pygame.sprite.Sprite):

    def __init__(self, x, y, dx, dy):

        pygame.sprite.Sprite.__init__(self)

        self.speed = 7

        self.dx = dx
        self.dy = dy

        self.image = enemy_bullet_img

        self.rect = self.image.get_rect()

        self.rect.center = (x, y)

    def update(self, time_scale):

        self.rect.x += self.dx * self.speed * time_scale

        self.rect.y += self.dy * self.speed * time_scale

        if (
            self.rect.right < 0
            or self.rect.left > WIDTH
            or self.rect.bottom < 0
            or self.rect.top > HEIGHT
        ):
            self.kill()

        if pygame.sprite.collide_rect(self, player):

            player.health -= 25

            self.kill()

# ============================================
# ITEM BOX
# ============================================

class ItemBox(pygame.sprite.Sprite):

    def __init__(self, item_type, x, y):

        pygame.sprite.Sprite.__init__(self)

        self.item_type = item_type

        self.image = item_boxes[self.item_type]

        self.rect = self.image.get_rect()

        self.rect.center = (x, y)

    def update(self):

        if pygame.sprite.collide_rect(self, player):

            if self.item_type == 'Health':

                player.health += 25

                if player.health > player.max_health:

                    player.health = player.max_health

            self.kill()

# ============================================
# HEALTH BAR
# ============================================

class HealthBar():

    def __init__(self, x, y, health, max_health):

        self.x = x
        self.y = y

        self.health = health
        self.max_health = max_health

    def draw(self, health):

        self.health = health

        ratio = self.health / self.max_health

        pygame.draw.rect(
            screen,
            RED,
            (self.x, self.y, 150, 20)
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (self.x, self.y, 150 * ratio, 20)
        )

# ============================================
# CREATE GROUPS
# ============================================

bullet_group = pygame.sprite.Group()

enemy_bullet_group = pygame.sprite.Group()

enemy_group = pygame.sprite.Group()

item_box_group = pygame.sprite.Group()

# ============================================
# CREATE ENEMY
# ============================================

def create_enemy():

    side = random.choice(
        ["top", "bottom", "left", "right"]
    )

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

    enemy = Enemy(x, y)

    enemy_group.add(enemy)

# ============================================
# START LEVEL
# ============================================

def start_level(current_level):

    enemy_group.empty()

    enemy_count = current_level + 1

    for _ in range(enemy_count):

        create_enemy()

# ============================================
# RESET GAME
# ============================================

def reset_game():

    global player
    global health_bar
    global level
    global score
    global enemy_speed
    global shoot_delay
    global score_multiplier

    bullet_group.empty()
    enemy_bullet_group.empty()
    item_box_group.empty()

    player = Player(
        WIDTH // 2,
        HEIGHT // 2,
        5,
        100
    )

    health_bar = HealthBar(
        10,
        10,
        player.health,
        player.health
    )

    level = 1
    score = 0

    enemy_speed = 2

    shoot_delay = 90

    score_multiplier = 1

    start_level(level)

# ============================================
# START GAME
# ============================================

reset_game()

# ============================================
# MAIN LOOP
# ============================================

while True:

    clock.tick(FPS)

    screen.blit(bg_img, (0, 0))

    # ========================================
    # EVENTS
    # ========================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()

            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                mouse_pos = pygame.mouse.get_pos()

                if game_state == "START":

                    if start_btn_rect.collidepoint(mouse_pos):

                        reset_game()

                        game_state = "PLAYING"

                elif game_state == "PLAYING":

                    player.shoot()

        if event.type == pygame.KEYDOWN:

            if game_state == "GAME_OVER":

                if event.key == pygame.K_r:

                    reset_game()

                    game_state = "PLAYING"

    # ========================================
    # START SCREEN
    # ========================================

    if game_state == "START":

        title = font.render(
            "SUPERHOT",
            True,
            WHITE
        )

        screen.blit(title, (250, 220))

        pygame.draw.rect(
            screen,
            GRAY,
            start_btn_rect
        )

        btn_text = small_font.render(
            "Start Game",
            True,
            WHITE
        )

        screen.blit(
            btn_text,
            (
                start_btn_rect.x + 45,
                start_btn_rect.y + 15
            )
        )

    # ========================================
    # PLAYING
    # ========================================

    elif game_state == "PLAYING":

        keys = pygame.key.get_pressed()

        # ====================================
        # SUPERHOT TIME SYSTEM
        # ====================================

        if (
            keys[pygame.K_w]
            or keys[pygame.K_s]
            or keys[pygame.K_a]
            or keys[pygame.K_d]
        ):

            time_scale = 1.0

        else:

            time_scale = 0.08

        # ====================================
        # PLAYER
        # ====================================

        if player.alive:

            player.move(keys)

            player.update()

            player.draw()

        # ====================================
        # ENEMIES
        # ====================================

        for enemy in enemy_group:

            enemy.update(time_scale)

            enemy.draw()

            if pygame.sprite.collide_rect(player, enemy):

                game_state = "GAME_OVER"

        # ====================================
        # BULLETS
        # ====================================

        bullet_group.update()

        bullet_group.draw(screen)

        enemy_bullet_group.update(time_scale)

        enemy_bullet_group.draw(screen)

        # ====================================
        # ITEMS
        # ====================================

        item_box_group.update()

        item_box_group.draw(screen)

        # ====================================
        # HEALTH
        # ====================================

        health_bar.draw(player.health)

        # ====================================
        # SCORE
        # ====================================

        score += 0.1 * time_scale * score_multiplier

        # ====================================
        # NEXT LEVEL
        # ====================================

        if score >= level * 100:

            level += 1

            enemy_speed += 0.4

            if shoot_delay > 25:

                shoot_delay -= 8

            score_multiplier += 0.2

            bullet_group.empty()

            enemy_bullet_group.empty()

            start_level(level)

        # ====================================
        # PLAYER DEAD
        # ====================================

        if not player.alive:

            game_state = "GAME_OVER"

        # ====================================
        # UI
        # ====================================

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
            f"Enemies: {len(enemy_group)}",
            True,
            WHITE
        )

        screen.blit(score_text, (10, 40))

        screen.blit(level_text, (10, 70))

        screen.blit(enemy_text, (10, 100))

    # ========================================
    # GAME OVER
    # ========================================

    elif game_state == "GAME_OVER":

        over_text = font.render(
            "GAME OVER",
            True,
            RED
        )

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

        screen.blit(over_text, (250, 180))

        screen.blit(score_text, (260, 260))

        screen.blit(level_text, (250, 300))

        screen.blit(restart_text, (220, 380))

    pygame.display.update()