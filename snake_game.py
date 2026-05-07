import random
from dataclasses import dataclass

import pygame


# 全局常量：把窗口大小、颜色、速度等配置集中放在文件顶部。
# 这样后面想调难度或改外观时，不需要在逻辑代码里到处寻找数字。
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 540
CELL_SIZE = 24
GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE
FPS = 10

BACKGROUND_COLOR = (18, 18, 26)
GRID_COLOR = (30, 30, 42)
SNAKE_HEAD_COLOR = (110, 231, 183)
SNAKE_BODY_COLOR = (52, 211, 153)
FOOD_COLOR = (248, 113, 113)
TEXT_COLOR = (244, 244, 245)
ACCENT_COLOR = (250, 204, 21)

 
@dataclass(frozen=True)
class Point:
    """表示网格上的一个坐标点。

    dataclass 会自动生成 __init__、__eq__ 等方法。
    frozen=True 表示创建后不能修改，更适合当作“值对象”使用。
    """

    x: int
    y: int


class SnakeGame:
    def __init__(self) -> None:
        """初始化 pygame、窗口、字体，并把游戏重置到开始状态。"""

        pygame.init()
        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("consolas", 42, bold=True)
        self.ui_font = pygame.font.SysFont("consolas", 24)
        self.small_font = pygame.font.SysFont("consolas", 18)
        self.reset()

    def reset(self) -> None:
        """重新开始一局游戏。

        注意这里既会被 __init__ 调用，也会在游戏结束后按空格时调用。
        """

        center = Point(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        # snake 是一个列表，列表第 0 个元素永远代表蛇头。
        self.snake = [
            center,
            Point(center.x - 1, center.y),
            Point(center.x - 2, center.y),
        ]
        # direction 是当前移动方向，next_direction 是玩家刚输入的下一个方向。
        # 分开存储可以避免一帧内连续按键导致蛇反向撞到自己。
        self.direction = Point(1, 0)
        self.next_direction = self.direction
        self.food = self.spawn_food()
        self.score = 0
        # getattr(obj, "name", default) 表示：如果属性存在就读取，否则用默认值。
        # 这里保证第一次启动时 best_score 是 0，重开时保留历史最高分。
        self.best_score = getattr(self, "best_score", 0)
        self.state = "start"

    def spawn_food(self) -> Point:
        """随机生成食物坐标，并确保食物不会出现在蛇身上。"""

        while True:
            point = Point(
                random.randrange(0, GRID_WIDTH),
                random.randrange(0, GRID_HEIGHT),
            )
            if point not in self.snake:
                return point

    def handle_input(self) -> bool:
        """处理键盘和窗口事件。

        返回 True 表示游戏继续运行；返回 False 表示退出主循环。
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.state in {"start", "game_over"} and event.key == pygame.K_SPACE:
                    self.reset()
                    self.state = "running"
                elif self.state == "running":
                    if event.key in (pygame.K_UP, pygame.K_w) and self.direction.y != 1:
                        self.next_direction = Point(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and self.direction.y != -1:
                        self.next_direction = Point(0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and self.direction.x != 1:
                        self.next_direction = Point(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.direction.x != -1:
                        self.next_direction = Point(1, 0)
        return True

    def update(self) -> None:
        """更新游戏状态：移动蛇、判断碰撞、处理吃食物。"""

        if self.state != "running":
            return

        self.direction = self.next_direction
        head = self.snake[0]
        new_head = Point(head.x + self.direction.x, head.y + self.direction.y)

        # 撞墙：蛇头坐标超出网格范围。
        hit_wall = not (0 <= new_head.x < GRID_WIDTH and 0 <= new_head.y < GRID_HEIGHT)
        # 撞自己：新蛇头进入了蛇身所在格子。
        # 这里排除最后一节，因为如果本帧没有吃到食物，尾巴会马上移走。
        hit_self = new_head in self.snake[:-1]
        if hit_wall or hit_self:
            self.state = "game_over"
            self.best_score = max(self.best_score, self.score)
            return

        # 先把新蛇头插到列表开头，蛇就“前进”了一格。
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.best_score = max(self.best_score, self.score)
            self.food = self.spawn_food()
        else:
            # 没吃到食物时移除尾巴，蛇身长度保持不变。
            self.snake.pop()

    def draw_grid(self) -> None:
        """绘制背景网格，帮助玩家看清每个 CELL_SIZE 大小的格子。"""

        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

    def draw_snake(self) -> None:
        """绘制蛇头和蛇身。"""

        for index, segment in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_BODY_COLOR
            rect = pygame.Rect(
                segment.x * CELL_SIZE + 2,
                segment.y * CELL_SIZE + 2,
                CELL_SIZE - 4,
                CELL_SIZE - 4,
            )
            pygame.draw.rect(self.screen, color, rect, border_radius=6)

    def draw_food(self) -> None:
        """绘制食物。"""

        center = (
            self.food.x * CELL_SIZE + CELL_SIZE // 2,
            self.food.y * CELL_SIZE + CELL_SIZE // 2,
        )
        pygame.draw.circle(self.screen, FOOD_COLOR, center, CELL_SIZE // 2 - 4)

    def draw_hud(self) -> None:
        """绘制分数和最高分。HUD 是 Head-Up Display 的缩写。"""

        score_text = self.ui_font.render(f"Score: {self.score}", True, TEXT_COLOR)
        best_text = self.ui_font.render(f"Best: {self.best_score}", True, ACCENT_COLOR)
        self.screen.blit(score_text, (16, 12))
        self.screen.blit(best_text, (WINDOW_WIDTH - best_text.get_width() - 16, 12))

    def draw_overlay(self, title: str, subtitle: str) -> None:
        """绘制开始/结束时的半透明提示层。"""

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 8, 12, 170))
        self.screen.blit(overlay, (0, 0))

        title_surface = self.title_font.render(title, True, TEXT_COLOR)
        subtitle_surface = self.ui_font.render(subtitle, True, ACCENT_COLOR)
        hint_surface = self.small_font.render(
            "Use Arrow Keys or WASD to move. Press ESC to quit.",
            True,
            TEXT_COLOR,
        )

        self.screen.blit(
            title_surface,
            (
                (WINDOW_WIDTH - title_surface.get_width()) // 2,
                WINDOW_HEIGHT // 2 - 70,
            ),
        )
        self.screen.blit(
            subtitle_surface,
            (
                (WINDOW_WIDTH - subtitle_surface.get_width()) // 2,
                WINDOW_HEIGHT // 2 - 12,
            ),
        )
        self.screen.blit(
            hint_surface,
            (
                (WINDOW_WIDTH - hint_surface.get_width()) // 2,
                WINDOW_HEIGHT // 2 + 32,
            ),
        )

    def draw(self) -> None:
        """按顺序绘制整帧画面。

        游戏绘制通常是“先清屏，再画背景，再画对象，最后刷新屏幕”。
        """

        self.screen.fill(BACKGROUND_COLOR)
        self.draw_grid()
        self.draw_food()
        self.draw_snake()
        self.draw_hud()

        if self.state == "start":
            self.draw_overlay("Snake", "Press SPACE to start")
        elif self.state == "game_over":
            self.draw_overlay("Game Over", "Press SPACE to play again")

        pygame.display.flip()

    def run(self) -> None:
        """游戏主循环：输入 -> 更新 -> 绘制 -> 控制帧率。"""

        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    # 只有直接运行本文件时才启动游戏。
    # 如果这个文件被其他脚本 import，下面这行不会执行。
    SnakeGame().run()
