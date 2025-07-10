## 贪吃蛇大作战

## 简介
本项目是一个基于 Python 和 pygame 的多模式贪吃蛇游戏，支持初级（经典）、中等、困难、挑战等玩法，拥有原始皮肤和两个不同颜色的皮肤（借鉴了B站up主肖老师的退休生活的皮肤以及小蛇相关的代码）
、两个游戏主题（可换），适合娱乐和学习。

## 主要特性
- 经典模式、困难模式、挑战模式等多种玩法
- 多种蛇皮肤与主题背景可选
- 排行榜与分数记录
- 支持暂停、特殊食物、陷阱等机制
- 丰富的图片资源和音效（需自行准备，有资源占位）

## 安装与运行
1. **安装依赖**

   本项目依赖 Python 3.7+ 和 pygame。
   该项目使用python 3.10
   ```bash
   pip install pygame
   ```

2. **运行游戏**

   在项目根目录下执行：
   ```bash
   python main.py
   ```

## 目录结构说明
```
├── main.py                # 游戏主入口
├── core/
│   ├── snake.py           # 蛇的基本逻辑与数据结构
│   ├── challenge.py       # 挑战模式与特殊机制
│   └── menu.py            # 菜单、排行榜、设置等界面
├── config.json            # 游戏配置（皮肤、主题、音量）
├── scores.json            # 排行榜分数数据
├── *.png                  # 游戏图片资源
├── *.ttc                  # 字体文件
```

## 配置说明（config.json）               
音量（0~1）
皮肤（original/yellow/vanguard）
主题（default/space/forest）

```json
{
  "volume": 1.0,        
  "skin": "yellow",     
  "theme": "forest"     
}
```

## 分数存储格式（scores.json）
排行榜分数以 JSON 数组形式存储，每项包含玩家名和分数：
```json
[
  { "name": "玩家1", "score": 50 },
  { "name": "玩家2", "score": 40 }
]
```

## 主要玩法说明
- **经典模式**：传统贪吃蛇玩法，支持穿墙或死亡墙壁（困难模式）。
- **挑战模式**：包含特殊食物（加速、减速、加分、护盾）和陷阱，玩法更丰富。
- **排行榜**：记录前10名最高分。
- **设置**：可调整音量、皮肤、主题。

## 资源说明
- 需准备如下图片资源：`snake.png`、`snake2.png`、`food.png`、`wall.png`、`trap.png`、`apple.png`、`bad_apple.png`、`candy.png`、`hamburger.png`、`menu_background.png`、`sad.png`、`bottle_on.png`、`buttle_up.png`、`bottle_down.png`、`forest.png`、`space.png`、`yun.png` 等。
- 字体文件：`msyh.ttc`、`msyhbd.ttc`、`msyhl.ttc`（微软雅黑字体，需自行准备）。

## 操作说明
- 方向键控制移动
- Enter/ESC 进行菜单选择或返回
- 游戏中 ESC 可暂停/退出

致谢
- pygame 官方文档与社区
- 各类开源图片/音效资源

如有问题或建议，欢迎反馈！
如有问题或建议，欢迎反馈！ 
