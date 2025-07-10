import pygame
import json
import os

# 网格参数
W, H = 800, 600
GRID_SIZE = 20

FONT_PATH = "msyhbd.ttc"

class GameMenu:
    def __init__(self):
        self.options = ["经典模式", "模式选择", "排行榜", "设置", "退出"]
        self.selected = 0
        self.font = pygame.font.Font(FONT_PATH, int(48*0.75))
        self.small_font = pygame.font.Font(FONT_PATH, int(36*0.75))
        
    def draw(self, surface):
        # 菜单背景
        try:
            bg = pygame.image.load('menu_background.png')
            bg = pygame.transform.scale(bg, (W, H))
            surface.blit(bg, (0, 0))
        except Exception as e:
            bg_color = (30, 30, 50)
            surface.fill(bg_color)
        # 标题
        title = self.font.render("贪吃蛇大作战", True, (255, 215, 0))
        try:
            yun_img = pygame.image.load('yun.png')
            # 计算图片尺寸，保证文字完全包裹且不碰边
            margin_w = int(title.get_width() * 0.25)
            margin_h = int(title.get_height() * 0.6)
            yun_width = title.get_width() + 2 * margin_w
            yun_height = title.get_height() + 2 * margin_h
            yun_img = pygame.transform.scale(yun_img, (yun_width, yun_height))
            yun_x = W//2 - yun_width//2
            # 距顶部60像素，且图片底部距离第一个按钮至少30像素
            btn_start_y = 150  # 按钮起始y
            yun_y = max(30, btn_start_y - yun_height - 30)
            surface.blit(yun_img, (yun_x, yun_y))
            # 字体居中叠加在图片上，且保证不碰yun边缘
            title_x = yun_x + margin_w
            title_y = yun_y + margin_h
            surface.blit(title, (title_x, title_y))
        except Exception as e:
            surface.blit(title, (W//2 - title.get_width()//2, 80))
        
        # 菜单选项
        for i, option in enumerate(self.options):
            color = (0, 200, 255) if i == self.selected else (200, 200, 200)
            text = self.font.render(option, True, color)
            # 加载按钮图片
            try:
                if i == self.selected:
                    btn_img = pygame.image.load('bottle_down.png')
                else:
                    btn_img = pygame.image.load('bottle_up.png')
                btn_img = pygame.transform.scale(btn_img, (int((text.get_width()+40)*0.9), int((text.get_height()+20)*0.9)))
                btn_x = W//2 - btn_img.get_width()//2
                btn_y = 150 + i * 80  # 整体往上挪
                surface.blit(btn_img, (btn_x, btn_y))
                text_x = btn_x + (btn_img.get_width() - text.get_width())//2
                text_y = btn_y + (btn_img.get_height() - text.get_height())//2
                surface.blit(text, (text_x, text_y))
            except Exception as e:
                # 加载失败则只显示文字
                surface.blit(text, (W//2 - text.get_width()//2, 150 + i * 80))
        

class ScoreBoard:
    def __init__(self):
        self.scores = self.load_scores()
        self.font = pygame.font.Font(FONT_PATH, 36)
        
    def load_scores(self):
        try:
            with open('scores.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return [{"name": "玩家1", "score": 50},
                    {"name": "玩家2", "score": 40},
                    {"name": "玩家3", "score": 30}]
    
    def save_score(self, name, score):
        self.scores.append({"name": name, "score": score})
        # 按分数降序排序并保留前10名
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]
        try:
            with open('scores.json', 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, ensure_ascii=False, indent=2)
        except:
            print("警告：无法保存排行榜数据")
    
    def draw(self, surface):
        # 菜单背景
        try:
            bg = pygame.image.load('menu_background.png')
            bg = pygame.transform.scale(bg, (W, H))
            surface.blit(bg, (0, 0))
        except Exception as e:
            surface.fill((30, 30, 50))
        title = self.font.render("排行榜", True, (255, 215, 0))
        surface.blit(title, (W//2 - title.get_width()//2, 50))
        
        for i, score in enumerate(self.scores):
            text = f"{i+1}. {score['name']}: {score['score']}"
            score_text = self.font.render(text, True, (200, 200, 255))
            surface.blit(score_text, (W//2 - 100, 120 + i * 40))
        
        back_text = self.font.render("按ESC键返回", True, (150, 150, 150))
        # 按钮样式
        try:
            btn_img = pygame.image.load('bottle_up.png')
            btn_img = pygame.transform.scale(btn_img, (back_text.get_width()+40, back_text.get_height()+20))
            btn_x = W//2 - btn_img.get_width()//2
            btn_y = H - 80
            surface.blit(btn_img, (btn_x, btn_y))
            text_x = btn_x + (btn_img.get_width() - back_text.get_width())//2
            text_y = btn_y + (btn_img.get_height() - back_text.get_height())//2
            surface.blit(back_text, (text_x, text_y))
        except Exception as e:
            surface.blit(back_text, (W//2 - back_text.get_width()//2, H - 80))

class GameConfig:
    def __init__(self):
        self.volume = 0.5
        self.skin = "original"
        self.theme = "default"  # 新增主题字段
        self.load_config()
        
    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.volume = config.get('volume', 0.5)
                skin_val = config.get('skin', 'original')
                if skin_val == 'default':
                    skin_val = 'original'
                self.skin = skin_val
                self.theme = config.get('theme', 'default')
        except:
            self.save_config()
            
    def save_config(self):
        config = {
            'volume': self.volume,
            'skin': self.skin,
            'theme': self.theme
        }
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except:
            print("警告：无法保存配置文件")

class SettingsMenu:
    def __init__(self, config):
        self.config = config
        self.options = ["音量: ", "皮肤: ", "主题: ", "返回"]
        self.selected = 0
        self.font = pygame.font.Font(FONT_PATH, int(48*0.9))
        
    def draw(self, surface):
        try:
            bg = pygame.image.load('menu_background.png')
            bg = pygame.transform.scale(bg, (W, H))
            surface.blit(bg, (0, 0))
        except Exception as e:
            surface.fill((30, 30, 50))
        title = self.font.render("设置", True, (255, 215, 0))
        surface.blit(title, (W//2 - title.get_width()//2, 50))
        skin_map = {"original": "初始", "yellow": "黄阿玛", "vanguard": "先锋战士"}
        for i, option in enumerate(self.options):
            color = (0, 200, 255) if i == self.selected else (200, 200, 200)
            if i == 0:  # 音量
                text = f"{option}{int(self.config.volume * 100)}%"
            elif i == 1:  # 皮肤
                text = f"{option}{skin_map.get(self.config.skin, self.config.skin)}"
            elif i == 2:  # 主题
                theme_map = {"default": "初始", "space": "太空", "forest": "森林"}
                text = f"{option}{theme_map.get(self.config.theme, self.config.theme)}"
            else:
                text = option
            text_surf = self.font.render(text, True, color)
            try:
                if i == self.selected:
                    btn_img = pygame.image.load('bottle_down.png')
                else:
                    btn_img = pygame.image.load('bottle_up.png')
                btn_img = pygame.transform.scale(btn_img, (int((text_surf.get_width()+40)*0.9), int((text_surf.get_height()+20)*0.9)))
                btn_x = W//2 - btn_img.get_width()//2
                btn_y = 150 + i * 80
                surface.blit(btn_img, (btn_x, btn_y))
                text_x = btn_x + (btn_img.get_width() - text_surf.get_width())//2
                text_y = btn_y + (btn_img.get_height() - text_surf.get_height())//2
                surface.blit(text_surf, (text_x, text_y))
            except Exception as e:
                surface.blit(text_surf, (W//2 - text_surf.get_width()//2, 150 + i * 80))
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_LEFT:
                if self.selected == 0:  # 音量
                    self.config.volume = max(0.0, self.config.volume - 0.1)
                elif self.selected == 1:  # 皮肤
                    skins = ["original", "yellow", "vanguard"]
                    current_idx = skins.index(self.config.skin)
                    self.config.skin = skins[(current_idx - 1) % len(skins)]
                elif self.selected == 2:  # 主题
                    themes = ["default", "space", "forest"]
                    current_idx = themes.index(self.config.theme)
                    self.config.theme = themes[(current_idx - 1) % len(themes)]
            elif event.key == pygame.K_RIGHT:
                if self.selected == 0:  # 音量
                    self.config.volume = min(1.0, self.config.volume + 0.1)
                elif self.selected == 1:  # 皮肤
                    skins = ["original", "yellow", "vanguard"]
                    current_idx = skins.index(self.config.skin)
                    self.config.skin = skins[(current_idx + 1) % len(skins)]
                elif self.selected == 2:  # 主题
                    themes = ["default", "space", "forest"]
                    current_idx = themes.index(self.config.theme)
                    self.config.theme = themes[(current_idx + 1) % len(themes)]
            elif event.key == pygame.K_RETURN:
                if self.selected == len(self.options) - 1:  # 返回
                    self.config.save_config()
                    return 'back'
            elif event.key == pygame.K_ESCAPE:
                self.config.save_config()
                return 'back'
        return None


class ModeSelection:
    def __init__(self):
        self.modes = ["简单模式", "中等模式", "困难模式", "挑战模式", "返回"]
        self.selected = 0
        self.font = pygame.font.Font(FONT_PATH, int(48*0.9))
        
    def draw(self, surface):
        try:
            bg = pygame.image.load('menu_background.png')
            bg = pygame.transform.scale(bg, (W, H))
            surface.blit(bg, (0, 0))
        except Exception as e:
            surface.fill((30, 30, 50))
        title = self.font.render("模式选择", True, (255, 215, 0))
        surface.blit(title, (W//2 - title.get_width()//2, 50))
        
        for i, mode in enumerate(self.modes):
            color = (0, 200, 255) if i == self.selected else (200, 200, 200)
            text = self.font.render(mode, True, color)
            # 按钮样式
            try:
                if i == self.selected:
                    btn_img = pygame.image.load('bottle_down.png')
                else:
                    btn_img = pygame.image.load('bottle_up.png')
                btn_img = pygame.transform.scale(btn_img, (int((text.get_width()+40)*0.9), int((text.get_height()+20)*0.9)))
                btn_x = W//2 - btn_img.get_width()//2
                btn_y = 150 + i * 80
                surface.blit(btn_img, (btn_x, btn_y))
                text_x = btn_x + (btn_img.get_width() - text.get_width())//2
                text_y = btn_y + (btn_img.get_height() - text.get_height())//2
                surface.blit(text, (text_x, text_y))
            except Exception as e:
                surface.blit(text, (W//2 - text.get_width()//2, 150 + i * 80)) 