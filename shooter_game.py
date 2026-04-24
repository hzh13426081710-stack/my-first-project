import math
import random
from dataclasses import dataclass

import pygame


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

BACKGROUND_COLOR = (9, 12, 20)
GRID_COLOR = (24, 31, 46)
PLAYER_COLOR = (83, 217, 164)
PLAYER_HIT_COLOR = (253, 224, 71)
BULLET_COLOR = (248, 250, 252)
ENEMY_COLOR = (248, 113, 113)
ENEMY_FAST_COLOR = (251, 146, 60)
TEXT_COLOR = (241, 245, 249)
MUTED_TEXT_COLOR = (148, 163, 184)
ACCENT_COLOR = (96, 165, 250)
PANEL_COLOR = (12, 18, 30, 210)

PLAYER_RADIUS = 18
PLAYER_SPEED = 320
PLAYER_MAX_LIVES = 3
INVULNERABILITY_TIME = 0.9
SHOOT_COOLDOWN = 0.14
ENEMY_CONTACT_COOLDOWN = 0.5
HITSCAN_RANGE = 1600
TRAIL_DURATION = 0.05


@dataclass
class ShotTrail:
    start_x: float
    start_y: float
    end_x: float
    end_y: float
    timer: float = TRAIL_DURATION


@dataclass
class Enemy:
    x: float
    y: float
    speed: float
    radius: int
    color: tuple[int, int, int]
    points: int

    def update(self, dt: float, target_x: float, target_y: float) -> None:
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy) or 1.0
        self.x += dx / distance * self.speed * dt
        self.y += dy / distance * self.speed * dt


class ShooterGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Geometry Survivor")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.SysFont("consolas", 54, bold=True)
        self.ui_font = pygame.font.SysFont("consolas", 28)
        self.small_font = pygame.font.SysFont("consolas", 20)
        self.reset(keep_state=False)

    def reset(self, keep_state: bool = True) -> None:
        self.player_x = WINDOW_WIDTH / 2
        self.player_y = WINDOW_HEIGHT / 2
        self.lives = PLAYER_MAX_LIVES
        self.score = 0
        self.best_score = getattr(self, "best_score", 0)
        self.shot_trails: list[ShotTrail] = []
        self.enemies: list[Enemy] = []
        self.shoot_timer = 0.0
        self.spawn_timer = 0.0
        self.elapsed_time = 0.0
        self.invulnerability_timer = 0.0
        self.contact_damage_timer = 0.0
        self.state = getattr(self, "state", "start") if keep_state else "start"

    def start_game(self) -> None:
        self.reset()
        self.state = "running"

    def handle_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.state in {"start", "game_over"} and event.key == pygame.K_SPACE:
                    self.start_game()
        return True

    def update(self, dt: float) -> None:
        if self.state != "running":
            return

        self.elapsed_time += dt
        self.shoot_timer = max(0.0, self.shoot_timer - dt)
        self.spawn_timer = max(0.0, self.spawn_timer - dt)
        self.invulnerability_timer = max(0.0, self.invulnerability_timer - dt)
        self.contact_damage_timer = max(0.0, self.contact_damage_timer - dt)

        self.update_player(dt)
        self.update_shooting()
        self.update_shot_trails(dt)
        self.update_enemies(dt)
        self.handle_player_hits()
        self.spawn_enemies_if_needed()

    def update_player(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        dx = float(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - float(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        dy = float(keys[pygame.K_s] or keys[pygame.K_DOWN]) - float(
            keys[pygame.K_w] or keys[pygame.K_UP]
        )

        if dx or dy:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
            self.player_x += dx * PLAYER_SPEED * dt
            self.player_y += dy * PLAYER_SPEED * dt

        self.player_x = max(PLAYER_RADIUS, min(WINDOW_WIDTH - PLAYER_RADIUS, self.player_x))
        self.player_y = max(PLAYER_RADIUS, min(WINDOW_HEIGHT - PLAYER_RADIUS, self.player_y))

    def update_shooting(self) -> None:
        mouse_buttons = pygame.mouse.get_pressed()
        if not mouse_buttons[0] or self.shoot_timer > 0.0:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.player_x
        dy = mouse_y - self.player_y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return

        direction_x = dx / distance
        direction_y = dy / distance
        muzzle_offset = PLAYER_RADIUS + 6
        muzzle_x = self.player_x + direction_x * muzzle_offset
        muzzle_y = self.player_y + direction_y * muzzle_offset
        end_x = muzzle_x + direction_x * HITSCAN_RANGE
        end_y = muzzle_y + direction_y * HITSCAN_RANGE

        hit_enemy, hit_distance = self.find_hitscan_target(
            muzzle_x, muzzle_y, direction_x, direction_y
        )
        if hit_enemy is not None:
            hit_distance = max(0.0, hit_distance - hit_enemy.radius * 0.35)
            end_x = muzzle_x + direction_x * hit_distance
            end_y = muzzle_y + direction_y * hit_distance
            self.enemies.remove(hit_enemy)
            self.score += hit_enemy.points
            self.best_score = max(self.best_score, self.score)

        self.shot_trails.append(ShotTrail(muzzle_x, muzzle_y, end_x, end_y))
        self.shoot_timer = SHOOT_COOLDOWN

    def update_shot_trails(self, dt: float) -> None:
        for trail in self.shot_trails:
            trail.timer -= dt
        self.shot_trails = [trail for trail in self.shot_trails if trail.timer > 0.0]

    def update_enemies(self, dt: float) -> None:
        for enemy in self.enemies:
            enemy.update(dt, self.player_x, self.player_y)

    def find_hitscan_target(
        self, start_x: float, start_y: float, dir_x: float, dir_y: float
    ) -> tuple[Enemy | None, float]:
        closest_enemy = None
        closest_distance = HITSCAN_RANGE

        for enemy in self.enemies:
            to_enemy_x = enemy.x - start_x
            to_enemy_y = enemy.y - start_y
            projection = to_enemy_x * dir_x + to_enemy_y * dir_y
            if projection < 0 or projection > closest_distance:
                continue

            closest_x = start_x + dir_x * projection
            closest_y = start_y + dir_y * projection
            perpendicular_distance = math.hypot(enemy.x - closest_x, enemy.y - closest_y)

            if perpendicular_distance <= enemy.radius:
                closest_enemy = enemy
                closest_distance = projection

        return closest_enemy, closest_distance

    def handle_player_hits(self) -> None:
        if self.invulnerability_timer > 0.0 or self.contact_damage_timer > 0.0:
            return

        for enemy in self.enemies:
            if self.circle_collision(
                self.player_x,
                self.player_y,
                PLAYER_RADIUS,
                enemy.x,
                enemy.y,
                enemy.radius,
            ):
                self.lives -= 1
                self.invulnerability_timer = INVULNERABILITY_TIME
                self.contact_damage_timer = ENEMY_CONTACT_COOLDOWN
                if self.lives <= 0:
                    self.state = "game_over"
                    self.best_score = max(self.best_score, self.score)
                return

    def spawn_enemies_if_needed(self) -> None:
        if self.spawn_timer > 0.0:
            return

        difficulty = min(self.elapsed_time / 12.0, 8.0)
        self.spawn_timer = max(0.28, 1.1 - difficulty * 0.09)

        for _ in range(1 + int(self.elapsed_time // 22)):
            self.enemies.append(self.create_enemy(difficulty))

    def create_enemy(self, difficulty: float) -> Enemy:
        side = random.choice(("top", "bottom", "left", "right"))
        margin = 40
        if side == "top":
            x, y = random.uniform(0, WINDOW_WIDTH), -margin
        elif side == "bottom":
            x, y = random.uniform(0, WINDOW_WIDTH), WINDOW_HEIGHT + margin
        elif side == "left":
            x, y = -margin, random.uniform(0, WINDOW_HEIGHT)
        else:
            x, y = WINDOW_WIDTH + margin, random.uniform(0, WINDOW_HEIGHT)

        if random.random() < min(0.45, 0.18 + difficulty * 0.03):
            return Enemy(
                x=x,
                y=y,
                speed=170 + difficulty * 12,
                radius=12,
                color=ENEMY_FAST_COLOR,
                points=15,
            )

        return Enemy(
            x=x,
            y=y,
            speed=110 + difficulty * 10,
            radius=18,
            color=ENEMY_COLOR,
            points=10,
        )

    @staticmethod
    def circle_collision(
        ax: float, ay: float, ar: float, bx: float, by: float, br: float
    ) -> bool:
        return math.hypot(ax - bx, ay - by) <= ar + br

    def draw(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_grid()
        self.draw_shot_trails()
        self.draw_enemies()
        self.draw_player()
        self.draw_hud()

        if self.state == "start":
            self.draw_overlay(
                "Geometry Survivor",
                "Press SPACE to begin",
                "Move with WASD. Hold left mouse to fire.",
            )
        elif self.state == "game_over":
            self.draw_overlay(
                "Game Over",
                "Press SPACE to restart",
                f"Final Score: {self.score}",
            )

        pygame.display.flip()

    def draw_grid(self) -> None:
        spacing = 40
        for x in range(0, WINDOW_WIDTH, spacing):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, spacing):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)

    def draw_player(self) -> None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - self.player_y, mouse_x - self.player_x)
        forward_x = math.cos(angle)
        forward_y = math.sin(angle)
        side_x = -forward_y
        side_y = forward_x

        nose = (
            self.player_x + forward_x * (PLAYER_RADIUS + 8),
            self.player_y + forward_y * (PLAYER_RADIUS + 8),
        )
        rear_left = (
            self.player_x - forward_x * 10 + side_x * 12,
            self.player_y - forward_y * 10 + side_y * 12,
        )
        rear_right = (
            self.player_x - forward_x * 10 - side_x * 12,
            self.player_y - forward_y * 10 - side_y * 12,
        )

        player_color = PLAYER_HIT_COLOR if self.invulnerability_timer > 0.0 else PLAYER_COLOR
        pygame.draw.polygon(self.screen, player_color, (nose, rear_left, rear_right))
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            (int(self.player_x), int(self.player_y)),
            4,
        )

    def draw_shot_trails(self) -> None:
        for trail in self.shot_trails:
            alpha = max(0, min(255, int(255 * (trail.timer / TRAIL_DURATION))))
            color = (*BULLET_COLOR, alpha)
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(
                overlay,
                color,
                (trail.start_x, trail.start_y),
                (trail.end_x, trail.end_y),
                3,
            )
            pygame.draw.circle(
                overlay,
                color,
                (int(trail.end_x), int(trail.end_y)),
                4,
            )
            self.screen.blit(overlay, (0, 0))

    def draw_enemies(self) -> None:
        for enemy in self.enemies:
            pygame.draw.circle(
                self.screen,
                enemy.color,
                (int(enemy.x), int(enemy.y)),
                enemy.radius,
            )

    def draw_hud(self) -> None:
        score_surface = self.ui_font.render(f"Score {self.score}", True, TEXT_COLOR)
        best_surface = self.small_font.render(f"Best {self.best_score}", True, ACCENT_COLOR)
        time_surface = self.small_font.render(
            f"Threat {1 + int(self.elapsed_time // 12)}", True, MUTED_TEXT_COLOR
        )

        self.screen.blit(score_surface, (18, 14))
        self.screen.blit(best_surface, (18, 48))
        self.screen.blit(time_surface, (18, 74))

        for index in range(PLAYER_MAX_LIVES):
            color = PLAYER_COLOR if index < self.lives else GRID_COLOR
            pygame.draw.circle(
                self.screen,
                color,
                (WINDOW_WIDTH - 30 - index * 28, 30),
                10,
            )

    def draw_overlay(self, title: str, subtitle: str, hint: str) -> None:
        panel = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        panel.fill(PANEL_COLOR)
        self.screen.blit(panel, (0, 0))

        title_surface = self.title_font.render(title, True, TEXT_COLOR)
        subtitle_surface = self.ui_font.render(subtitle, True, ACCENT_COLOR)
        hint_surface = self.small_font.render(hint, True, TEXT_COLOR)
        exit_surface = self.small_font.render("Press ESC to quit.", True, MUTED_TEXT_COLOR)

        self.screen.blit(
            title_surface,
            ((WINDOW_WIDTH - title_surface.get_width()) // 2, WINDOW_HEIGHT // 2 - 90),
        )
        self.screen.blit(
            subtitle_surface,
            ((WINDOW_WIDTH - subtitle_surface.get_width()) // 2, WINDOW_HEIGHT // 2 - 20),
        )
        self.screen.blit(
            hint_surface,
            ((WINDOW_WIDTH - hint_surface.get_width()) // 2, WINDOW_HEIGHT // 2 + 24),
        )
        self.screen.blit(
            exit_surface,
            ((WINDOW_WIDTH - exit_surface.get_width()) // 2, WINDOW_HEIGHT // 2 + 56),
        )

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            running = self.handle_input()
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    ShooterGame().run()
