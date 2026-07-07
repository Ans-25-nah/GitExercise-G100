# STILL-WORLD (testing)
# Member 1 - DANISH:
#   - Player movement system (WASD)
#   - Shooting mechanism (mouse left click + keyboard F)
#   - Bullet system integration (player's bullet)
#   - Collision detection (Walls & Boundaries)
#
# Member 2 - DANG YEE TING:
#   - Enemy AI behavior (敌人追踪玩家、射击)
#   - Level logic design & flow (等级提升、敌人生成、难度递增)
#   - Game Difficulty Balancing (调整敌人难度)
#   - Enemy2 (100%掉落血包)
#
# Member 3 - ANSON:
#   - Game state management (START, PLAYING, TRANSITION, RESULT)
#   - Score tracking system (Score increasing)
#   - UI (Start button、health、score and ending screen)
#   - End game data summary (Result Screen)
#   - Music & Sound
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

# 我和ans一起弄的，中间的是我的part，其他的都是ans，我会顺便套用他设的东西而已
game_state = "START"
level = 1
score = 0
score_multiplier = 1
next_level_ready = False

enemy_base_speed = 2.0  # 敌人基础移动速度
enemy_shoot_delay = 90  # 敌人基础射击延迟（数字越大，开火越慢）
enemy_health_base = 100  # 敌人基础血量
enemy_bullet_speed = 7.0  # 敌人基础子弹速度

MAX_ENEMY_SPEED = 8.0   # 敌人能达到的最大速度上限
MIN_SHOOT_DELAY = 25  # 敌人开火间隔的最小值（数字越小，开火越快）
MAX_ENEMY_HEALTH = 200  # 敌人能达到的最大血量上限
MAX_ENEMY_BULLET_SPEED = 12.0  # 敌人子弹的最大速度上限

# 变量，方便后续进行调整
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
wall_img = pygame.image.load('img/wall.png').convert_alpha()
wall_img = pygame.transform.scale(wall_img, (100, 100))

item_boxes = {'Health': health_box_img}

# ==================== LOAD SOUNDS ====================
pygame.mixer.init()


def load_sound(name):
    try:
        return pygame.mixer.Sound(os.path.join('sfx', name))
    except:
        print(f"Warning: Sound '{name}' not found.")
        return None


shoot_sound = load_sound('shoot.wav')
pickup_sound = load_sound('pickup.wav')
gameover_sound = load_sound('gameover.wav')
bgm_path = os.path.join('sfx', 'bgm_playing.wav')

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
            num_of_frames = len(os.listdir(f'img/player1/{animation}'))
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
        if not self.alive:
            return

        dx = 0
        dy = 0

        if keys[pygame.K_a]:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if keys[pygame.K_d]:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_s]:
            dy = self.speed

        # X Movement & Wall Collision
        self.rect.x += dx
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        hit_walls = pygame.sprite.spritecollide(self, wall_group, False)
        for wall in hit_walls:
            if dx > 0:
                self.rect.right = wall.rect.left
            if dx < 0:
                self.rect.left = wall.rect.right

        # Y Movement & Wall Collision
        self.rect.y += dy
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        hit_walls = pygame.sprite.spritecollide(self, wall_group, False)
        for wall in hit_walls:
            if dy > 0:
                self.rect.bottom = wall.rect.top
            if dy < 0:
                self.rect.top = wall.rect.bottom

        moving = (dx != 0 or dy != 0)
        self.update_action(1 if moving else 0)

    def shoot(self):
        global total_shots
        if self.alive:
            total_shots += 1
            if shoot_sound:
                shoot_sound.play()
            bullet = Bullet(self.rect.centerx,
                            self.rect.centery, self.direction)
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
            if self.alive:
                self.alive = False
                self.update_action(2)

    def draw(self):
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)

# ==================== ENEMY CLASS (ENEMY 1) 普通====================


class Enemy(pygame.sprite.Sprite):  # make an enemy model, can use pygame's tools(sprite)
    # __init__ =format
    # def在class的下面叫function,self是指enemy，定义这个enemy的专属属性，当游戏里创建一个新敌人时，传入它出生的坐标 x 和 y。
    def __init__(self, x, y):
        # .__init__ =start using
        pygame.sprite.Sprite.__init__(self)  # class+def+pygame是创造觉得的固定用法
        # ------ basic setting
        self.alive = True  # enemy status，True=alive,False=death
        self.health = current_enemy_health  # set current lvl enemy health bar
        self.direction = 1  # 没有被用到的code，从danish 那边复制过来的，设置移动方向，1 表示向右，-1 表示向左
        self.flip = False  # 刚出现的时候enemy默认不反转：False ，<0=True 表示向左转时翻转图片

        # make a empty list(box)to put all the photo(Idle  Run  Death 3动作)
        self.animation_list = []
        self.frame_index = 0  # 从第 0 帧开始播放
        self.action = 0  # 初始化当前动作：0：Idle，1：Run，2：Death
        # pygame自带的计时器
        self.update_time = pygame.time.get_ticks()  # 记录上一次更新动画帧的时间戳（单位：毫秒）
        self.shoot_timer = random.randint(
            0, current_shoot_delay)  # 随机初始化射击计时器，避免所有敌人同时开枪

        # make a loop for animation -----anson
        # for--in--是一个function，可以自动抽东西出来，【】是list
        for animation in ['Idle', 'Run', 'Death']:
            temp_list = []  # make a list(临时)，to save current 动作的所有帧数照片
            # 扫描对应的文件夹，找出所有以 .png 结尾的文件名，存进列表中
            # 名字=拿数量（os.listdir=把这个file的东西list完出来，
            # f''是可以在一堆字符串放{变量}
            num_of_frames = len(os.listdir(f'img/enemy1/{animation}'))
            # automatic repeat png
            # i是从0开始自动到下一个号码
            # for
            for i in range(num_of_frames):  # 计算这个动作一共有多少帧图片
                # pygame
                img = pygame.image.load(  # 根据帧数循环，依次读取图片
                    # 读取单个图片文件，并转换成带有透明通道的 Surface 对象，convert alpha和png一起 背景变透明
                    f'img/enemy1/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(  # size
                    img, (80, 80))  # 将图片缩放到 80x80 宽高像素的大小
                # ---放照片---
                temp_list.append(img)  # 将缩放后的图片添加进临时列表
            # 把当前动作的所有图片列表，添加到大动画列表中（形成二维列表）
            # .append 放进
            self.animation_list.append(temp_list)

        # 根据当前的 action 和 frame_index 设定敌人当前要显示的图片
            # 现在播到第几帧
        self.image = self.animation_list[self.action][self.frame_index]

        self.rect = self.image.get_rect()  # 获取图片的矩形区域（用于控制位置和碰撞检测）
        self.rect.center = (x, y)  # 将矩形区域的中心点对齐到传入的出生坐标 (x, y)

    # 每一帧更新敌人状态的主函数，传入时间缩放值 time_scale (实现SUPERHOT时间缓慢效果)

    def update(self, time_scale):
        # 调用更新动画帧的函数
        self.update_animation()
        # 调用检查健康状态的函数（看死了没）
        self.check_alive()
        # 如果敌人已经死了，直接结束更新，不执行下面的移动和射击逻辑
        if not self.alive:  # if not true=false，if not false=true
            return
        # 计算玩家中心点与敌人中心点在 X 轴上的距离
        dx = player.rect.centerx - self.rect.centerx
        # 计算玩家中心点与敌人中心点在 Y 轴上的距离
        dy = player.rect.centery - self.rect.centery
        # 使用直角三角形斜边公式，math是python的功能
        distance = math.hypot(dx, dy)

       # 如果距离大于 0（防止除以 0 导致报错）这个才是敌人移动
        if distance > 0:
            # 根据 X 轴距离比例，结合移动速度和时间缩放，更新敌人的 X 坐标（往玩家走）
            step_x = (dx / distance) * current_enemy_speed * time_scale
            # 根据 Y 轴距离比例，结合移动速度和时间缩放，更新敌人的 Y 坐标（往玩家走）
            step_y = (dy / distance) * current_enemy_speed * time_scale

            # Enemy X Wall Collision：danish 如果撞到墙上
            self.rect.x += step_x  # 先加自己的长方形和敌人
            hit_walls = pygame.sprite.spritecollide(self, wall_group, False)
            for wall in hit_walls:
                if step_x > 0:
                    self.rect.right = wall.rect.left
                if step_x < 0:
                    self.rect.left = wall.rect.right

            # Enemy Y Wall Collision
            self.rect.y += step_y
            hit_walls = pygame.sprite.spritecollide(self, wall_group, False)
            for wall in hit_walls:
                if step_y > 0:
                    self.rect.bottom = wall.rect.top
                if step_y < 0:
                    self.rect.top = wall.rect.bottom

        self.flip = dx < 0
        self.update_action(1)

        self.shoot_timer += 1 * time_scale
        if self.shoot_timer >= current_shoot_delay and distance > 0:
            self.shoot_timer = 0
            bullet = EnemyBullet(
                self.rect.centerx, self.rect.centery, dx/distance, dy/distance)
            enemy_bullet_group.add(bullet)

   # 负责处理动画帧切替的函数

    def update_animation(self):  # anson
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
        if new_action != self.action:  #
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

# ==================== ENEMY 2 CLASS (100% Drop Health)精英 ====================

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

            num_of_frames = len(os.listdir(f'img/enemy2/{animation}'))
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

    def update(self, time_scale):  # 每一帧更新敌人2状态的主函数，传入时间缩放值 time_scale
        self.update_animation()  # 更新动画帧
        self.check_alive()  # 检查是否死亡
        if not self.alive:  # 如果死了，直接退出更新，不再移动和射击
            return

        # 计算与玩家的 X 轴距离差
        dx = player.rect.centerx - self.rect.centerx
        # 计算与玩家的 Y 轴距离差
        dy = player.rect.centery - self.rect.centery
        # 计算直线距离
        distance = math.hypot(dx, dy)
        # 追踪玩家移动逻辑
        if distance > 0:
            step_x = (dx / distance) * current_enemy_speed * time_scale
            step_y = (dy / distance) * current_enemy_speed * time_scale

            # Enemy X Wall Collision ---danish
            self.rect.x += step_x
            hit_walls = pygame.sprite.spritecollide(self, wall_group, False)
            for wall in hit_walls:
                if step_x > 0:
                    self.rect.right = wall.rect.left
                if step_x < 0:
                    self.rect.left = wall.rect.right

            # Enemy Y Wall Collision ----danish
            self.rect.y += step_y
            hit_walls = pygame.sprite.spritecollide(self, wall_group, False)
            for wall in hit_walls:
                if step_y > 0:
                    self.rect.bottom = wall.rect.top
                if step_y < 0:
                    self.rect.top = wall.rect.bottom

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
            score += 40  # Enemy2 gives 40 points
            total_kills += 1  # 击杀数加 1
            # 100% drop health
            item_box_group.add(
                ItemBox('Health', self.rect.centerx, self.rect.centery))

    # 绘制敌人2的函数
    def draw(self):
        # 将图片画在屏幕上，处理是否左右翻转
        screen.blit(pygame.transform.flip(
            self.image, self.flip, False), self.rect)

# ==================== FLOATING TEXT ====================


class FloatingText(pygame.sprite.Sprite):  # 创造一个会飞的文字的模具
    def __init__(self, x, y, text="Hit", color=YELLOW):  # 初始化文字，文字坐标，hit，黄色 语法必须要用self
        super().__init__()  # 调用工具箱的语法，和pygame.什么.什么是一样的的功能，super比较方便
        # 用small_font 渲染.render（1010变成hit）
        self.image = small_font.render(text, True, color)  # hit，光滑，黄色
        # 给hit图片一个长方形，并把它的中心点对齐到敌人头上
        self.rect = self.image.get_rect(center=(x, y))  # enemy 中间出现
        self.counter = 0  # 文字的寿命计时器从0开始

    def update(self, time_scale):
        # pygame的世界是下是+，上是-，让文字向上飘，乘以 time_scale 可以让它配合变慢机制
        self.rect.y -= 1.5 * time_scale  # 每一帧更新时，让文字的 Y 坐标减去 1.5（在屏幕上就是往上飘）
        self.counter += 1 * time_scale   # 每一帧更新加一点
        if self.counter >= 25:  # 如果加到25就会self.kill（开除），防止游戏因为产生太多文字而卡顿
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
            return

        # Bullet vs Wall Collision
        if pygame.sprite.spritecollide(self, wall_group, False):
            self.kill()
            return

        for enemy in enemy_group:
            if self.rect.colliderect(enemy.rect) and enemy.alive:
                enemy.health -= 50
                total_hits += 1
                floating_text_group.add(FloatingText(
                    enemy.rect.centerx, enemy.rect.top - 10, "Hit"))
                self.kill()
                break


# 做一个enemy bullet的模具
class EnemyBullet(pygame.sprite.Sprite):
    # 当敌人开火时，会传入四个参数：子弹发射的起点坐标 (x, y)，以及子弹要飞行的方向向量 (dx, dy)（也就是朝向玩家的方向）。
    def __init__(self, x, y, dx, dy):
        super().__init__()
        # 设定子弹的飞行速度。它直接读取你之前设定的当前关卡的实时子弹速度。这意味着随着关卡变高，敌人子弹飞得越来越快，躲避难度越来越大！
        self.speed = current_enemy_bullet_speed
       # 把传进来的 X 轴和 Y 轴的方向记录在子弹自己身上，告诉子弹接下来要往哪里飞。
        self.dx = dx
        self.dy = dy
        # 给子弹穿上皮肤（子弹的图片），并在子弹图片周围生成一个隐形的“碰撞矩形块”，把它的中心点对准子弹刚出生的 (x, y) 坐标。
        self.image = enemy_bullet_img
        self.rect = self.image.get_rect(center=(x, y))
     # 让子弹飞（受时间变慢机制控制）

    def update(self, time_scale):
        self.rect.x += self.dx * self.speed * time_scale
        self.rect.y += self.dy * self.speed * time_scale
       # 检查子弹的矩形块是不是已经不在游戏屏幕（从宽高 0左上角, 0右下角 到 WIDTH, HEIGHT）的内部了。如果飞出去了，就执行 self.kill()。
       # self.rect.colliderect 是pygame检查长方形有没有碰撞到的工具
        if not self.rect.colliderect(0, 0, WIDTH, HEIGHT):
            self.kill()  # self.kill() 是 Pygame 的自带功能，意思是把这颗子弹从内存里彻底抹抹掉（毁灭）。如果不删掉，飞出屏幕的子弹会无限飞下去，积累多了游戏就会越来越卡。
            return

        # Enemy Bullet vs Wall Collision
        # 检查子弹有没有撞上(pygame tool)墙（wall_group：子弹，墙壁，不要让墙壁消失）
        if pygame.sprite.spritecollide(self, wall_group, False):
            self.kill()  # 如果撞上了，子弹立刻消失（self.kill()）
            return
        # 子弹撞到player，player 存活
        if self.rect.colliderect(player) and player.alive:
            player.health -= 15  # 扣15点血
            self.kill()  # kill is 方便省心

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
                if pickup_sound:
                    pickup_sound.play()
            self.kill()

# ==================== WALL CLASS ====================


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = wall_img
        self.rect = self.image.get_rect(center=(x, y))

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
floating_text_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()

# ==================== LEVEL & DIFFICULTY ====================


def create_enemy():
    # 随机选一个，【】list里面有四个选项
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        x, y = random.randint(0, WIDTH), -50  # ramdom.ramdint随机选区间
    elif side == "bottom":
        x, y = random.randint(0, WIDTH), HEIGHT + 50
    elif side == "left":
        x, y = -50, random.randint(0, HEIGHT)
    else:
        x, y = WIDTH + 50, random.randint(0, HEIGHT)

    # 30% chance to spawn Enemy2, 70% Enemy1
    if random.random() < 0.3:  # 有 30% 几率生成Enemy2
        enemy_group.add(Enemy2(x, y))  # .add是因为有超大篮子
    else:
        enemy_group.add(Enemy(x, y))  # 70% 是普通 Enemy


def start_level(current_level):
    enemy_group.empty()
    for _ in range(current_level + 1):  # _=no matter how much，keep repeating
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

    try:
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)
    except:
        print("Warning: Background music not found or unsupported format.")

    game_state = "PLAYING"

# ==================== UI SCREENS ====================


def show_result_screen():
    hit_rate = (total_hits / total_shots * 100) if total_shots > 0 else 0

    if hit_rate >= 90:
        rank = "S"
        rank_color = YELLOW
    elif hit_rate >= 75:
        rank = "A"
        rank_color = GREEN
    elif hit_rate >= 60:
        rank = "B"
        rank_color = WHITE
    else:
        rank = "C"
        rank_color = RED

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    pygame.draw.rect(screen, (40, 40, 40),
                     (170, 70, 460, 460), border_radius=15)
    pygame.draw.rect(screen, WHITE, (170, 70, 460, 460), 3, border_radius=15)

    draw_text("GAME OVER", large_font, RED, WIDTH//2, 120, center=True)
    draw_text(f"RANK {rank}", large_font,
              rank_color, WIDTH//2, 190, center=True)

    stats = [
        f"Final Score : {int(score)}",
        f"Level Reached : {level}",
        f"Enemies Killed : {total_kills}",
        f"Shots Fired : {total_shots}",
        f"Shots Hit : {total_hits}",
        f"Accuracy : {hit_rate:.1f}%"
    ]

    for i, stat in enumerate(stats):
        draw_text(stat, small_font, WHITE, WIDTH//2, 260 + i * 40, center=True)

    draw_text("Press R To Restart", small_font,
              GREEN, WIDTH//2, 485, center=True)
    draw_text("Press ESC To Quit", small_font,
              GRAY, WIDTH//2, 505, center=True)


def show_level_transition():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    pygame.draw.rect(screen, (40, 40, 40),
                     (180, 120, 440, 320), border_radius=15)
    pygame.draw.rect(screen, WHITE, (180, 120, 440, 320), 3, border_radius=15)

    draw_text("LEVEL CLEARED", large_font, YELLOW, WIDTH//2, 170, center=True)
    draw_text(f"Welcome To Level {level + 1}",
              font, WHITE, WIDTH//2, 230, center=True)
    draw_text("Difficulty Increased", small_font,
              RED, WIDTH//2, 290, center=True)
    draw_text("+ Enemy Speed", small_font, WHITE, WIDTH//2, 330, center=True)
    draw_text("+ Enemy Health", small_font, WHITE, WIDTH//2, 360, center=True)
    draw_text("+ Enemy Bullet Speed", small_font,
              WHITE, WIDTH//2, 390, center=True)
    draw_text("Press ENTER To Continue", small_font,
              GREEN, WIDTH//2, 470, center=True)


# ==================== INIT ====================
reset_game()
game_state = "START"

# Generate walls
wall_group.add(Wall(200, 300))
wall_group.add(Wall(600, 300))

pause_snapshot = None

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
            if game_state == "PLAYING" and event.key == pygame.K_p:
                pause_snapshot = screen.copy()
                game_state = "PAUSE"
            elif game_state == "PAUSE" and event.key == pygame.K_p:
                game_state = "PLAYING"
            elif game_state == "PAUSE" and event.key == pygame.K_m:
                reset_game()
                pygame.mixer.music.stop()
                game_state = "START"
                pause_snapshot = None
            elif game_state == "PLAYING" and event.key == pygame.K_f:
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
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        draw_text("STILL WORLD", large_font, WHITE, WIDTH//2, 160, center=True)
        draw_text("Time Moves When You Move", small_font,
                  YELLOW, WIDTH//2, 210, center=True)

        mouse_pos = pygame.mouse.get_pos()
        if start_btn_rect.collidepoint(mouse_pos):
            button_color = (180, 180, 180)
            border_color = WHITE
        else:
            button_color = (100, 100, 100)
            border_color = GRAY

        pygame.draw.rect(screen, button_color,
                         start_btn_rect, border_radius=12)
        pygame.draw.rect(screen, border_color,
                         start_btn_rect, 3, border_radius=12)
        draw_text("START GAME", small_font, BLACK, start_btn_rect.centerx,
                  start_btn_rect.centery - 10, center=True)

        draw_text("Click Button or Press ENTER", small_font,
                  WHITE, WIDTH//2, 420, center=True)
        draw_text("WASD = Move", small_font, GREEN, WIDTH//2, 470, center=True)
        draw_text("Mouse Click / F = Shoot", small_font,
                  GREEN, WIDTH//2, 500, center=True)

    elif game_state == "PLAYING":
        keys = pygame.key.get_pressed()
        time_scale = 1.0 if any(keys[k] for k in (  # set time scale
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

        # Player-Enemy collision
        # player 撞到enemy
        for enemy in list(enemy_group):

            if pygame.sprite.collide_rect(player, enemy) and enemy.alive and player.alive:
                player.health -= 25
                total_kills += 1
                # 判断撞到的是 Enemy 还是 Enemy2 并加分/掉落血包=isinstance( 谁 , 什么身份 )
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
        wall_group.draw(screen)

        score += 0.1 * time_scale * score_multiplier

        if not player.alive:
            pygame.mixer.music.fadeout(500)
            if gameover_sound:
                gameover_sound.play()
            game_state = "RESULT"

        draw_text(f"Score: {int(score)}", font, (0, 0, 139), 10, 40)
        draw_text(f"Enemies: {len(enemy_group)}", small_font, WHITE, 10, 90)
        draw_text(f"Shots: {total_shots}  Hits: {total_hits}",
                  small_font, WHITE, 10, 120)

        level_text = str(level)
        text_surface = font.render(level_text, True, (0, 0, 139))
        text_rect = text_surface.get_rect()
        circle_center = (WIDTH - 70, 50)
        radius = max(text_rect.width, text_rect.height) // 2 + 20
        pygame.draw.circle(screen, (173, 216, 230), circle_center, radius)
        text_rect.center = circle_center
        screen.blit(text_surface, text_rect)

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
        wall_group.draw(screen)

        draw_text(f"Score: {int(score)}", font, (0, 0, 139), 10, 40)
        draw_text(f"Enemies: {len(enemy_group)}", small_font, WHITE, 10, 90)

        level_text = str(level)
        text_surface = font.render(level_text, True, (0, 0, 139))
        text_rect = text_surface.get_rect()
        circle_center = (WIDTH - 70, 50)
        radius = max(text_rect.width, text_rect.height) // 2 + 20
        pygame.draw.circle(screen, (173, 216, 230), circle_center, radius)
        text_rect.center = circle_center
        screen.blit(text_surface, text_rect)

        show_level_transition()

    elif game_state == "RESULT":
        show_result_screen()

    elif game_state == "PAUSE":
        screen.blit(pause_snapshot, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        draw_text("PAUSED", large_font, YELLOW, WIDTH //
                  2, HEIGHT//2 - 20, center=True)
        draw_text("Press P to resume", small_font, WHITE,
                  WIDTH//2, HEIGHT//2 + 30, center=True)
        draw_text("Press M to Main Menu", small_font, WHITE,
                  WIDTH//2, HEIGHT//2 + 70, center=True)

    pygame.display.update()
