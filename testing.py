#STILL-WORLD (testing)
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
#   - Game state management (START, PLAYING, TRANSITION,RESULT)
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
# Member 3:
game_state = "START"
# Member 2 & 3: 等级、分数
level = 1
score = 0
score_multiplier = 1
next_level_ready = False

# Member 2:balancing dificulty难度平衡）
enemy_base_speed = 2.0 #敌人移动的速度
enemy_shoot_delay = 90 #射击间隔，越小shoot速度越快
enemy_health_base = 100 #敌人生命值
enemy_bullet_speed = 7.0 #敌人子弹的速度

MAX_ENEMY_SPEED = 8.0 #敌人速度的limit (避免快到躲不了)
MIN_SHOOT_DELAY = 25 #shooting的间隔下限 （最快每25秒射一次）
MAX_ENEMY_HEALTH = 200 #敌人生命的limit
MAX_ENEMY_BULLET_SPEED = 12.0 #敌人子弹速度的上限

# Member 2: 当前难度值（跟着等级变化）
current_enemy_speed = enemy_base_speed #当前敌人的速度，跟着level加
current_shoot_delay = enemy_shoot_delay #当前射击延迟
current_enemy_health = enemy_health_base #当前敌人生命
current_enemy_bullet_speed = enemy_bullet_speed #当前子弹速度

# Member 3:data for result screen
total_shots = 0
total_hits = 0
total_kills = 0

# ==================== FONTS ====================
# Member 3: UI font
font = pygame.font.Font(None, 42) #normal font ,size 42
small_font = pygame.font.Font(None, 28) #small font, size 28
large_font = pygame.font.Font(None, 64) #big font, size 64

# ==================== LOAD IMAGES ====================
bg_img = pygame.image.load('img/background1/background.png').convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (20, 20))
enemy_bullet_img = pygame.image.load('img/icons/enemy_bullet.png').convert_alpha()
enemy_bullet_img = pygame.transform.scale(enemy_bullet_img, (20, 20))
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
health_box_img = pygame.transform.scale(health_box_img, (35, 35))
item_boxes = {'Health': health_box_img}

# Member 3: start button area
start_btn_rect = pygame.Rect(300, 320, 200, 50) #rect place and size

# Member 3: draw text
def draw_text(text, font, text_col, x, y, center=False):
    img = font.render(text, True, text_col)  #let font become pic
    if center:
        rect = img.get_rect(center=(x, y)) #center
        screen.blit(img, rect) #draw it at middle
    else:
        screen.blit(img, (x, y)) #draw

# ==================== PLAYER CLASS ====================
# Member 1: player movement and shooting
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
                img = pygame.image.load(f'img/player1/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (80, 80))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()

    # Member 1: (WASD)
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

        moving = (keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s])
        self.update_action(1 if moving else 0)

    # Member 1: shooting
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
            self.frame_index = 0 if self.action != 2 else len(self.animation_list[self.action]) - 1

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
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

# ==================== ENEMY CLASS ====================
# Member 2: enemy ai behavior敌人AI行为、动画、难度参数
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.health = current_enemy_health        
        self.direction = 1 #方向 1右边，-1左边
        self.flip = False #是否反转图片
        
        self.animation_list = [] #存所有动画帧
        self.frame_index = 0 #当前播放的帧
        self.action = 0 #当前动作
        self.update_time = pygame.time.get_ticks() #上一次更新动画的时间
        self.shoot_timer = random.randint(0, current_shoot_delay)   #随机射击计时器

        for animation in ['Idle', 'Run', 'Death']:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/enemy1/{animation}')) #读取file里面图片数量
            for i in range(num_of_frames): 
                img = pygame.image.load(f'img/enemy1/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (80, 80)) #缩放到80x80
                temp_list.append(img) #加入列表
            self.animation_list.append(temp_list) #将整个动作序列加入动画列表
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, time_scale): #每帧更新
        self.update_animation()
        self.check_alive() #检查是否死亡
        if not self.alive: #if dead，不再移动/射击
            return
        
        #往玩家方向移动
        dx = player.rect.centerx - self.rect.centerx #水平距离差
        dy = player.rect.centery - self.rect.centery #垂直
        distance = math.hypot(dx, dy) #欧氏距离
        if distance > 0: #避免除以0
            #移动：单位向量x当前敌人速度x时标（慢动作）
            self.rect.x += (dx / distance) * current_enemy_speed * time_scale
            self.rect.y += (dy / distance) * current_enemy_speed * time_scale
        self.flip = dx < 0 #如果复数 玩家在左边，反转照片
        self.update_action(1) #设置为跑步动作（1）         
        
        self.shoot_timer += 1 * time_scale
        if self.shoot_timer >= current_shoot_delay and distance > 0:
            self.shoot_timer = 0
            #create bullet ，方向指向玩家
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery,
                                 dx/distance, dy/distance)
            enemy_bullet_group.add(bullet)

    def update_animation(self):
        ANIMATION_COOLDOWN = 100 
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1 #下一帧
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0 if self.action != 2 else len(self.animation_list[self.action]) - 1

    def update_action(self, new_action): #换动作
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self): #检查生命，if 死亡就加分，增加击杀数，random掉血包
        global score, total_kills
        if self.health <= 0 and self.alive:
            self.alive = False
            self.update_action(2) #切换到死亡动画
            score += 25 #增加分数
            total_kills += 1 #击杀数加一
            # 随机掉落血包
            if random.randint(1,3) == 1: #三分之一的概率掉落血包
                item_box_group.add(ItemBox('Health', self.rect.centerx, self.rect.centery))

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

# ==================== BULLET CLASSES ====================
# Member 1: player bullet
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

# Member 2: 敌人子弹系统enemy bullet
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.speed = current_enemy_bullet_speed   # 难度影响子弹速度
        self.dx = dx #水平方向
        self.dy = dy #垂直方向
        self.image = enemy_bullet_img 
        self.rect = self.image.get_rect(center=(x, y)) #设置初始位置

    def update(self, time_scale):
        self.rect.x += self.dx * self.speed * time_scale #x方向移动
        self.rect.y += self.dy * self.speed * time_scale #y方向移动
        if not self.rect.colliderect(0, 0, WIDTH, HEIGHT): #if子弹超出screen，kill
            self.kill()
        if self.rect.colliderect(player) and player.alive: #如果hit玩家且玩家活着
            player.health -= 15          # 子弹伤害（15）
            self.kill() #子弹消失

# Member 3: colectable item (health)
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        super().__init__()
        self.item_type = item_type 
        self.image = item_boxes[item_type] #load pic
        self.rect = self.image.get_rect(center=(x, y)) #set the place 

    def update(self): #check if player collect it
        if self.rect.colliderect(player) and player.alive:
            if self.item_type == 'Health':
                #add 25 health,not over max health
                player.health = min(player.max_health, player.health + 25)
            self.kill() #gone after collected 

# ==================== HEALTH BAR ====================
# Member 3: UI 血条
class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x #healthbar 左上角x 
        self.y = y #healthbar 左上角y
        self.max_health = max_health 
    def draw(self, health):
        ratio = health / self.max_health #生命值比例
        #draw red background
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        #draw green front
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

# ==================== GROUPS ====================

bullet_group = pygame.sprite.Group()
enemy_bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

# ==================== LEVEL & DIFFICULTY ====================
# Member 2: enemy ai敌人生成、level关卡控制、难度平衡difficulty balancing
def create_enemy(): 
    #在screen外随机生成敌人
    side = random.choice(["top","bottom","left","right"]) #随机选择边缘
    if side == "top": x, y = random.randint(0, WIDTH), -50 #上方外部
    elif side == "bottom": x, y = random.randint(0, WIDTH), HEIGHT + 50 #下方外部
    elif side == "left": x, y = -50, random.randint(0, HEIGHT) #左侧外部
    else: x, y = WIDTH + 50, random.randint(0, HEIGHT) #右侧外部
    enemy_group.add(Enemy(x, y)) #create 敌人并加入组
#开始指定level，清空all敌人，生成当前等级+1个敌人
def start_level(current_level):
    enemy_group.empty() #清空现有敌人
    for _ in range(current_level + 1): #敌人数= 等级+1
        create_enemy()

def next_level():
    #难度平衡：每级增加敌人速度、减少射击延迟、增加生命值和子弹速度
    global level, score_multiplier
    global current_enemy_speed, current_shoot_delay, current_enemy_health, current_enemy_bullet_speed
    level += 1 #等级加一
    #敌人移动速度每level+0.25，不超过上限
    current_enemy_speed = min(current_enemy_speed + 0.25, MAX_ENEMY_SPEED)
    #射击延迟每级-3帧，不低于下限
    current_shoot_delay = max(current_shoot_delay - 3, MIN_SHOOT_DELAY)
    #敌人生命值每级+10，不超过上限
    current_enemy_health = min(current_enemy_health + 10, MAX_ENEMY_HEALTH)
    #敌人子弹速度每级+0.2，不超过上限
    current_enemy_bullet_speed = min(current_enemy_bullet_speed + 0.2, MAX_ENEMY_BULLET_SPEED)
    #得分倍数增加，让后期得分更快
    score_multiplier += 0.15
    #清空所有子弹（必变残留）
    bullet_group.empty()
    enemy_bullet_group.empty()
    start_level(level) #生成新等级的敌人

def reset_game():
    global player, health_bar, level, score, score_multiplier, game_state, next_level_ready
    global total_shots, total_hits, total_kills
    global current_enemy_speed, current_shoot_delay, current_enemy_health, current_enemy_bullet_speed
    bullet_group.empty()
    enemy_bullet_group.empty()
    item_box_group.empty()
    #重新create character
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
# Member 3: result screen and next level screen
def show_result_screen():

    # ===== Accuracy Calculation =====

    # 计算命中率
    hit_rate = (total_hits / total_shots * 100) if total_shots > 0 else 0


    # ===== Rank System =====

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


    # ===== Background Overlay =====

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    overlay.fill((0, 0, 0, 220))

    screen.blit(overlay, (0, 0))


    # ===== Main Result Box =====

    pygame.draw.rect(
        screen,
        (40, 40, 40),
        (170, 70, 460, 460),
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (170, 70, 460, 460),
        3,
        border_radius=15
    )


    # ===== Title =====

    draw_text(
        "GAME OVER",
        large_font,
        RED,
        WIDTH//2,
        120,
        center=True
    )


    # ===== Rank =====

    draw_text(
        f"RANK {rank}",
        large_font,
        rank_color,
        WIDTH//2,
        190,
        center=True
    )


    # ===== Statistics =====

    stats = [

        f"Final Score : {int(score)}",

        f"Level Reached : {level}",

        f"Enemies Killed : {total_kills}",

        f"Shots Fired : {total_shots}",

        f"Shots Hit : {total_hits}",

        f"Accuracy : {hit_rate:.1f}%"
    ]


    # 显示统计资料
    for i, stat in enumerate(stats):

        draw_text(
            stat,
            small_font,
            WHITE,
            WIDTH//2,
            260 + i * 40,
            center=True
        )


    # ===== Restart =====

    draw_text(
        "Press R To Restart",
        small_font,
        GREEN,
        WIDTH//2,
        485,
        center=True
    )


    # ===== Quit =====

    draw_text(
        "Press ESC To Quit",
        small_font,
        GRAY,
        WIDTH//2,
        505,
        center=True
    )
#-----------update level transition--------------------
def show_level_transition():

    # ===== Dark Overlay =====

    # create a dark grey layer
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # black + 220 tranparency
    overlay.fill((0, 0, 0, 220))

    # draw on screen
    screen.blit(overlay, (0, 0))


    # ===== Main Box =====

    # box bg
    pygame.draw.rect(
        screen,
        (40, 40, 40),
        (180, 120, 440, 320),
        border_radius=15
    )

    # white border
    pygame.draw.rect(
        screen,
        WHITE,
        (180, 120, 440, 320),
        3,
        border_radius=15
    )


    # ===== Title =====

    draw_text(
        "LEVEL CLEARED",
        large_font,
        YELLOW,
        WIDTH//2,
        170,
        center=True
    )


    # ===== Current Level =====

    draw_text(
        f"Welcome To Level {level + 1}",
        font,
        WHITE,
        WIDTH//2,
        230,
        center=True
    )


    # ===== Difficulty Changes =====

    draw_text(
        "Difficulty Increased",
        small_font,
        RED,
        WIDTH//2,
        290,
        center=True
    )

    draw_text(
        f"+ Enemy Speed",
        small_font,
        WHITE,
        WIDTH//2,
        330,
        center=True
    )

    draw_text(
        f"+ Enemy Health",
        small_font,
        WHITE,
        WIDTH//2,
        360,
        center=True
    )

    draw_text(
        f"+ Enemy Bullet Speed",
        small_font,
        WHITE,
        WIDTH//2,
        390,
        center=True
    )


    # ===== Continue =====

    draw_text(
        "Press ENTER To Continue",
        small_font,
        GREEN,
        WIDTH//2,
        470,
        center=True
    )

# ==================== INIT ====================
reset_game()
game_state = "START"   # start from main menu

# ==================== MAIN LOOP ====================
while True:
    clock.tick(FPS)
    screen.blit(bg_img, (0,0))

    # -------------------- event --------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # mouse click：start button / shooting in while playing
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "START":
                if start_btn_rect.collidepoint(event.pos):
                    reset_game()
            elif game_state == "PLAYING":
                if player.alive:
                    player.shoot()          # Member 1 shooting

        # keyboard
        if event.type == pygame.KEYDOWN:
            if game_state == "PLAYING" and event.key == pygame.K_f:
                player.shoot()              # Member 1 shoot by press keyboard
            elif game_state == "LEVEL_TRANSITION" and event.key == pygame.K_RETURN:
                next_level()                # Member 2 press enter to next level
                game_state = "PLAYING"
                next_level_ready = False
            elif game_state == "RESULT":
                if event.key == pygame.K_r:
                    reset_game()            # Member 3 restart game
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif game_state == "START" and event.key == pygame.K_RETURN:
                reset_game()

    # -------------------- update --------------------week11
    # Member 3: main menu
    if game_state == "START":

        # ===== Dark Overlay =====
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # ===== Title =====
        draw_text("STILL WORLD", large_font, WHITE, WIDTH//2, 160, center=True)
        #width//2=screen center
        draw_text(
            "Time Moves When You Move",
            small_font,
            YELLOW,
            WIDTH//2,
            210,
            center=True
        )

        # ===== Hover Button =====
        mouse_pos = pygame.mouse.get_pos() #find wheres the mouse

        if start_btn_rect.collidepoint(mouse_pos): #check if cursor is on the rect
            button_color = (180, 180, 180) #cursor on the rect,rect will shiner
            border_color = WHITE
        else:
            button_color = (100, 100, 100)
            border_color = GRAY
        #border_radius=12 to let the corner smooth
        #3 = border thickness
        pygame.draw.rect(screen, button_color, start_btn_rect, border_radius=12)
        pygame.draw.rect(screen, border_color, start_btn_rect, 3, border_radius=12)
        #----------------button text---------------
        draw_text(
            "START GAME",
            small_font,
            BLACK,
            start_btn_rect.centerx,
            start_btn_rect.centery - 10,
            center=True
        )

        # ===== Instructions =====
        draw_text(
            "Click Button or Press ENTER",
            small_font,
            WHITE,
            WIDTH//2,
            420,
            center=True
        )

        draw_text(
            "WASD = Move",
            small_font,
            GREEN,
            WIDTH//2,
            470,
            center=True
        )

        draw_text(
            "Mouse Click / F = Shoot",
            small_font,
            GREEN,
            WIDTH//2,
            500,
            center=True
        )

    # Member 1+2+3: game main loop游戏主循环
    elif game_state == "PLAYING":
        keys = pygame.key.get_pressed()
        time_scale = 1.0 if any(keys[k] for k in (pygame.K_w,pygame.K_s,pygame.K_a,pygame.K_d)) else 0.08

        # 等级过渡检测 (Member 2 & 3)
        if not next_level_ready and score >= level * 100:
            game_state = "LEVEL_TRANSITION"
            next_level_ready = True
            continue

        # Member 1: player movement、update、draw
        if player.alive:
            player.move(keys)
            player.update()
            player.draw()
            health_bar.draw(player.health)

        # Member 2: 敌人更新
        for enemy in enemy_group:
            enemy.update(time_scale)
            enemy.draw()

        # Member 2: 玩家与敌人碰撞（动到enemy会受伤）
        for enemy in list(enemy_group):
            if pygame.sprite.collide_rect(player, enemy) and enemy.alive and player.alive:
                player.health -= 25
                score += 25
                total_kills += 1
                if random.randint(1,3) == 1:
                    item_box_group.add(ItemBox('Health', enemy.rect.centerx, enemy.rect.centery))
                enemy.kill()
                if player.health <= 0:
                    player.alive = False
                    player.update_action(2)
                    game_state = "RESULT"
                break

        # Member 1+2+3: bullet and item update
        bullet_group.update()
        bullet_group.draw(screen)
        enemy_bullet_group.update(time_scale)
        enemy_bullet_group.draw(screen)
        item_box_group.update()
        item_box_group.draw(screen)

        # Member 3: score multiplier
        score += 0.1 * time_scale * score_multiplier

        if not player.alive:
            game_state = "RESULT"

        # Member 3: UI show
        draw_text(f"Score: {int(score)}", small_font, WHITE, 10, 40)
        draw_text(f"Level: {level}", small_font, GREEN, 10, 70)
        draw_text(f"Enemies: {len(enemy_group)}", small_font, WHITE, 10, 100)
        draw_text(f"Shots: {total_shots}  Hits: {total_hits}", small_font, WHITE, 10, 130)

    # Member 3: next level screen
    elif game_state == "LEVEL_TRANSITION":
        # stay，show "press enter"
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
        draw_text(f"Shots: {total_shots}  Hits: {total_hits}", small_font, WHITE, 10, 130)
        show_level_transition()

    # Member 3:game end and go to result screen
    elif game_state == "RESULT":
        show_result_screen()

    pygame.display.update()