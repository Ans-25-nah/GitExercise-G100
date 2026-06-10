
# STILL-WORLD (testing)
# Member 1 - DANISH:
#   - Player movement system (WASD)
#   - Shooting mechanism (mouse left click + keyboard F)
#   - Bullet system integration (player's bullet)
#
# Member 2 - DANG YEE TING:
#   - Enemy AI behavior (敌人追踪玩家、射击)
#   - Level logic design & flow (等级提升、敌人生成、难度递增)
#   - Game Difficulty Balancing (调整敌人难度)
#
# Member 3 - ANSON:
#   - Game state management (START, PLAYING, RESULT)
#   - Score tracking system (Score increasing)
#   - UI (Start button、health、score and ending screen)
#   - End game data summary (Result Screen)
# ============================================

import pygame
import sys
import math
import random
import os

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("STILL WORLD")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (255, 60, 60)
GREEN = (50, 255, 120)
GRAY = (120, 120, 120)
YELLOW = (255, 255, 100)

# ==================== GAME VARIABLES ====================
game_state = "START"
level = 1
score = 0
score_multiplier = 1
next_level_ready = False

enemy_base_speed = 2.0
enemy_shoot_delay = 90
enemy_health_base = 100
enemy_bullet_speed = 7.0

MAX_ENEMY_SPEED = 8.0
MIN_SHOOT_DELAY = 25
MAX_ENEMY_HEALTH = 200
MAX_ENEMY_BULLET_SPEED = 12.0

current_enemy_speed = enemy_base_speed
current_shoot_delay = enemy_shoot_delay
current_enemy_health = enemy_health_base
current_enemy_bullet_speed = enemy_bullet_speed

total_shots = 0
total_hits = 0
total_kills = 0

# ==================== FONTS ====================
font = pygame.font.Font(None, 42)
small_font = pygame.font.Font(None, 28)
large_font = pygame.font.Font(None, 64)

# ==================== LOAD IMAGES ====================
bg_img = pygame.image.load('img/background1/background.png').convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (20, 20))
enemy_bullet_img = pygame.image.load(
    'img/icons/enemy_bullet.png').convert_alpha()
enemy_bullet_img = pygame.transform.scale(enemy_bullet_img, (20, 20))
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
health_box_img = pygame.transform.scale(health_box_img, (35, 35))
item_boxes = {'Health': health_box_img}

start_btn_rect = pygame.Rect(300, 320, 200, 50)


def draw_text(text, font, text_col, x, y, center=False):
    img = font.render(text, True, text_col)
    if center:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))

# ==================== PLAYER CLASS ====================


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
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        for animation in ['Idle', 'Run', 'Death']:
            temp_list = []
            frames = [f for f in os.listdir(
                f'img/player1/{animation}') if f.endswith('.png')]
            num_of_frames = len(frames)
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'img/player1/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (80, 80))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()

    def move(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.flip = True
            self.direction = -1
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.flip = False
            self.direction = 1
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

        moving = (keys[pygame.K_a] or keys[pygame.K_d]
                  or keys[pygame.K_w] or keys[pygame.K_s])
        self.update_action(1 if moving else 0)

    def shoot(self):
        global total_shots
        total_shots += 1
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction)
        bullet_group.add(bullet)

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0 if self.action != 2 else len(
                self.animation_list[self.action]) - 1

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
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)

# ==================== ENEMY CLASS (ENEMY 1) ====================


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.health = current_enemy_health
        self.direction = 1
        self.flip = False

        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.shoot_timer = random.randint(0, current_shoot_delay)

        for animation in ['Idle', 'Run', 'Death']:
            temp_list = []
            frames = [f for f in os.listdir(
                f'img/enemy1/{animation}') if f.endswith('.png')]
            num_of_frames = len(frames)
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'img/enemy1/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (80, 80))
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
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.rect.x += (dx / distance) * current_enemy_speed * time_scale
            self.rect.y += (dy / distance) * current_enemy_speed * time_scale
        self.flip = dx < 0
        self.update_action(1)

        self.shoot_timer += 1 * time_scale
        if self.shoot_timer >= current_shoot_delay and distance > 0:
            self.shoot_timer = 0
            bullet = EnemyBullet(
                self.rect.centerx, self.rect.centery, dx/distance, dy/distance)
            enemy_bullet_group.add(bullet)

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0 if self.action != 2 else len(
                self.animation_list[self.action]) - 1

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        global score, total_kills
        if self.health <= 0 and self.alive:
            self.alive = False
            self.update_action(2)
            score += 25
            total_kills += 1
            # Enemy1 随机 1/3 概率掉落血包
            if random.randint(1, 3) == 1:
                item_box_group.add(
                    ItemBox('Health', self.rect.centerx, self.rect.centery))

    def draw(self):
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)


# ==================== ENEMY 2 CLASS (100% Drop Health) ====================
# 新增 Enemy2
class Enemy2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.health = current_enemy_health  # 血量和enemy1一样
        self.direction = 1
        self.flip = False

        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.shoot_timer = random.randint(0, current_shoot_delay)

        # 读取 enemy2 的图片
        for animation in ['Idle', 'Run', 'Death']:
            temp_list = []
            frames = [f for f in os.listdir(
                f'img/enemy2/{animation}') if f.endswith('.png')]
            num_of_frames = len(frames)
            for i in range(num_of_frames):
                img = pygame.image.load(
                    f'img/enemy2/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (80, 80))
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
        distance = math.hypot(dx, dy)
        if distance > 0:
            self.rect.x += (dx / distance) * current_enemy_speed * time_scale
            self.rect.y += (dy / distance) * current_enemy_speed * time_scale
        self.flip = dx < 0
        self.update_action(1)

        self.shoot_timer += 1 * time_scale
        if self.shoot_timer >= current_shoot_delay and distance > 0:
            self.shoot_timer = 0
            bullet = EnemyBullet(
                self.rect.centerx, self.rect.centery, dx/distance, dy/distance)
            enemy_bullet_group.add(bullet)

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0 if self.action != 2 else len(
                self.animation_list[self.action]) - 1

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        global score, total_kills
        if self.health <= 0 and self.alive:
            self.alive = False
            self.update_action(2)
            score += 40  # 死后给多点分数
            total_kills += 1
            # Enemy2 死亡 100% 掉血包
            item_box_group.add(
                ItemBox('Health', self.rect.centerx, self.rect.centery))

    def draw(self):
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)


# ==================== BULLET CLASSES ====================
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction

    def update(self):
        global total_hits
        self.rect.x += self.direction * self.speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
        for enemy in enemy_group:
            if self.rect.colliderect(enemy.rect) and enemy.alive:
                enemy.health -= 50
                total_hits += 1
                self.kill()
                break


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.speed = current_enemy_bullet_speed
        self.dx = dx
        self.dy = dy
        self.image = enemy_bullet_img
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, time_scale):
        self.rect.x += self.dx * self.speed * time_scale
        self.rect.y += self.dy * self.speed * time_scale
        if not self.rect.colliderect((0, 0, WIDTH, HEIGHT)):
            self.kill()
        if self.rect.colliderect(player) and player.alive:
            player.health -= 15
            self.kill()

# ==================== ITEM BOX ====================


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes[item_type]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        if self.rect.colliderect(player) and player.alive:
            if self.item_type == 'Health':
                player.health = min(player.max_health, player.health + 25)
            self.kill()

# ==================== HEALTH BAR ====================


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.max_health = max_health

    def draw(self, health):
        ratio = health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


# ==================== GROUPS ====================
bullet_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

# ==================== LEVEL & DIFFICULTY ====================


def create_enemy():
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x, y = random.randint(0, WIDTH), -50
    elif side == "bottom":
        x, y = random.randint(0, WIDTH), HEIGHT + 50
    elif side == "left":
        x, y = -50, random.randint(0, HEIGHT)
    else:
        x, y = WIDTH + 50, random.randint(0, HEIGHT)

    #  (Enemy2 added)：生成敌人时有 30% 几率生成Enemy2，70% 是普通 Enemy
    if random.random() < 0.3:
        enemy_group.add(Enemy2(x, y))
    else:
        enemy_group.add(Enemy(x, y))


def start_level(current_level):
    enemy_group.empty()
    for _ in range(current_level + 1):
        create_enemy()


def next_level():
    global level, score_multiplier
    global current_enemy_speed, current_shoot_delay, current_enemy_health, current_enemy_bullet_speed
    level += 1
    current_enemy_speed = min(current_enemy_speed + 0.25, MAX_ENEMY_SPEED)
    current_shoot_delay = max(current_shoot_delay - 3, MIN_SHOOT_DELAY)
    current_enemy_health = min(current_enemy_health + 10, MAX_ENEMY_HEALTH)
    current_enemy_bullet_speed = min(
        current_enemy_bullet_speed + 0.2, MAX_ENEMY_BULLET_SPEED)
    score_multiplier += 0.15
    bullet_group.empty()
    enemy_bullet_group.empty()
    start_level(level)


def reset_game():
    global player, health_bar, level, score, score_multiplier, game_state, next_level_ready
    global total_shots, total_hits, total_kills
    global current_enemy_speed, current_shoot_delay, current_enemy_health, current_enemy_bullet_speed
    bullet_group.empty()
    enemy_bullet_group.empty()
    item_box_group.empty()
    player = Player(WIDTH//2, HEIGHT//2, 5, 100)
    health_bar = HealthBar(10, 10, player.health, player.max_health)
    level = 1
    score = 0
    score_multiplier = 1
    total_shots = 0
    total_hits = 0
    total_kills = 0
    next_level_ready = False
    current_enemy_speed = enemy_base_speed
    current_shoot_delay = enemy_shoot_delay
    current_enemy_health = enemy_health_base
    current_enemy_bullet_speed = enemy_bullet_speed
    start_level(level)
    game_state = "PLAYING"

# ==================== UI SCREENS ====================


def show_result_screen():
    hit_rate = (total_hits / total_shots * 100) if total_shots > 0 else 0
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    draw_text("GAME OVER", large_font, RED, WIDTH//2, 80, center=True)
    stats = [
        f"Final Score: {int(score)}",
        f"Level Reached: {level}",
        f"Enemies Killed: {total_kills}",
        f"Shots Fired: {total_shots}",
        f"Shots Hit: {total_hits}",
        f"Accuracy: {hit_rate:.1f}%"
    ]
    for i, stat in enumerate(stats):
        color = YELLOW if i == 5 else WHITE
        draw_text(stat, small_font, color, WIDTH//2, 180 + i*45, center=True)
    draw_text("Press R to Restart", small_font,
              GREEN, WIDTH//2, 500, center=True)
    draw_text("Press ESC to Quit", small_font,
              GRAY, WIDTH//2, 550, center=True)


def show_level_transition():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    draw_text("NEXT LEVEL", large_font, YELLOW,
              WIDTH//2, HEIGHT//2 - 50, center=True)
    draw_text(f"You reached Level {level} !", font,
              WHITE, WIDTH//2, HEIGHT//2 + 20, center=True)
    draw_text("Press ENTER to continue", small_font, GREEN,
              WIDTH//2, HEIGHT//2 + 100, center=True)


# ==================== INIT ====================
reset_game()
game_state = "START"

# ==================== MAIN LOOP ====================
while True:
    clock.tick(FPS)
    screen.blit(bg_img, (0, 0))

    # -------------------- event --------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "START":
                if start_btn_rect.collidepoint(event.pos):
                    reset_game()
            elif game_state == "PLAYING":
                if player.alive:
                    player.shoot()

        if event.type == pygame.KEYDOWN:
            if game_state == "PLAYING" and event.key == pygame.K_f:
                player.shoot()
            elif game_state == "LEVEL_TRANSITION" and event.key == pygame.K_RETURN:
                next_level()
                game_state = "PLAYING"
                next_level_ready = False
            elif game_state == "RESULT":
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif game_state == "START" and event.key == pygame.K_RETURN:
                reset_game()

    # -------------------- update --------------------
    if game_state == "START":
        draw_text("SUPERHOT", font, WHITE, 250, 220)
        pygame.draw.rect(screen, GRAY, start_btn_rect)
        draw_text("Start Game", small_font, WHITE,
                  start_btn_rect.x+45, start_btn_rect.y+15)
        draw_text("Click or Press Enter", small_font,
                  WHITE, WIDTH//2, 420, center=True)

    elif game_state == "PLAYING":
        keys = pygame.key.get_pressed()
        time_scale = 1.0 if any(keys[k] for k in (
            pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)) else 0.08

        if not next_level_ready and score >= level * 100:
            game_state = "LEVEL_TRANSITION"
            next_level_ready = True
            continue

        if player.alive:
            player.move(keys)
            player.update()
            player.draw()
            health_bar.draw(player.health)

        for enemy in enemy_group:
            enemy.update(time_scale)
            enemy.draw()

        # 修改 (Enemy2 逻辑)：玩家直接和敌人撞击时也做了适应，区分掉落概率
        for enemy in list(enemy_group):
            if pygame.sprite.collide_rect(player, enemy) and enemy.alive and player.alive:
                player.health -= 25
                total_kills += 1

                # 判断撞到的是 Enemy 还是 Enemy2 并加分/掉落血包
                if isinstance(enemy, Enemy2):
                    score += 40
                    item_box_group.add(
                        # 100% 掉落
                        ItemBox('Health', enemy.rect.centerx, enemy.rect.centery))
                else:
                    score += 25
                    if random.randint(1, 3) == 1:  # 1/3 概率掉落
                        item_box_group.add(
                            ItemBox('Health', enemy.rect.centerx, enemy.rect.centery))

                enemy.kill()
                if player.health <= 0:
                    player.alive = False
                    player.update_action(2)
                    game_state = "RESULT"
                break

        bullet_group.update()
        bullet_group.draw(screen)
        enemy_bullet_group.update(time_scale)
        enemy_bullet_group.draw(screen)
        item_box_group.update()
        item_box_group.draw(screen)

        score += 0.1 * time_scale * score_multiplier

        if not player.alive:
            game_state = "RESULT"

        draw_text(f"Score: {int(score)}", small_font, WHITE, 10, 40)
        draw_text(f"Level: {level}", small_font, GREEN, 10, 70)
        draw_text(f"Enemies: {len(enemy_group)}", small_font, WHITE, 10, 100)
        draw_text(f"Shots: {total_shots}  Hits: {total_hits}",
                  small_font, WHITE, 10, 130)

    elif game_state == "LEVEL_TRANSITION":
        if player.alive:
            player.update()
            player.draw()
            health_bar.draw(player.health)
        for enemy in enemy_group:
            enemy.update(0)
            enemy.draw()
        bullet_group.draw(screen)
        enemy_bullet_group.draw(screen)
        item_box_group.draw(screen)
        draw_text(f"Score: {int(score)}", small_font, WHITE, 10, 40)
        draw_text(f"Level: {level}", small_font, GREEN, 10, 70)
        draw_text(f"Enemies: {len(enemy_group)}", small_font, WHITE, 10, 100)
        draw_text(f"Shots: {total_shots}  Hits: {total_hits}",
                  small_font, WHITE, 10, 130)
        show_level_transition()

    elif game_state == "RESULT":
        show_result_screen()

    pygame.display.update()
