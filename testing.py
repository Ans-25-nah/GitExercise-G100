
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
    # 构造函数：在创建敌人对象时自动调用（__init__），传入出生坐标 (x, y)
    def __init__(self, x, y):
        # 初始化 sprite工文件夹里的sprite工具里面的功能
        pygame.sprite.Sprite.__init__(self)
        self.alive = True  # 标记敌人是否存活，刚出生时为 True
        self.health = current_enemy_health  # 设置敌人的当前血量，初始值为当前关卡的敌人基础血量
        self.direction = 1  # 设置移动方向，1 表示向右，-1 表示向左
        self.flip = False  # 图片水平翻转标志：False 表示不翻转，True 表示向左转时翻转图片

        self.animation_list = []  # 创建一个空列表 用来储存所有的动画图片（Idle  Run  Death 三个动作）
        self.frame_index = 0  # 从第 0 帧开始播放
        self.action = 0  # 初始化当前动作：0：Idle，1：Run，2：Death
        # pygame自带的计时器
        self.update_time = pygame.time.get_ticks()  # 记录上一次更新动画帧的时间戳（单位：毫秒）
        self.shoot_timer = random.randint(
            0, current_shoot_delay)  # 随机初始化射击计时器，避免所有敌人同时开枪

        # 循环遍历三种动画文件夹
        for animation in ['Idle', 'Run', 'Death']:
            temp_list = []  # 创建一个临时列表，用于存放当前这个动作的所有图片帧
            frames = [f for f in os.listdir(  # 扫描对应的文件夹，找出所有以 .png 结尾的文件名，存进列表中
                f'img/enemy1/{animation}') if f.endswith('.png')]
            num_of_frames = len(frames)  # 计算这个动作一共有多少帧图片
            for i in range(num_of_frames):  # 根据帧数循环，依次读取图片
                img = pygame.image.load(  # 读取单个图片文件，并转换成带有透明通道的 Surface 对象
                    f'img/enemy1/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(
                    img, (80, 80))  # 将图片缩放到 80x80 像素的大小
                temp_list.append(img)  # 将缩放后的图片添加进临时列表
            # 把当前动作的所有图片列表，添加到大动画列表中（形成二维列表）
            self.animation_list.append(temp_list)

        # 根据当前的 action 和 frame_index 设定敌人当前要显示的图片
        self.image = self.animation_list[self.action][self.frame_index]
        # 获取图片的矩形区域（用于控制位置和碰撞检测）
        self.rect = self.image.get_rect()
        # 将矩形区域的中心点对齐到传入的出生坐标 (x, y)
        self.rect.center = (x, y)

    # 每一帧更新敌人状态的主函数，传入时间缩放值 time_scale (实现SUPERHOT时间缓慢效果)
    def update(self, time_scale):
        # 调用更新动画帧的函数
        self.update_animation()
        # 调用检查健康状态的函数（看死了没）
        self.check_alive()
        # 如果敌人已经死了，直接结束更新，不执行下面的移动和射击逻辑
        if not self.alive:
            return

        # 计算玩家中心点与敌人中心点在 X 轴上的距离
        dx = player.rect.centerx - self.rect.centerx
        # 计算玩家中心点与敌人中心点在 Y 轴上的距离
        dy = player.rect.centery - self.rect.centery
        # 使用直角三角形斜边公式，计算敌人到玩家的绝对直线距离
        distance = math.hypot(dx, dy)
        # 如果距离大于 0（防止除以 0 导致报错）
        if distance > 0:
            # 根据 X 轴距离比例，结合移动速度和时间缩放，更新敌人的 X 坐标（往玩家走）
            self.rect.x += (dx / distance) * current_enemy_speed * time_scale
            # 根据 Y 轴距离比例，结合移动速度和时间缩放，更新敌人的 Y 坐标（往玩家走）
            self.rect.y += (dy / distance) * current_enemy_speed * time_scale

        # 如果 dx < 0 说明玩家在敌人的左边，self.flip 设为 True (图片翻转)
        self.flip = dx < 0
        # 只要在移动，就把动作切换为 1 (Run 跑步)
        self.update_action(1)

        # 射击计时器累加时间（乘以 time_scale 受到时间变慢系统的控制）
        self.shoot_timer += 1 * time_scale
        # 如果计时器达到了当前关卡的射击延迟，并且玩家还活着（距离 > 0）
        if self.shoot_timer >= current_shoot_delay and distance > 0:
            # 重置射击计时器
            self.shoot_timer = 0
            # 创建一颗敌人子弹，传入敌人中心点，以及子弹飞向玩家的方向向量 (dx/distance, dy/distance)
            bullet = EnemyBullet(
                self.rect.centerx, self.rect.centery, dx/distance, dy/distance)
            # 将创建的子弹加入到敌人子弹精灵组中，让它在屏幕上渲染更新
            enemy_bullet_group.add(bullet)

    # 负责处理动画帧切替的函数
    def update_animation(self):
        # 设定动画帧切换的冷却时间为 100 毫秒（每 0.1 秒换一帧）
        ANIMATION_COOLDOWN = 100
        # 根据当前的动作索引和图片帧索引，更新 self.image
        self.image = self.animation_list[self.action][self.frame_index]
        # 如果当前系统时间减去上一次更新的时间，大于设定的冷却时间
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            # 更新时间戳为当前系统时间
            self.update_time = pygame.time.get_ticks()
            # 帧索引加 1，播放下一帧图片
            self.frame_index += 1
        # 如果帧索引超过了当前动作图片的总张数（放完了）
        if self.frame_index >= len(self.animation_list[self.action]):
            # 如果当前的动作用不是 2 (Death 死亡)，就重置回第 0 帧循环播放；如果是死亡动画，就停在最后一帧
            self.frame_index = 0 if self.action != 2 else len(
                self.animation_list[self.action]) - 1

    # 负责切换动作状态的函数（比如从 Idle 换到 Run）
    def update_action(self, new_action):
        # 如果传入的新动作和当前正在运行的动作不一样
        if new_action != self.action:
            # 把动作修改为新动作
            self.action = new_action
            # 帧索引归零，从新动画的第一帧开始播放
            self.frame_index = 0
            # 重置动画更新时间戳
            self.update_time = pygame.time.get_ticks()

    # 负责检查敌人死活的函数
    def check_alive(self):
        # 引入全局变量：分数、总击杀数
        global score, total_kills
        # 如果血量小于等于 0，并且当前状态还是活着的（说明是刚刚死掉）
        if self.health <= 0 and self.alive:
            # 将存活状态设为 False
            self.alive = False
            # 将动作切换为 2 (Death 死亡动画)
            self.update_action(2)
            # 游戏分数增加 25 分
            score += 25
            # 总击杀数加 1
            total_kills += 1
            # Enemy1 随机 1/3 的概率掉落血包（随机抽 1, 2, 3，如果是 1 就掉落）
            if random.randint(1, 3) == 1:
                # 创建一个血包，位置在敌人死掉的中心点，并加入到道具精灵组
                item_box_group.add(
                    ItemBox('Health', self.rect.centerx, self.rect.centery))

    # 负责把敌人绘制到屏幕上的函数
    def draw(self):
        # 使用 blit 将图片画在屏幕上，pygame.transform.flip 用来控制图片是否需要左右翻转
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)


# ==================== ENEMY 2 CLASS (100% Drop Health) ====================

# 新增 Enemy2 类，继承自 pygame 的精灵类（Sprite），专门用来 100% 爆血包
class Enemy2(pygame.sprite.Sprite):
    # 构造函数：传入出生坐标 (x, y)
    def __init__(self, x, y):
        # 初始化父类 pygame.sprite.Sprite
        pygame.sprite.Sprite.__init__(self)
        # 标记敌人2是否存活
        self.alive = True
        # 设置血量，初始值和普通敌人 1 一样
        self.health = current_enemy_health
        # 设置移动方向（1为右，-1为左）
        self.direction = 1
        # 图片水平翻转标志
        self.flip = False

        # 创建一个空列表，用来储存 Enemy2 的所有动画图片
        self.animation_list = []
        # 初始化当前播放的动画帧索引
        self.frame_index = 0
        # 初始化当前动作（0: Idle, 1: Run, 2: Death）
        self.action = 0
        # 记录上一次更新动画帧的时间戳
        self.update_time = pygame.time.get_ticks()
        # 随机初始化射击计时器
        self.shoot_timer = random.randint(0, current_shoot_delay)

        # 循环读取 enemy2 的图片资源
        for animation in ['Idle', 'Run', 'Death']:
            # 创建一个临时列表存放当前动作的图片
            temp_list = []
            # 获取 img/enemy2 文件夹下对应动作的所有 .png 图片文件名
            frames = [f for f in os.listdir(
                f'img/enemy2/{animation}') if f.endswith('.png')]
            # 计算总帧数
            num_of_frames = len(frames)
            # 循环读取图片
            for i in range(num_of_frames):
                # 加载 enemy2 的图片，并转换透明通道
                img = pygame.image.load(
                    f'img/enemy2/{animation}/{i}.png').convert_alpha()
                # 缩放到 80x80 大小
                img = pygame.transform.scale(img, (80, 80))
                # 放进临时列表
                temp_list.append(img)
            # 将该动作的完整图片组，添加进大动画列表中
            self.animation_list.append(temp_list)

        # 设定 Enemy2 当前要显示的图片
        self.image = self.animation_list[self.action][self.frame_index]
        # 获取图片的矩形区域
        self.rect = self.image.get_rect()
        # 设置矩形中心坐标为出生点
        self.rect.center = (x, y)

    # 每一帧更新敌人2状态的主函数，传入时间缩放值 time_scale
    def update(self, time_scale):
        # 更新动画帧
        self.update_animation()
        # 检查是否死亡
        self.check_alive()
        # 如果死了，直接退出更新，不再移动和射击
        if not self.alive:
            return

        # 计算与玩家的 X 轴距离差
        dx = player.rect.centerx - self.rect.centerx
        # 计算与玩家的 Y 轴距离差
        dy = player.rect.centery - self.rect.centery
        # 计算直线距离
        distance = math.hypot(dx, dy)
        # 追踪玩家移动逻辑
        if distance > 0:
            self.rect.x += (dx / distance) * current_enemy_speed * time_scale
            self.rect.y += (dy / distance) * current_enemy_speed * time_scale

        # 根据玩家在左还是在右，控制图片是否水平翻转
        self.flip = dx < 0
        # 处于移动状态，动作设为 1 (Run)
        self.update_action(1)

        # 射击控制逻辑
        self.shoot_timer += 1 * time_scale
        if self.shoot_timer >= current_shoot_delay and distance > 0:
            self.shoot_timer = 0
            # 创建开火子弹飞向玩家
            bullet = EnemyBullet(
                self.rect.centerx, self.rect.centery, dx/distance, dy/distance)
            enemy_bullet_group.add(bullet)

    # 动画帧更新函数（和 Enemy1 相同）
    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0 if self.action != 2 else len(
                self.animation_list[self.action]) - 1

    # 动作切换函数（和 Enemy1 相同）
    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    # 检查敌人2是否死亡以及处理 100% 掉落
    def check_alive(self):
        global score, total_kills  # 引入全局变量
        if self.health <= 0 and self.alive:  # 如果血量小于等于0
            self.alive = False  # 死掉
            self.update_action(2)  # 播Death
            score += 40  # 特殊的Enemy2 死后加 40 分
            total_kills += 1  # 击杀数加 1
            # 100% 在死掉的位置生成一个健康血包
            item_box_group.add(
                ItemBox('Health', self.rect.centerx, self.rect.centery))

    # 绘制敌人2的函数
    def draw(self):
        # 将图片画在屏幕上，处理是否左右翻转
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)

# ===================hit text================new added


class FloatingText(pygame.sprite.Sprite):
    def __init__(self, x, y, text="Hit", color=(255, 255, 100)):  # 当子弹打中敌人、要创建这个文字时，传入文字生成的坐标
        super().__init__()
        # 使用你现有的 small_font 渲染文本
        self.image = small_font.render(text, True, color)  # 把文本字符串真正的“画”成一张图片
        # 获取这张字体的图片矩形大小，并把它的中心点对齐到敌人头上
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0  # 文字的寿命计时器

    def update(self, time_scale):
        # 让文字向上飘，乘以 time_scale 可以让它配合变慢机制
        self.rect.y -= 1.5 * time_scale  # 每一帧更新时，让文字的 Y 坐标减去 1.5（在屏幕上就是往上飘）
        self.counter += 1 * time_scale
        if self.counter >= 25:  # 当计时器达到25就会selfkill，防止游戏因为产生太多文字而卡顿。
            self.kill()


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
                hit_text = FloatingText(  # ----------------
                    # rectcenterx：获取敌人的中心 X 坐标。，-10:敌人图片上 10 个像素的位置。
                    enemy.rect.centerx, enemy.rect.top - 10, "Hit")
                # new added 用 add() 把它扔进篮子里------------------
                floating_text_group.add(hit_text)
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
floating_text_group = pygame.sprite.Group()  # new added------------------

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

    # 每次刷新，随机抽一个敌人时
    if random.random() < 0.3:  # 有 30% 几率生成Enemy2
        enemy_group.add(Enemy2(x, y))
    else:
        enemy_group.add(Enemy(x, y))  # 70% 是普通 Enemy


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
    floating_text_group.empty()  # new added 把屏幕上旧 “Hit” 字全部清空---------------
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

        # 玩家直接和敌人撞击时，
        for enemy in list(enemy_group):
            if pygame.sprite.collide_rect(player, enemy) and enemy.alive and player.alive:
                player.health -= 25
                total_kills += 1

                # 判断撞到的是 Enemy 还是 Enemy2 并加分/掉落血包
                if isinstance(enemy, Enemy2):  # insintance（）检查enemy是不是enemy2
                    score += 40
                    item_box_group.add(  # 把工具箱里面的东西正式生效
                        # 100% 掉落
                        # 死掉的中心掉血包
                        ItemBox('Health', enemy.rect.centerx, enemy.rect.centery))
                else:  # 如果不是
                    score += 25
                    if random.randint(1, 3) == 1:  # 1/3 概率掉落血包
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
        # 让篮子里所有的 “Hit” 字体执行上面写好的“往上飘、涨寿命”的逻辑。
        floating_text_group.update(time_scale)
        # new added 把所有还没消失的 “Hit” 文字画到屏幕上------------------
        floating_text_group.draw(screen)

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
