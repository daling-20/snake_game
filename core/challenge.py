import random
import pygame
import time
from core.snake import Snake

W, H = 800, 600
GRID_SIZE = 20
GRID_WIDTH = W // GRID_SIZE
GRID_HEIGHT = H // GRID_SIZE

SPECIAL_TYPES = [
    'speed_up',    # apple.png
    'slow_down',   # bad_apple.png
    'add_score',   # candy.png
    'shield',      # hamburger.png
]

SPECIAL_IMAGES = {
    'speed_up': 'apple.png',
    'slow_down': 'bad_apple.png',
    'add_score': 'candy.png',
    'shield': 'hamburger.png',
}

TRAP_IMAGE = 'trap.png'

class ChallengeSnake(Snake):
    def __init__(self, block_size, difficulty="medium"):
        super().__init__(block_size)
        # 初始长度为1，分数为0
        self.blocks = [self.blocks[0]]
        self.body = self.blocks
        self.score = 0
        self.special_foods = []  # [(pos, type)]
        self.traps = self.generate_traps(5)
        self.shield_active = False
        self.shield_expire_time = 0
        self.speed_timer_expire = 0  # 真实时间戳
        self.slow_timer_expire = 0   # 真实时间戳
        self.speed = 5  # 挑战模式初始速度为5
        self.init_speed = self.speed
        self.base_speed = self.init_speed
        self.trap_active = True
        self.last_trap_update = time.time()
        # 特殊食物刷新定时
        self.last_update = {
            'speed_up': time.time(),
            'slow_down': time.time(),
            'add_score': time.time(),
            'shield': time.time()
        }

    def generate_traps(self, n):
        traps = []
        for _ in range(n):
            while True:
                pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
                # 避开最外层墙壁
                if pos[0] == 0 or pos[0] == GRID_WIDTH-1 or pos[1] == 0 or pos[1] == GRID_HEIGHT-1:
                    continue
                if pos not in self.body and pos not in traps:
                    traps.append(pos)
                    break
        return traps

    def get_speed_food_interval(self):
        # 分数每+20，刷新间隔-1秒，最低5秒
        interval = 12 - int(self.score // 20)
        return max(interval, 5)

    def get_other_food_interval(self):
        return 10

    def update_traps(self):
        now = time.time()
        # trap数量随分数增加，每+5分+1，最高50
        trap_count = min(5 + self.score // 5, 50)
        if now - self.last_trap_update >= 8:
            self.traps = self.generate_traps(trap_count)
            self.last_trap_update = now
        # 若数量不足也补足
        elif len(self.traps) < trap_count:
            self.traps += self.generate_traps(trap_count - len(self.traps))

    def update_special_foods(self):
        self.update_traps()
        now = time.time()
        food_types = {ftype: None for ftype in SPECIAL_TYPES}
        for idx, (pos, ftype) in enumerate(self.special_foods):
            food_types[ftype] = idx
        for ftype in ['speed_up', 'slow_down']:
            interval = self.get_speed_food_interval()
            if food_types[ftype] is None or now - self.last_update[ftype] >= interval:
                while True:
                    pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
                    # 禁止出现在墙壁
                    if pos[0] == 0 or pos[0] == GRID_WIDTH-1 or pos[1] == 0 or pos[1] == GRID_HEIGHT-1:
                        continue
                    if pos not in self.body and pos not in [f[0] for f in self.special_foods] and pos not in self.traps:
                        break
                if food_types[ftype] is not None:
                    self.special_foods[food_types[ftype]] = (pos, ftype)
                else:
                    self.special_foods.append((pos, ftype))
                self.last_update[ftype] = now
        for ftype in ['add_score', 'shield']:
            interval = self.get_other_food_interval()
            if food_types[ftype] is None or now - self.last_update[ftype] >= interval:
                while True:
                    pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
                    if pos[0] == 0 or pos[0] == GRID_WIDTH-1 or pos[1] == 0 or pos[1] == GRID_HEIGHT-1:
                        continue
                    if pos not in self.body and pos not in [f[0] for f in self.special_foods] and pos not in self.traps:
                        break
                if food_types[ftype] is not None:
                    self.special_foods[food_types[ftype]] = (pos, ftype)
                else:
                    self.special_foods.append((pos, ftype))
                self.last_update[ftype] = now

    def update_base_speed(self):
        # 分数每+1，基础速度+5%，上限5倍
        self.base_speed = self.init_speed * min(1 + 0.05 * self.score, 5.0)
        # 如果没有加速/减速效果，当前速度也同步
        now = time.time()
        if self.speed_timer_expire == 0 and self.slow_timer_expire == 0:
            self.speed = self.base_speed

    def move(self):
        now = time.time()
        # 处理加速/减速计时（真实时间），可叠加
        if self.speed_timer_expire > 0 and now > self.speed_timer_expire:
            self.speed_timer_expire = 0
        if self.slow_timer_expire > 0 and now > self.slow_timer_expire:
            self.slow_timer_expire = 0
        # 计算当前速度（可叠加）
        speed_factor = 1.0
        if self.speed_timer_expire > now:
            speed_factor *= 1.25
        if self.slow_timer_expire > now:
            speed_factor *= 0.75
        self.speed = self.base_speed * speed_factor
        # 处理护盾过期
        if self.shield_active and now > self.shield_expire_time:
            self.shield_active = False
            self.shield_expire_time = 0
        super().move()

    def check_collision(self):
        head = self.body[0]
        # 撞到自己
        if head in self.body[1:]:
            return True
        return False

    def eat_special_food(self):
        head = self.body[0]
        for idx, (pos, food_type) in enumerate(self.special_foods):
            if head == pos:
                now = time.time()
                if food_type == 'speed_up':
                    self.score += 1
                    self.grow_snake()
                    self.update_base_speed()
                    self.speed_timer_expire = now + 5  # 刷新加速时间
                    if self.score < 0:
                        del self.special_foods[idx]
                        return 'dead'
                elif food_type == 'slow_down':
                    self.score -= 1
                    if len(self.body) > 1:
                        self.body.pop()
                    self.update_base_speed()
                    self.slow_timer_expire = now + 5  # 刷新减速时间
                    if self.score < 0:
                        del self.special_foods[idx]
                        return 'dead'
                elif food_type == 'add_score':
                    self.score += 3
                    tail = self.body[-1]
                    for _ in range(3):
                        self.body.append(type(tail)(tail.x, tail.y))
                    self.update_base_speed()
                elif food_type == 'shield':
                    self.score += 1
                    self.grow_snake()
                    self.shield_active = True
                    self.shield_expire_time = now + 10  # 刷新护盾时间
                    if self.score < 0:
                        del self.special_foods[idx]
                        return 'dead'
                del self.special_foods[idx]
                return food_type
        return None

    def eat_trap(self):
        head = self.body[0]
        if head in self.traps:
            return True
        return False 