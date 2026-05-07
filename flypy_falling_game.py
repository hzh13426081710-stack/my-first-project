import random
from dataclasses import dataclass

import pygame


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
FPS = 60

BACKGROUND_COLOR = (12, 16, 24)
GRID_COLOR = (29, 39, 56)
TEXT_COLOR = (241, 245, 249)
MUTED_TEXT_COLOR = (148, 163, 184)
ACCENT_COLOR = (94, 234, 212)
WARNING_COLOR = (251, 191, 36)
DANGER_COLOR = (248, 113, 113)
TARGET_COLOR = (37, 99, 235)
TARGET_EDGE_COLOR = (125, 211, 252)
PANEL_COLOR = (15, 23, 42, 220)
INPUT_COLOR = (34, 197, 94)

PLAYER_LIVES = 5
TARGET_WIDTH = 126
TARGET_HEIGHT = 56
SPAWN_Y = 86
BOTTOM_LIMIT = WINDOW_HEIGHT - 58


INITIAL_CODES = {
    "b": "b",
    "p": "p",
    "m": "m",
    "f": "f",
    "d": "d",
    "t": "t",
    "n": "n",
    "l": "l",
    "g": "g",
    "k": "k",
    "h": "h",
    "j": "j",
    "q": "q",
    "x": "x",
    "zh": "v",
    "ch": "i",
    "sh": "u",
    "r": "r",
    "z": "z",
    "c": "c",
    "s": "s",
    "y": "y",
    "w": "w",
}

FINAL_CODES = {
    "a": "a",
    "ai": "d",
    "an": "j",
    "ang": "h",
    "ao": "c",
    "e": "e",
    "ei": "w",
    "en": "f",
    "eng": "g",
    "er": "r",
    "i": "i",
    "ia": "x",
    "ian": "m",
    "iang": "l",
    "iao": "n",
    "ie": "p",
    "in": "b",
    "ing": "k",
    "iong": "s",
    "iu": "q",
    "o": "o",
    "ong": "s",
    "ou": "z",
    "u": "u",
    "ua": "x",
    "uai": "k",
    "uan": "r",
    "uang": "l",
    "ue": "t",
    "ui": "v",
    "un": "y",
    "uo": "o",
    "v": "v",
    "ve": "t",
    "van": "r",
    "vn": "y",
}

ZERO_INITIAL_CODES = {
    "a": "aa",
    "ai": "ai",
    "an": "an",
    "ang": "ah",
    "ao": "ao",
    "e": "ee",
    "ei": "ei",
    "en": "en",
    "eng": "eg",
    "er": "er",
    "o": "oo",
    "ou": "ou",
}

YU_FINALS = {
    "yu": "v",
    "yuan": "van",
    "yue": "ve",
    "yun": "vn",
}

LEVELS = {
    1: {
        "name": "基础声韵",
        "hint": "常见简单音节，适合热身",
        "syllables": [
            "ba",
            "bo",
            "ma",
            "mo",
            "fa",
            "fo",
            "da",
            "de",
            "ta",
            "te",
            "na",
            "ne",
            "ni",
            "li",
            "la",
            "le",
            "ga",
            "ge",
            "ka",
            "ke",
            "ha",
            "he",
            "hao",
            "mei",
            "ming",
            "lai",
            "zai",
            "wo",
            "you",
        ],
    },
    2: {
        "name": "易混韵母",
        "hint": "集中练 an/ang、en/eng、in/ing",
        "syllables": [
            "ban",
            "bang",
            "pan",
            "pang",
            "man",
            "mang",
            "fan",
            "fang",
            "dan",
            "dang",
            "tan",
            "tang",
            "nan",
            "nang",
            "lan",
            "lang",
            "gen",
            "geng",
            "ken",
            "keng",
            "hen",
            "heng",
            "zhen",
            "zheng",
            "chen",
            "cheng",
            "shen",
            "sheng",
            "xin",
            "xing",
            "min",
            "ming",
            "jin",
            "jing",
            "qin",
            "qing",
        ],
    },
    3: {
        "name": "翘舌平舌",
        "hint": "对比 zh/ch/sh 与 z/c/s",
        "syllables": [
            "zhi",
            "chi",
            "shi",
            "zi",
            "ci",
            "si",
            "zha",
            "cha",
            "sha",
            "za",
            "ca",
            "sa",
            "zhan",
            "chan",
            "shan",
            "zan",
            "can",
            "san",
            "zhang",
            "chang",
            "shang",
            "zang",
            "cang",
            "sang",
            "zhong",
            "chong",
            "shou",
            "zou",
            "cou",
            "sou",
        ],
    },
}

LEVELS[4] = {
    "name": "全量混合",
    "hint": "混合全部内置音节",
    "syllables": sorted(
        set(LEVELS[1]["syllables"])
        | set(LEVELS[2]["syllables"])
        | set(LEVELS[3]["syllables"])
        | {
            "xiang",
            "shuang",
            "yuan",
            "yue",
            "yun",
            "xue",
            "juan",
            "quan",
            "xuan",
            "guang",
            "kuang",
            "huang",
            "qiao",
            "xiao",
            "jiong",
            "qiong",
            "xiong",
            "ruan",
            "run",
            "rui",
            "luo",
            "nuo",
            "dui",
            "tui",
        },
    ),
}


@dataclass
class FallingTarget:
    syllable: str
    code: str
    x: float
    y: float
    speed: float


def make_font(size: int, bold: bool = False, monospace: bool = False) -> pygame.font.Font:
    if monospace:
        candidates = ["consolas", "couriernew", "microsoftyahei", "simhei"]
    else:
        candidates = ["microsoftyahei", "simhei", "simsun", "arialunicode", "consolas"]

    for name in candidates:
        path = pygame.font.match_font(name, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.SysFont(None, size, bold=bold)


def flypy_code(syllable: str) -> str:
    syllable = syllable.lower().replace("ü", "v")

    if syllable in ZERO_INITIAL_CODES:
        return ZERO_INITIAL_CODES[syllable]
    if syllable in YU_FINALS:
        final = YU_FINALS[syllable]
        return "y" + FINAL_CODES[final]

    initial = ""
    final = syllable
    for candidate in ("zh", "ch", "sh"):
        if syllable.startswith(candidate):
            initial = candidate
            final = syllable[len(candidate) :]
            break

    if not initial and syllable[:1] in INITIAL_CODES:
        initial = syllable[0]
        final = syllable[1:]

    if initial in {"j", "q", "x"}:
        if final in {"u", "ue", "uan", "un"}:
            final = {"u": "v", "ue": "ve", "uan": "van", "un": "vn"}[final]

    if initial == "y":
        if syllable in YU_FINALS:
            final = YU_FINALS[syllable]
        elif final.startswith("u"):
            final = final[1:] or "u"
        elif final.startswith("i"):
            final = final[1:] or "i"

    if initial == "w":
        if final.startswith("u"):
            final = final[1:] or "u"
        elif final == "o":
            final = "o"

    if initial not in INITIAL_CODES or final not in FINAL_CODES:
        raise ValueError(f"Unsupported syllable for Flypy mapping: {syllable}")
    return INITIAL_CODES[initial] + FINAL_CODES[final]


class FlypyFallingGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("小鹤双拼下落练习")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = make_font(46, bold=True)
        self.ui_font = make_font(26)
        self.small_font = make_font(19)
        self.code_font = make_font(28, bold=True, monospace=True)
        self.target_font = make_font(27, bold=True, monospace=True)
        self.best_score = 0
        self.selected_level = 1
        self.state = "level_select"
        self.reset_round()

    def reset_round(self) -> None:
        self.targets: list[FallingTarget] = []
        self.input_buffer = ""
        self.score = 0
        self.lives = PLAYER_LIVES
        self.combo = 0
        self.max_combo = 0
        self.correct_count = 0
        self.attempt_count = 0
        self.spawn_timer = 0.5
        self.elapsed_time = 0.0
        self.miss_flash = 0.0
        self.message = ""

    @property
    def syllable_pool(self) -> list[str]:
        return list(LEVELS[self.selected_level]["syllables"])

    def start_level(self, level: int) -> None:
        self.selected_level = level
        self.reset_round()
        self.state = "running"

    def handle_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.state == "level_select":
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        self.start_level(1)
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        self.start_level(2)
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        self.start_level(3)
                    elif event.key in (pygame.K_4, pygame.K_KP4):
                        self.start_level(4)
                elif self.state == "game_over":
                    if event.key == pygame.K_SPACE:
                        self.start_level(self.selected_level)
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        self.start_level(1)
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        self.start_level(2)
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        self.start_level(3)
                    elif event.key in (pygame.K_4, pygame.K_KP4):
                        self.start_level(4)
                elif self.state == "running":
                    if event.key == pygame.K_BACKSPACE:
                        self.input_buffer = self.input_buffer[:-1]
                    elif event.unicode and event.unicode.isalpha():
                        self.input_buffer += event.unicode.lower()
                        if len(self.input_buffer) >= 2:
                            self.check_answer(self.input_buffer[:2])
        return True

    def check_answer(self, code: str) -> None:
        self.attempt_count += 1
        matches = [target for target in self.targets if target.code == code]

        if matches:
            target = max(matches, key=lambda item: item.y)
            self.targets.remove(target)
            self.correct_count += 1
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.score += 10 + min(self.combo, 20)
            self.message = f"命中 {target.syllable} = {target.code}"
        else:
            self.combo = 0
            self.score = max(0, self.score - 2)
            self.miss_flash = 0.22
            self.message = f"{code} 没有命中"

        self.input_buffer = ""
        self.best_score = max(self.best_score, self.score)

    def spawn_target(self) -> None:
        syllable = random.choice(self.syllable_pool)
        code = flypy_code(syllable)
        lane_count = 6
        lane_width = WINDOW_WIDTH / lane_count
        lane = random.randrange(lane_count)
        x = lane * lane_width + (lane_width - TARGET_WIDTH) / 2
        occupied = [target for target in self.targets if abs(target.x - x) < 10 and target.y < 150]
        if occupied:
            x = random.randrange(40, WINDOW_WIDTH - TARGET_WIDTH - 40)

        base_speed = 72 + (self.selected_level - 1) * 8
        speed = base_speed + min(self.elapsed_time * 0.25, 28)
        self.targets.append(FallingTarget(syllable, code, x, SPAWN_Y, speed))

    def update(self, dt: float) -> None:
        if self.state != "running":
            return

        self.elapsed_time += dt
        self.spawn_timer -= dt
        self.miss_flash = max(0.0, self.miss_flash - dt)

        spawn_interval = max(0.9, 1.65 - min(self.elapsed_time * 0.01, 0.45))
        if self.spawn_timer <= 0:
            self.spawn_target()
            self.spawn_timer = spawn_interval

        for target in self.targets[:]:
            target.y += target.speed * dt
            if target.y + TARGET_HEIGHT >= BOTTOM_LIMIT:
                self.targets.remove(target)
                self.lives -= 1
                self.combo = 0
                self.message = f"漏掉 {target.syllable} = {target.code}"
                self.miss_flash = 0.28
                if self.lives <= 0:
                    self.state = "game_over"
                    self.best_score = max(self.best_score, self.score)
                    break

    def draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        center: tuple[int, int] | None = None,
        topleft: tuple[int, int] | None = None,
    ) -> pygame.Surface:
        surface = font.render(text, True, color)
        if center is not None:
            rect = surface.get_rect(center=center)
            self.screen.blit(surface, rect)
        elif topleft is not None:
            self.screen.blit(surface, topleft)
        return surface

    def draw_background(self) -> None:
        self.screen.fill(BACKGROUND_COLOR)
        for y in range(80, WINDOW_HEIGHT, 42):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y), 1)
        for x in range(0, WINDOW_WIDTH, 80):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 80), (x, WINDOW_HEIGHT), 1)

        if self.miss_flash > 0:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((248, 113, 113, int(90 * min(self.miss_flash / 0.28, 1))))
            self.screen.blit(overlay, (0, 0))

    def draw_hud(self) -> None:
        level = LEVELS[self.selected_level]
        self.draw_text(f"关卡 {self.selected_level}: {level['name']}", self.small_font, ACCENT_COLOR, topleft=(18, 12))
        self.draw_text(f"分数 {self.score}", self.ui_font, TEXT_COLOR, topleft=(18, 38))
        self.draw_text(f"最佳 {self.best_score}", self.small_font, MUTED_TEXT_COLOR, topleft=(18, 70))

        input_text = self.input_buffer.upper().ljust(2, "_")
        input_surface = self.code_font.render(input_text, True, INPUT_COLOR)
        input_rect = input_surface.get_rect(center=(WINDOW_WIDTH // 2, 38))
        self.screen.blit(input_surface, input_rect)
        self.draw_text("当前输入", self.small_font, MUTED_TEXT_COLOR, center=(WINDOW_WIDTH // 2, 70))

        combo_color = WARNING_COLOR if self.combo else MUTED_TEXT_COLOR
        combo_surface = self.small_font.render(f"连击 {self.combo}  最高 {self.max_combo}", True, combo_color)
        self.screen.blit(combo_surface, (WINDOW_WIDTH - combo_surface.get_width() - 18, 15))

        for index in range(PLAYER_LIVES):
            color = DANGER_COLOR if index < self.lives else GRID_COLOR
            pygame.draw.circle(self.screen, color, (WINDOW_WIDTH - 30 - index * 28, 58), 10)

        if self.message:
            color = DANGER_COLOR if self.miss_flash > 0 else MUTED_TEXT_COLOR
            message_surface = self.small_font.render(self.message, True, color)
            self.screen.blit(message_surface, (WINDOW_WIDTH - message_surface.get_width() - 18, 76))

    def draw_targets(self) -> None:
        for target in self.targets:
            rect = pygame.Rect(int(target.x), int(target.y), TARGET_WIDTH, TARGET_HEIGHT)
            pygame.draw.rect(self.screen, TARGET_COLOR, rect, border_radius=8)
            pygame.draw.rect(self.screen, TARGET_EDGE_COLOR, rect, 2, border_radius=8)
            self.draw_text(target.syllable, self.target_font, TEXT_COLOR, center=rect.center)

    def draw_level_select(self) -> None:
        self.draw_background()
        self.draw_text("小鹤双拼下落练习", self.title_font, TEXT_COLOR, center=(WINDOW_WIDTH // 2, 92))
        self.draw_text("按数字键选择关卡，输入两个字母消除下落音节", self.small_font, MUTED_TEXT_COLOR, center=(WINDOW_WIDTH // 2, 138))

        start_y = 205
        for index in range(1, 5):
            level = LEVELS[index]
            rect = pygame.Rect(170, start_y + (index - 1) * 82, 620, 58)
            pygame.draw.rect(self.screen, PANEL_COLOR, rect, border_radius=8)
            pygame.draw.rect(self.screen, GRID_COLOR, rect, 1, border_radius=8)
            self.draw_text(f"{index}", self.code_font, ACCENT_COLOR, center=(rect.x + 34, rect.centery))
            self.draw_text(level["name"], self.ui_font, TEXT_COLOR, topleft=(rect.x + 78, rect.y + 8))
            self.draw_text(level["hint"], self.small_font, MUTED_TEXT_COLOR, topleft=(rect.x + 78, rect.y + 34))

        self.draw_text("ESC 退出", self.small_font, MUTED_TEXT_COLOR, center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 42))
        pygame.display.flip()

    def draw_game_over(self) -> None:
        self.draw_background()
        self.draw_targets()
        self.draw_hud()

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill(PANEL_COLOR)
        self.screen.blit(overlay, (0, 0))

        accuracy = 0 if self.attempt_count == 0 else self.correct_count / self.attempt_count * 100
        self.draw_text("练习结束", self.title_font, TEXT_COLOR, center=(WINDOW_WIDTH // 2, 176))
        self.draw_text(f"分数 {self.score}    最佳 {self.best_score}", self.ui_font, ACCENT_COLOR, center=(WINDOW_WIDTH // 2, 242))
        self.draw_text(
            f"正确 {self.correct_count}/{self.attempt_count}    正确率 {accuracy:.0f}%    最高连击 {self.max_combo}",
            self.small_font,
            TEXT_COLOR,
            center=(WINDOW_WIDTH // 2, 292),
        )
        self.draw_text("SPACE 重开当前关卡    1-4 切换关卡    ESC 退出", self.small_font, MUTED_TEXT_COLOR, center=(WINDOW_WIDTH // 2, 352))
        pygame.display.flip()

    def draw(self) -> None:
        if self.state == "level_select":
            self.draw_level_select()
            return
        if self.state == "game_over":
            self.draw_game_over()
            return

        self.draw_background()
        self.draw_hud()
        self.draw_targets()
        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000
            running = self.handle_input()
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    FlypyFallingGame().run()
