import pygame
import random
import sys
import os
from core.snake import Snake
from core.snake import Position
from core.menu import GameMenu, ScoreBoard, GameConfig, SettingsMenu, ModeSelection
from core.challenge import ChallengeSnake, SPECIAL_IMAGES, TRAP_IMAGE
import time
from core.snake import Direction


# 网格参数
W, H = 800, 600
GRID_SIZE = 20
GRID_WIDTH = W // GRID_SIZE
GRID_HEIGHT = H // GRID_SIZE

# 初始化
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("贪吃蛇")
clock = pygame.time.Clock()

# 资源加载（占位）
def load_ai_assets(skin="default"):
    assets = {
        'snake_head': pygame.Surface((GRID_SIZE, GRID_SIZE)),
        'snake_body': pygame.Surface((GRID_SIZE, GRID_SIZE)),
        'food': pygame.Surface((GRID_SIZE, GRID_SIZE))
    }
    
    # 不同皮肤不同颜色
    if skin == "space":
        assets['snake_head'].fill((0, 150, 255))
        assets['snake_body'].fill((0, 100, 200))
    elif skin == "forest":
        assets['snake_head'].fill((50, 200, 50))
        assets['snake_body'].fill((30, 150, 30))
    else:  # default
        assets['snake_head'].fill((0, 255, 0))
        assets['snake_body'].fill((0, 200, 0))
    
    # 加载food.png图片
    try:
        food_image = pygame.image.load('food.png')
        # 将图片缩放到网格大小
        food_image = pygame.transform.scale(food_image, (GRID_SIZE, GRID_SIZE))
        assets['food'] = food_image
    except:
        # 如果加载失败，使用默认的红色方块
        assets['food'].fill((255, 0, 0))
        print("警告：无法加载food.png，使用默认食物图片")
    
    # 音效占位
    sounds = {
        'eat': pygame.mixer.Sound(pygame.sndarray.array([0]*10000)),
        'game_over': pygame.mixer.Sound(pygame.sndarray.array([0]*10000))
    }
    return assets, sounds

def load_challenge_assets():
    # 加载所有特殊食物和陷阱图片
    images = {}
    for key, filename in SPECIAL_IMAGES.items():
        try:
            img = pygame.image.load(filename)
            img = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
            images[key] = img
        except:
            images[key] = pygame.Surface((GRID_SIZE, GRID_SIZE))
            images[key].fill((255, 255, 0))
    # 陷阱
    try:
        trap_img = pygame.image.load(TRAP_IMAGE)
        trap_img = pygame.transform.scale(trap_img, (GRID_SIZE, GRID_SIZE))
        images['trap'] = trap_img
    except:
        images['trap'] = pygame.Surface((GRID_SIZE, GRID_SIZE))
        images['trap'].fill((255, 0, 255))
    return images

def load_theme_bg(theme):
    # print("load_theme_bg被调用，theme=", theme)
    if theme == "space":
        try:
            bg = pygame.image.load("space.png")
            return pygame.transform.scale(bg, (W, H))
        except Exception as e:
            print("加载space.png失败：", e)
    elif theme == "forest":
        try:
            bg = pygame.image.load("forest.png")
            return pygame.transform.scale(bg, (W, H))
        except Exception as e:
            print("加载forest.png失败：", e)
    return None

class Food:
    def __init__(self, snake_body, deadly_wall=False):
        self.position = self.generate_pos(snake_body, deadly_wall)
    def generate_pos(self, snake_body, deadly_wall=False):
        while True:
            if deadly_wall:
                # 不能在最外圈生成
                pos = (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))
            else:
                pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in snake_body:
                return pos

def draw_grid(surface):
    for y in range(0, H, GRID_SIZE):
        for x in range(0, W, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, (40, 40, 40), rect, 1)

def draw_snake(surface, snake, frame):
    total_cells = 9
    cell_width = snake.image.get_width() // total_cells
    cell_height = snake.image.get_height()
    for index, block in enumerate(snake.body):
        x, y = block.x, block.y
        positon = (x * GRID_SIZE, y * GRID_SIZE)
        direction = snake.direction if hasattr(snake, 'direction') and 0 <= snake.direction <= 3 else 0
        if index == 0:
            # 精灵图索引：右0/1，左2/3，上4/5，下6/7
            sprite_idx = direction * 2 + (frame % 2)
            src = (sprite_idx * cell_width, 0, cell_width, cell_height)
        else:
            src = (8 * cell_width, 0, cell_width, cell_height)
        sub_img = snake.image.subsurface(src)
        sub_img = pygame.transform.scale(sub_img, (GRID_SIZE, GRID_SIZE))
        surface.blit(sub_img, positon)

def draw_food(surface, food, assets):
    rect = pygame.Rect(food.position[0] * GRID_SIZE, food.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    surface.blit(assets['food'], rect)

def draw_foods(surface, foods, assets):
    for pos in foods:
        rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        surface.blit(assets['food'], rect)

def draw_obstacles(surface, obstacles):
    for pos in obstacles:
        rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, (100, 100, 100), rect)

def draw_special_foods(surface, special_foods, images):
    for pos, food_type in special_foods:
        rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        surface.blit(images.get(food_type), rect)

def draw_traps(surface, traps, images):
    for pos in traps:
        rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        surface.blit(images.get('trap'), rect)

FONT_PATH = "msyhbd.ttc"

def draw_score(surface, score):
    font = pygame.font.Font(FONT_PATH, 36)
    text = font.render(f"得分: {score}", True, (255, 255, 255))
    surface.blit(text, (10, 10))

def get_snake_image(skin):
    if skin == "yellow":
        return pygame.image.load("snake.png")
    elif skin == "vanguard":
        return pygame.image.load("snake2.png")
    else:
        return None  # original皮肤用Snake类默认图片


class GameOverScreen:
    def __init__(self, score):
        self.score = score
        self.options = ["返回主菜单"]
        self.selected = 0
        self.font = pygame.font.Font(FONT_PATH, 64)
        self.small_font = pygame.font.Font(FONT_PATH, 36)
    def draw(self, surface):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        text = self.font.render("游戏结束", True, (255, 80, 80))
        surface.blit(text, (W//2 - text.get_width()//2, H//3))
        score_text = self.small_font.render(f"得分: {self.score}", True, (255, 255, 255))
        surface.blit(score_text, (W//2 - score_text.get_width()//2, H//3 + 80))
        # 按钮样式
        for i, option in enumerate(self.options):
            color = (0, 200, 255) if i == self.selected else (200, 200, 200)
            text = self.small_font.render(option, True, color)
            try:
                if i == self.selected:
                    btn_img = pygame.image.load('bottle_on.png')
                else:
                    btn_img = pygame.image.load('buttle_up.png')
                btn_img = pygame.transform.scale(btn_img, (int((text.get_width()+40)*0.9), int((text.get_height()+20)*0.9)))
                btn_x = W//2 - btn_img.get_width()//2
                btn_y = H//3 + 160 + i * 90
                surface.blit(btn_img, (btn_x, btn_y))
                text_x = btn_x + (btn_img.get_width() - text.get_width())//2
                text_y = btn_y + (btn_img.get_height() - text.get_height())//2
                surface.blit(text, (text_x, text_y))
            except Exception as e:
                surface.blit(text, (W//2 - text.get_width()//2, H//3 + 160 + i * 90))
        tip = self.small_font.render("按Enter或ESC返回主菜单", True, (200, 200, 200))
        surface.blit(tip, (W//2 - tip.get_width()//2, H//3 + 160 + 90))


def classic_game_loop(snake, config, score_board, speed_scale=1.0, deadly_wall=False, wall_img=None):
    assets, sounds = load_ai_assets(config.skin)
    # 设置皮肤图片
    img = get_snake_image(config.skin)
    if img is not None:
        img = pygame.transform.scale(img, (snake.block_size * 9, snake.block_size))
        snake.image = img
    food = Food(snake.body, deadly_wall=deadly_wall)
    running = True
    key_to_direction = {
        pygame.K_RIGHT: Direction.right,
        pygame.K_LEFT: Direction.left,
        pygame.K_UP: Direction.up,
        pygame.K_DOWN: Direction.down
    }
    pause_menu = PauseMenu()
    pause = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in key_to_direction:
                    snake.change_direction(key_to_direction[event.key])
                if event.key == pygame.K_ESCAPE:
                    pause = not pause
                    if pause:
                        pygame.mixer.pause()
                    else:
                        pygame.mixer.unpause()
        if pause:
            pause_menu.draw(screen)
            pygame.display.flip()
            clock.tick(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        pause_menu.selected = (pause_menu.selected - 1) % len(pause_menu.options)
                    elif event.key == pygame.K_DOWN:
                        pause_menu.selected = (pause_menu.selected + 1) % len(pause_menu.options)
                    elif event.key == pygame.K_RETURN:
                        if pause_menu.selected == 0:  # 继续
                            pause = False
                            pygame.mixer.unpause()
                        elif pause_menu.selected == 1:  # 退出
                            return  # 直接退出game_loop，回到主菜单
            continue
        keys = pygame.key.get_pressed()
        if any(keys[key] for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]):
            snake.current_speed = snake.speed * speed_scale * 1.5
        else:
            snake.current_speed = snake.speed * speed_scale
        # 吃食物
        head = snake.body[0]
        if head == food.position:
            snake.grow = True
            snake.score += 1
            food = Food(snake.body, deadly_wall=deadly_wall)
        snake.move()
        # 困难模式判定墙壁死亡
        if deadly_wall:
            x, y = snake.body[0].x, snake.body[0].y
            if x == 0 or x == GRID_WIDTH-1 or y == 0 or y == GRID_HEIGHT-1:
                score_board.save_score("Player", snake.score)
                return snake.score
        if snake.check_collision():
            score_board.save_score("Player", snake.score)
            return snake.score
        # 渲染顺序修正：先背景，再其它
        bg_img = load_theme_bg(config.theme)
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill((0, 0, 0))
        draw_grid(screen)
        if deadly_wall and wall_img is not None:
            for i in range(GRID_WIDTH):
                screen.blit(wall_img, (i*GRID_SIZE, 0))
                screen.blit(wall_img, (i*GRID_SIZE, (GRID_HEIGHT-1)*GRID_SIZE))
            for j in range(GRID_HEIGHT):
                screen.blit(wall_img, (0, j*GRID_SIZE))
                screen.blit(wall_img, ((GRID_WIDTH-1)*GRID_SIZE, j*GRID_SIZE))
        frame = (pygame.time.get_ticks() // 200) % 2
        draw_snake(screen, snake, frame)
        draw_food(screen, food, assets)
        draw_score(screen, snake.score)
        font = pygame.font.Font(FONT_PATH, 24)
        mode_text = font.render(f"模式: classic", True, (200, 200, 200))
        screen.blit(mode_text, (W - 150, 10))
        pygame.display.flip()
        clock.tick(snake.current_speed)

def challenge_game_loop(snake, config, score_board, challenge_images, wall_img=None):
    assets, sounds = load_ai_assets(config.skin)
    img = get_snake_image(config.skin)
    if img is not None:
        img = pygame.transform.scale(img, (snake.block_size * 9, snake.block_size))
        snake.image = img
    foods = []
    last_food_change_time = time.time()
    # 初始参数
    food_min = 1
    food_max = 80
    for _ in range(3):
        while True:
            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if pos[0] == 0 or pos[0] == GRID_WIDTH-1 or pos[1] == 0 or pos[1] == GRID_HEIGHT-1:
                continue
            if pos not in snake.body and pos not in [f[0] for f in snake.special_foods] and pos not in snake.traps and pos not in foods:
                foods.append(pos)
                break
    running = True
    move_interval = 1.0 / snake.speed  # 蛇每秒移动speed次
    last_move_time = time.time()
    key_to_direction = {
        pygame.K_RIGHT: Direction.right,
        pygame.K_LEFT: Direction.left,
        pygame.K_UP: Direction.up,
        pygame.K_DOWN: Direction.down
    }
    pause_menu = PauseMenu()
    pause = False
    special_sound_start_time = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in key_to_direction:
                    snake.change_direction(key_to_direction[event.key])
                if event.key == pygame.K_ESCAPE:
                    pause = not pause
                    if pause:
                        pygame.mixer.pause()
                    else:
                        pygame.mixer.unpause()
        if pause:
            pause_menu.draw(screen)
            pygame.display.flip()
            clock.tick(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        pause_menu.selected = (pause_menu.selected - 1) % len(pause_menu.options)
                    elif event.key == pygame.K_DOWN:
                        pause_menu.selected = (pause_menu.selected + 1) % len(pause_menu.options)
                    elif event.key == pygame.K_RETURN:
                        if pause_menu.selected == 0:  # 继续
                            pause = False
                            pygame.mixer.unpause()
                        elif pause_menu.selected == 1:  # 退出
                            return  # 直接退出game_loop，回到主菜单
            continue
        keys = pygame.key.get_pressed()
        if any(keys[key] for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]):
            snake.current_speed = snake.speed * 1.5
        else:
            snake.current_speed = snake.speed
        # 根据得分动态调整食物变化机制
        score = snake.score
        if score <= 10:
            food_change_interval = 15
            delta_min, delta_max = 1, 3
        elif 10 < score < 30:
            food_change_interval = 10
            delta_min, delta_max = 3, 5
        else:
            food_change_interval = 5
            delta_min, delta_max = 5, 10
        now = time.time()
        if now - last_food_change_time >= food_change_interval:
            delta = random.randint(delta_min, delta_max)
            if random.choice([True, False]):
                for _ in range(delta):
                    if len(foods) < food_max:
                        for _ in range(100):
                            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
                            if pos[0] == 0 or pos[0] == GRID_WIDTH-1 or pos[1] == 0 or pos[1] == GRID_HEIGHT-1:
                                continue
                            if pos not in snake.body and pos not in [f[0] for f in snake.special_foods] and pos not in snake.traps and pos not in foods:
                                foods.append(pos)
                                break
            else:
                for _ in range(delta):
                    if len(foods) > food_min:
                        foods.pop(random.randrange(len(foods)))
            last_food_change_time = now
        if now - last_move_time >= 1.0 / snake.current_speed:
            head = snake.body[0]
            # 普通食物吃食判定（提前）
            if head in foods:
                snake.grow = True
                snake.score += 1
                foods.remove(head)
                if snake.score < 0:
                    score_board.save_score("Player", snake.score)
                    if special_sound_start_time is not None and time.time() - special_sound_start_time >= 0.5:
                        # PIXEL_FEAST_SOUND.stop() # 删除特殊音效
                        pass
                    return snake.score
            # 特殊食物吃食判定（提前，设置grow）
            for idx, (pos, food_type) in enumerate(list(snake.special_foods)):
                if head == pos:
                    # 播放特殊音效（使用独立通道，避免被覆盖）
                    # if PIXEL_FEAST_SOUND: # 删除特殊音效
                    #     channel = pygame.mixer.find_channel()
                    #     if channel:
                    #         channel.set_volume(config.volume)
                    #         channel.play(PIXEL_FEAST_SOUND)
                    #     else:
                    #         PIXEL_FEAST_SOUND.set_volume(config.volume)
                    #         PIXEL_FEAST_SOUND.play()
                    # special_sound_start_time = time.time() # 删除特殊音效
                    result = snake.eat_special_food()
                    if result == 'dead':
                        score_board.save_score("Player", snake.score)
                        return snake.score
                    break
            snake._last_body = list(snake.body)
            snake.move()
            snake.update_special_foods()
            # 吃特殊食物后重新获取蛇头位置
            head = snake.body[0]
            x, y = head.x, head.y
            on_wall = (x == 0 or x == GRID_WIDTH-1 or y == 0 or y == GRID_HEIGHT-1)
            if not hasattr(snake, 'wall_protect_timer'):
                snake.wall_protect_timer = 0
            if on_wall:
                if snake.shield_active:
                    if snake.wall_protect_timer == 0:
                        snake.wall_protect_timer = time.time()
                    elif time.time() - snake.wall_protect_timer > 1:
                        snake.shield_active = False
                        snake.shield_expire_time = 0
                        score_board.save_score("Player", snake.score)
                        return snake.score
                    # 蛇头保持原地不动（回退本次move）
                    if hasattr(snake, '_last_body'):
                        snake.body = list(snake._last_body)
                else:
                    score_board.save_score("Player", snake.score)
                    return snake.score
            else:
                if hasattr(snake, 'wall_protect_timer') and snake.wall_protect_timer != 0:
                    # 离开墙壁，护盾消失
                    snake.shield_active = False
                    snake.shield_expire_time = 0
                    snake.wall_protect_timer = 0
                else:
                    snake.wall_protect_timer = 0
            if snake.eat_trap():
                if snake.shield_active:
                    snake.traps.remove(snake.body[0])
                    snake.shield_active = False
                    snake.shield_expire_time = 0
                else:
                    score_board.save_score("Player", snake.score)
                    return snake.score
            if snake.check_collision():
                score_board.save_score("Player", snake.score)
                return snake.score
            last_move_time = now
        # 渲染顺序修正：先背景，再其它
        bg_img = load_theme_bg(config.theme)
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill((0, 0, 0))
        draw_grid(screen)
        if wall_img is not None:
            for i in range(GRID_WIDTH):
                screen.blit(wall_img, (i*GRID_SIZE, 0))
                screen.blit(wall_img, (i*GRID_SIZE, (GRID_HEIGHT-1)*GRID_SIZE))
            for j in range(GRID_HEIGHT):
                screen.blit(wall_img, (0, j*GRID_SIZE))
                screen.blit(wall_img, ((GRID_WIDTH-1)*GRID_SIZE, j*GRID_SIZE))
        draw_traps(screen, snake.traps, challenge_images)
        frame = (pygame.time.get_ticks() // 200) % 2
        draw_snake(screen, snake, frame)
        draw_foods(screen, foods, assets)
        draw_special_foods(screen, snake.special_foods, challenge_images)
        draw_score(screen, snake.score)
        font = pygame.font.Font(FONT_PATH, 24)
        if snake.shield_active:
            shield_sec = int(snake.shield_expire_time - time.time() + 0.999)
            if shield_sec < 0:
                shield_sec = 0
            shield_text = font.render(f"护盾: {shield_sec}s", True, (0, 255, 255))
        else:
            shield_text = font.render(f"护盾: 无", True, (100, 100, 100))
        screen.blit(shield_text, (W - 150, 40))
        mode_text = font.render(f"模式: challenge", True, (200, 200, 200))
        screen.blit(mode_text, (W - 150, 10))
        pygame.display.flip()
        clock.tick(30)


class PauseMenu:
    def __init__(self):
        self.options = ["继续", "退出"]
        self.selected = 0
        self.font = pygame.font.Font(FONT_PATH, int(48*0.9))
    def draw(self, surface):
        # 用sad.png作为背景
        try:
            sad_bg = pygame.image.load('sad.png')
            sad_bg = pygame.transform.scale(sad_bg, (W, H))
            surface.blit(sad_bg, (0, 0))
        except Exception as e:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
        # 半透明遮罩
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))
        # 居中显示按钮
        for i, option in enumerate(self.options):
            color = (0, 200, 255) if i == self.selected else (200, 200, 200)
            text = self.font.render(option, True, color)
            try:
                if i == self.selected:
                    btn_img = pygame.image.load('bottle_on.png')
                else:
                    btn_img = pygame.image.load('buttle_up.png')
                btn_img = pygame.transform.scale(btn_img, (int((text.get_width()+40)*0.9), int((text.get_height()+20)*0.9)))
                btn_x = W//2 - btn_img.get_width()//2
                btn_y = H//2 - 60 + i * 90
                surface.blit(btn_img, (btn_x, btn_y))
                text_x = btn_x + (btn_img.get_width() - text.get_width())//2
                text_y = btn_y + (btn_img.get_height() - text.get_height())//2
                surface.blit(text, (text_x, text_y))
            except Exception as e:
                surface.blit(text, (W//2 - text.get_width()//2, H//2 - 60 + i * 90))


# 全局音乐与音效变量
# PIXEL_FEAST_SOUND = None # 删除特殊音效
# GAME_OVER_MUSIC = None # 删除背景音乐
# MENU_MUSIC = None # 删除背景音乐

def main():
    # global PIXEL_FEAST_SOUND, GAME_OVER_MUSIC, MENU_MUSIC # 删除特殊音效和背景音乐
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("贪吃蛇大作战")
    clock = pygame.time.Clock()
    
    # 初始化菜单和配置
    menu = GameMenu()
    score_board = ScoreBoard()
    config = GameConfig()
    settings_menu = SettingsMenu(config)
    mode_selection = ModeSelection()
    
    # 游戏状态
    game_state = "menu"  # menu, game, scores, settings, mode_selection, game_over
    snake = None
    food = None
    game_mode = "classic"  # classic, challenge
    
    challenge_images = load_challenge_assets()
    
    foods = []
    last_food_change_time = time.time()
    food_change_interval = 15  # 秒
    food_min = 1
    food_max = 80
    
    # 预加载墙壁图片
    try:
        wall_img = pygame.image.load('wall.png')
        wall_img = pygame.transform.scale(wall_img, (GRID_SIZE, GRID_SIZE))
    except:
        wall_img = pygame.Surface((GRID_SIZE, GRID_SIZE))
        wall_img.fill((180, 180, 180))
    
    # 1. 在资源加载处加载snake.png
    snake_head_img = pygame.image.load('snake.png')
    snake_head_img = pygame.transform.scale(snake_head_img, (GRID_SIZE, GRID_SIZE))
    assets = {
        'snake_head': snake_head_img,
        'snake_body': snake_head_img,  # 可替换为其它身体图片
        'food': pygame.Surface((GRID_SIZE, GRID_SIZE))
    }
    
    # 不同皮肤不同颜色
    if config.skin == "space":
        assets['snake_head'].fill((0, 150, 255))
        assets['snake_body'].fill((0, 100, 200))
    elif config.skin == "forest":
        assets['snake_head'].fill((50, 200, 50))
        assets['snake_body'].fill((30, 150, 30))
    else:  # default
        assets['snake_head'].fill((0, 255, 0))
        assets['snake_body'].fill((0, 200, 0))
    
    # 加载food.png图片
    try:
        food_image = pygame.image.load('food.png')
        # 将图片缩放到网格大小
        food_image = pygame.transform.scale(food_image, (GRID_SIZE, GRID_SIZE))
        assets['food'] = food_image
    except:
        # 如果加载失败，使用默认的红色方块
        assets['food'].fill((255, 0, 0))
        print("警告：无法加载food.png，使用默认食物图片")
    
    # 音效占位
    sounds = {
        'eat': pygame.mixer.Sound(pygame.sndarray.array([0]*10000)),
        'game_over': pygame.mixer.Sound(pygame.sndarray.array([0]*10000))
    }

    game_over_screen = None
    game_over_music_played = False

    # 加载音效和音乐
    # try: # 删除背景音乐
    #     PIXEL_FEAST_SOUND = pygame.mixer.Sound('Pixel Feast.wav')
    # except Exception as e:
    #     print('警告：无法加载Pixel Feast.wav', e)
    # try:
    #     GAME_OVER_MUSIC = '贪吃蛇的遗憾.wav'
    # except Exception as e:
    #     print('警告：无法加载贪吃蛇的遗憾.wav', e)
    # try:
    #     MENU_MUSIC = '柔软的云.wav'
    # except Exception as e:
    #     print('警告：无法加载柔软的云.wav', e)

    menu_music_played = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if game_state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        menu.selected = (menu.selected + 1) % len(menu.options)
                    elif event.key == pygame.K_UP:
                        menu.selected = (menu.selected - 1) % len(menu.options)
                    elif event.key == pygame.K_RETURN:
                        if menu.selected == 0:  # 经典模式
                            if menu_music_played:
                                # pygame.mixer.music.stop() # 删除背景音乐
                                menu_music_played = False
                            game_mode = "classic"
                            snake = Snake(GRID_SIZE, config.skin)
                            classic_game_loop(snake, config, score_board)
                            game_state = "menu"
                        elif menu.selected == 1:  # 模式选择
                            game_state = "mode_selection"
                        elif menu.selected == 2:  # 排行榜
                            game_state = "scores"
                        elif menu.selected == 3:  # 设置
                            game_state = "settings"
                        elif menu.selected == 4:  # 退出
                            pygame.quit()
                            sys.exit()
            
            elif game_state == "mode_selection":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        mode_selection.selected = (mode_selection.selected + 1) % len(mode_selection.modes)
                    elif event.key == pygame.K_UP:
                        mode_selection.selected = (mode_selection.selected - 1) % len(mode_selection.modes)
                    elif event.key == pygame.K_RETURN:
                        if mode_selection.selected == 0:  # 简单模式
                            if menu_music_played:
                                # pygame.mixer.music.stop() # 删除背景音乐
                                menu_music_played = False
                            game_mode = "classic"
                            snake = Snake(GRID_SIZE, config.skin)
                            classic_game_loop(snake, config, score_board)
                            game_state = "menu"
                        elif mode_selection.selected == 1:  # 中等模式
                            if menu_music_played:
                                # pygame.mixer.music.stop() # 删除背景音乐
                                menu_music_played = False
                            game_mode = "classic"
                            snake = Snake(GRID_SIZE, config.skin)
                            classic_game_loop(snake, config, score_board, speed_scale=1.5)
                            game_state = "menu"
                        elif mode_selection.selected == 2:  # 困难模式
                            if menu_music_played:
                                # pygame.mixer.music.stop() # 删除背景音乐
                                menu_music_played = False
                            game_mode = "classic"
                            snake = Snake(GRID_SIZE, config.skin)
                            score = classic_game_loop(snake, config, score_board, speed_scale=1.5, deadly_wall=True, wall_img=wall_img)
                            game_over_screen = GameOverScreen(score if score is not None else 0)
                            game_state = "game_over"
                        elif mode_selection.selected == 3:  # 挑战模式
                            if menu_music_played:
                                # pygame.mixer.music.stop() # 删除背景音乐
                                menu_music_played = False
                            game_mode = "challenge"
                            snake = ChallengeSnake(GRID_SIZE, config.skin)
                            score = challenge_game_loop(snake, config, score_board, challenge_images, wall_img=wall_img)
                            game_over_screen = GameOverScreen(score if score is not None else 0)
                            game_state = "game_over"
                        elif mode_selection.selected == 4:  # 返回
                            game_state = "menu"
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "menu"
            
            elif game_state == "scores":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = "menu"
            
            elif game_state == "settings":
                result = settings_menu.handle_event(event)
                if result == 'back':
                    game_state = "menu"
            
            elif game_state == "game":
                key_to_direction = {
                    pygame.K_RIGHT: Direction.right,
                    pygame.K_LEFT: Direction.left,
                    pygame.K_UP: Direction.up,
                    pygame.K_DOWN: Direction.down
                }
                if event.type == pygame.KEYDOWN:
                    if event.key in key_to_direction:
                        snake.change_direction(key_to_direction[event.key])
                    if event.key == pygame.K_ESCAPE:
                        game_state = "menu"
        
        # 绘制当前状态
        if game_state == "menu":
            # 一级目录背景音乐
            # if MENU_MUSIC and not menu_music_played: # 删除背景音乐
            #     pygame.mixer.music.load(MENU_MUSIC)
            #     pygame.mixer.music.play(-1, start=40.0)
            #     pygame.mixer.music.set_volume(config.volume)
            #     menu_music_played = True
            # 检查是否需要停止其它音乐
            if game_over_music_played:
                # pygame.mixer.music.stop() # 删除背景音乐
                game_over_music_played = False
            menu.draw(screen)
        elif game_state == "scores":
            # 二级目录背景音乐
            # if MENU_MUSIC and not menu_music_played: # 删除背景音乐
            #     pygame.mixer.music.load(MENU_MUSIC)
            #     pygame.mixer.music.play(-1, start=40.0)
            #     pygame.mixer.music.set_volume(config.volume)
            #     menu_music_played = True
            if game_over_music_played:
                # pygame.mixer.music.stop() # 删除背景音乐
                game_over_music_played = False
            score_board.draw(screen)
        elif game_state == "settings":
            # if MENU_MUSIC and not menu_music_played: # 删除背景音乐
            #     pygame.mixer.music.load(MENU_MUSIC)
            #     pygame.mixer.music.play(-1, start=40.0)
            #     pygame.mixer.music.set_volume(config.volume)
            #     menu_music_played = True
            if game_over_music_played:
                # pygame.mixer.music.stop() # 删除背景音乐
                game_over_music_played = False
            settings_menu.draw(screen)
        elif game_state == "mode_selection":
            # if MENU_MUSIC and not menu_music_played: # 删除背景音乐
            #     pygame.mixer.music.load(MENU_MUSIC)
            #     pygame.mixer.music.play(-1, start=40.0)
            #     pygame.mixer.music.set_volume(config.volume)
            #     menu_music_played = True
            if game_over_music_played:
                # pygame.mixer.music.stop() # 删除背景音乐
                game_over_music_played = False
            mode_selection.draw(screen)
        elif game_state == "game_over":
            # if menu_music_played: # 删除背景音乐
            #     pygame.mixer.music.stop()
            #     menu_music_played = False
            if game_over_screen:
                # 只在进入game_over时播放一次音乐
                # if GAME_OVER_MUSIC and not game_over_music_played: # 删除背景音乐
                #     pygame.mixer.music.load(GAME_OVER_MUSIC)
                #     pygame.mixer.music.play(-1)
                #     pygame.mixer.music.set_volume(config.volume)
                #     game_over_music_played = True
                game_over_screen.draw(screen)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        game_over_screen.selected = (game_over_screen.selected - 1) % len(game_over_screen.options)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        game_over_screen.selected = (game_over_screen.selected + 1) % len(game_over_screen.options)
                    elif event.key == pygame.K_RETURN:
                        if game_over_screen.selected == 0:
                            game_state = "menu"
                            game_over_screen = None
                            game_over_music_played = False
                            # 停止游戏结束音乐
                            # pygame.mixer.music.stop() # 删除背景音乐
                            break
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "menu"
                        game_over_screen = None
                        game_over_music_played = False
                        # 停止游戏结束音乐
                        # pygame.mixer.music.stop() # 删除背景音乐
                        break
        elif game_state == "game":
            # if menu_music_played: # 删除背景音乐
            #     pygame.mixer.music.stop()
            #     menu_music_played = False
            # 设置背景音乐音量（防止残留）
            # pygame.mixer.music.set_volume(config.volume) # 删除背景音乐
            # 游戏逻辑和绘制
            keys = pygame.key.get_pressed()
            if any(keys[key] for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]):
                snake.current_speed = snake.speed * 1.5
            else:
                snake.current_speed = snake.speed
            # 判断当前是否为困难模式
            is_deadly_wall = False
            if game_mode == "classic" and hasattr(snake, 'current_direction') and hasattr(snake, 'block_size'):
                # 通过 classic_game_loop 传递 deadly_wall
                # 这里只能通过 config 或 game_mode 判断，暂时用下面的方式
                # 但实际上主循环的 "game" 状态并未用 deadly_wall
                is_deadly_wall = False  # 你可以根据需要调整
            # 初始化foods
            if not foods:
                foods = []
                for _ in range(3):
                    while True:
                        if is_deadly_wall:
                            pos = (random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2))
                        else:
                            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
                        if pos[0] == 0 or pos[0] == GRID_WIDTH-1 or pos[1] == 0 or pos[1] == GRID_HEIGHT-1:
                            if is_deadly_wall:
                                continue
                        if pos not in snake.body and (not hasattr(snake, 'special_foods') or pos not in [f[0] for f in getattr(snake, 'special_foods', [])]) and (not hasattr(snake, 'traps') or pos not in getattr(snake, 'traps', [])) and pos not in foods:
                            foods.append(pos)
                            break
                last_food_change_time = time.time()
            # 每15秒动态调整食物数量
            now = time.time()
            if now - last_food_change_time >= food_change_interval:
                delta = random.randint(1, 3)
                if random.choice([True, False]):
                    # 增加
                    for _ in range(delta):
                        if len(foods) < food_max:
                            for _ in range(100):
                                if is_deadly_wall:
                                    pos = (random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2))
                                else:
                                    pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
                                if pos[0] == 0 or pos[0] == GRID_WIDTH-1 or pos[1] == 0 or pos[1] == GRID_HEIGHT-1:
                                    if is_deadly_wall:
                                        continue
                                if pos not in snake.body and (not hasattr(snake, 'special_foods') or pos not in [f[0] for f in getattr(snake, 'special_foods', [])]) and (not hasattr(snake, 'traps') or pos not in getattr(snake, 'traps', [])) and pos not in foods:
                                    foods.append(pos)
                                    break
                else:
                    # 减少
                    for _ in range(delta):
                        if len(foods) > food_min:
                            foods.pop(random.randrange(len(foods)))
                last_food_change_time = now
            # 判定吃普通食物
            head = snake.body[0]
            if head in foods:
                snake.grow = True
                snake.score += 1
                foods.remove(head)
                if snake.score < 0:
                    score_board.save_score("Player", snake.score)
                    game_state = "menu"
                    continue
            # 判定陷阱
            if snake.eat_trap():
                if snake.shield_active:
                    snake.traps.remove(snake.body[0])
                    snake.shield_active = False
                    snake.shield_expire_time = 0
                else:
                    score_board.save_score("Player", snake.score)
                    game_state = "menu"
                    continue
            # 渲染
            assets, sounds = load_ai_assets(config.skin) # 重新加载assets和sounds
            bg_img = load_theme_bg(config.theme)
            if bg_img:
                screen.blit(bg_img, (0, 0))
            else:
                screen.fill((0, 0, 0))
            draw_grid(screen)
            if hasattr(snake, 'traps'):
                draw_traps(screen, snake.traps, challenge_images)
            draw_snake(screen, snake, 0) # 经典模式不使用frame动画
            draw_foods(screen, foods, assets)
            if hasattr(snake, 'special_foods'):
                draw_special_foods(screen, snake.special_foods, challenge_images)
            draw_score(screen, snake.score)
            # 显示护盾剩余时间
            font = pygame.font.Font(FONT_PATH, 24)
            if snake.shield_active:
                shield_sec = int(snake.shield_expire_time - time.time() + 0.999)
                if shield_sec < 0:
                    shield_sec = 0
                shield_text = font.render(f"护盾: {shield_sec}s", True, (0, 255, 255))
            else:
                shield_text = font.render(f"护盾: 无", True, (100, 100, 100))
            screen.blit(shield_text, (W - 150, 40))
            # 显示游戏模式
            mode_text = font.render(f"模式: {game_mode}", True, (200, 200, 200))
            screen.blit(mode_text, (W - 150, 10))
        
        pygame.display.flip()
        clock.tick(60 if game_state != "game" else snake.current_speed if snake else 60)

if __name__ == "__main__":
    main() 