# Member B 的部分：定义初始时间比例
time_scale = 1.0
# 获取所有按键状态
keys = pygame.key.get_pressed()

# 检查玩家是否有移动输入 (WASD)
if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
    time_scale = 1.0  # 玩家动，时间动
else:
    time_scale = 0.1  # 玩家不动，时间变慢 (Superhot 核心逻辑)

    # 简单的近战敌人逻辑
for enemy in enemies:
    # 1. 计算方向（假设我们要走向玩家 player_pos）
    # 这里用最基础的减法，不要用复杂的向量库，这样更像学生写的
    dx = player_pos[0] - enemy_pos[0]
    dy = player_pos[1] - enemy_pos[1]
    
    # 2. 简单的归一化处理（防止斜向移动过快）
    distance = (dx**2 + dy**2)**0.5
    if distance > 0:
        # 3. 移动速度乘以 time_scale
        # 如果 time_scale 是 0.1，敌人就会慢动作挪动
        enemy_pos[0] += (dx / distance) * enemy_speed * time_scale
        enemy_pos[1] += (dy / distance) * enemy_speed * time_scale

        # 敌人射击冷却计数器
enemy_shoot_timer += 1 * time_scale  # 关键：计时器增加的速度也受时间缩放影响

if enemy_shoot_timer >= 100: # 假设 100 帧射一次
    # 执行射击逻辑...
    enemy_shoot_timer = 0