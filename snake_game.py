import random
from dataclasses import dataclass

import pygame


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
    x: int
    y: int


class SnakeGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("consolas", 42, bold=True)
        self.ui_font = pygame.font.SysFont("consolas", 24)
        self.small_font = pygame.font.SysFont("consolas", 18)
        self.reset()

    def reset(self) -> None:
        center = Point(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.snake = [
            center,
            Point(center.x - 1, center.y),
            Point(center.x - 2, center.y),
        ]
        self.direction = Point(1, 0)
        self.next_direction = self.direction
        self.food = self.spawn_food()
        self.score = 0
        self.best_score = getattr(self, "best_score", 0)
        self.state = "start"

    def spawn_food(self) -> Point:
        while True:
            point = Point(
                random.randrange(0, GRID_WIDTH),
                random.randrange(0, GRID_HEIGHT),
            )
            if point not in self.snake:
                return point

    def handle_input(self) -> bool:
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
        if self.state != "running":
            return

        self.direction = self.next_direction
        head = self.snake[0]
        new_head = Point(head.x + self.direction.x, head.y + self.direction.y)

        hit_wall = not (0 <= new_head.x < GRID_WIDTH and 0 <= new_head.y < GRID_HEIGHT)
        hit_self = new_head in self.snake[:-1]
        if hit_wall or hit_self:
            self.state = "game_over"
            self.best_score = max(self.best_score, self.score)
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.best_score = max(self.best_score, self.score)
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw_grid(self) -> None:
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

    def draw_snake(self) -> None:
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
        center = (
            self.food.x * CELL_SIZE + CELL_SIZE // 2,
            self.food.y * CELL_SIZE + CELL_SIZE // 2,
        )
        pygame.draw.circle(self.screen, FOOD_COLOR, center, CELL_SIZE // 2 - 4)

    def draw_hud(self) -> None:
        score_text = self.ui_font.render(f"Score: {self.score}", True, TEXT_COLOR)
        best_text = self.ui_font.render(f"Best: {self.best_score}", True, ACCENT_COLOR)
        self.screen.blit(score_text, (16, 12))
        self.screen.blit(best_text, (WINDOW_WIDTH - best_text.get_width() - 16, 12))

    def draw_overlay(self, title: str, subtitle: str) -> None:
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
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    SnakeGame().run()
