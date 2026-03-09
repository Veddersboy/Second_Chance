import os
import random
import pygame as pg

from src.states.minigames.minigame import Minigame

COL_BG = (18, 18, 19)
COL_TEXT = (248, 248, 248)
COL_EMPTY = (18, 18, 19)
COL_BORDER = (58, 58, 60)
COL_ABSENT = (58, 58, 60)
COL_PRESENT = (181, 159, 59)
COL_CORRECT = (83, 141, 78)

ROWS, COLS = 6, 5
TILE = 62
GAP = 8
RADIUS = 6
KEY_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]


def score_guess(secret: str, guess: str) -> list[str]:
    result = ["absent"] * 5
    secret_left = list(secret)

    for i in range(5):
        if guess[i] == secret[i]:
            result[i] = "correct"
            secret_left[i] = None

    for i in range(5):
        if result[i] == "correct":
            continue
        if guess[i] in secret_left:
            result[i] = "present"
            secret_left[secret_left.index(guess[i])] = None

    return result


def _load_word_set(path: str) -> set[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Word list file not found: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            return {line.strip().lower() for line in f if line.strip()}

    if ext == ".json":
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"Expected a JSON list in {path}")
        return {str(w).strip().lower() for w in data if str(w).strip()}

    raise ValueError(f"Unsupported word list type: {ext} (use .txt or .json)")


def status_color(status: str | None) -> tuple[int, int, int]:
    if status == "correct":
        return COL_CORRECT
    if status == "present":
        return COL_PRESENT
    if status == "absent":
        return COL_ABSENT
    return COL_EMPTY


def clamp_letter_state(old: str | None, new: str) -> str:
    order = {"absent": 0, "present": 1, "correct": 2}
    if old is None:
        return new
    return new if order[new] > order[old] else old


class Wordle(Minigame):
    def __init__(self):
        instructions = (
            "Guess the 5-letter word in 6 tries to revive. "
            "Type letters, Backspace to delete, Enter to submit."
        )
        img = "minigame_wordle.jpg"
        super().__init__(instructions, img=os.path.join("minigames", img))

        answers_path = os.path.join("assets", "wordlists", "wordle_answers.txt")
        valid_path = os.path.join("assets", "wordlists", "wordle_valid.txt")

        self.answers = sorted([w for w in _load_word_set(answers_path) if len(w) == 5 and w.isalpha()])
        self.valid_words = _load_word_set(valid_path)
        self.valid_words |= set(self.answers)

        if not self.answers:
            raise ValueError("Answer list is empty. Check your wordle_answers.txt file.")

        self._answer_queue = self.answers[:]
        random.shuffle(self._answer_queue)

        self.secret: str | None = None
        self.current = ""
        self.guesses: list[tuple[str, list[str]]] = []
        self.max_tries = 6
        self.message = ""

        self.title_font = pg.font.SysFont(None, 46)
        self.msg_font = pg.font.SysFont(None, 30)
        self.tile_font = pg.font.SysFont(None, 44)
        self.key_font = pg.font.SysFont(None, 28)

        self._start_new_round()

    def _next_secret(self) -> str:
        if not self._answer_queue:
            self._answer_queue = self.answers[:]
            random.shuffle(self._answer_queue)
        return self._answer_queue.pop()

    def _start_new_round(self):
        self.secret = self._next_secret()
        self.current = ""
        self.guesses.clear()
        self.message = ""

    def handle_events(self, events):
        super().handle_events(events)

        if self.won is not None:
            return

        for event in events:
            if event.type != pg.KEYDOWN:
                continue

            if event.key == pg.K_BACKSPACE:
                self.current = self.current[:-1]
                continue

            if event.key == pg.K_RETURN:
                self._submit_guess()
                continue

            ch = event.unicode.lower()
            if ch.isalpha() and len(ch) == 1 and len(self.current) < 5:
                self.current += ch

    def _submit_guess(self):
        if self.secret is None:
            self.message = "No secret word loaded."
            return

        guess = self.current.lower().strip()

        if len(guess) != 5:
            self.message = "Need 5 letters."
            return

        if guess not in self.valid_words:
            self.message = "Not a word."
            return

        fb = score_guess(self.secret, guess)
        self.guesses.append((guess, fb))
        self.current = ""
        self.message = ""

        if all(x == "correct" for x in fb):
            self.won = True
            self.win_text = ""
            return

        if len(self.guesses) >= self.max_tries:
            self.won = False
            return

    def update(self, events):
        super().update(events)

    def _grid_origin(self) -> tuple[int, int]:
        grid_w = COLS * TILE + (COLS - 1) * GAP
        grid_h = ROWS * TILE + (ROWS - 1) * GAP
        x0 = (self.screen.get_width() - grid_w) // 2
        y0 = 110
        return x0, y0

    def _draw_centered(self, font: pg.font.Font, text: str, y: int):
        surf = font.render(text, True, COL_TEXT)
        x = (self.screen.get_width() - surf.get_width()) // 2
        self.screen.blit(surf, (x, y))

    def _build_keyboard_map(self) -> dict[str, str]:
        m: dict[str, str] = {}
        for guess, fb in self.guesses:
            for ch, st in zip(guess, fb):
                up = ch.upper()
                m[up] = clamp_letter_state(m.get(up), st)
        return m

    def _draw_grid(self):
        x0, y0 = self._grid_origin()

        for r in range(ROWS):
            for c in range(COLS):
                x = x0 + c * (TILE + GAP)
                y = y0 + r * (TILE + GAP)
                rect = pg.Rect(x, y, TILE, TILE)

                letter = ""
                fill = COL_EMPTY
                border = COL_BORDER

                if r < len(self.guesses):
                    guess, fb = self.guesses[r]
                    letter = guess[c].upper()
                    fill = status_color(fb[c])
                    border = fill
                elif r == len(self.guesses):
                    if c < len(self.current):
                        letter = self.current[c].upper()
                        fill = (32, 32, 34)
                        border = (100, 100, 102)

                pg.draw.rect(self.screen, fill, rect, border_radius=RADIUS)
                pg.draw.rect(self.screen, border, rect, 2, border_radius=RADIUS)

                if letter:
                    surf = self.tile_font.render(letter, True, COL_TEXT)
                    tx = x + (TILE - surf.get_width()) // 2
                    ty = y + (TILE - surf.get_height()) // 2
                    self.screen.blit(surf, (tx, ty))

    def _draw_keyboard(self):
        key_map = self._build_keyboard_map()
        x0, y0 = self._grid_origin()
        grid_h = ROWS * TILE + (ROWS - 1) * GAP
        start_y = y0 + grid_h + 40

        key_w, key_h = 44, 58
        key_gap = 6

        for row_i, row in enumerate(KEY_ROWS):
            row_len = len(row)
            row_w = row_len * key_w + (row_len - 1) * key_gap

            indent = 0
            if row_i == 1:
                indent = key_w // 2
            elif row_i == 2:
                indent = key_w

            x = (self.screen.get_width() - row_w) // 2 + indent
            y = start_y + row_i * (key_h + key_gap)

            for ch in row:
                st = key_map.get(ch)
                fill = status_color(st) if st else (60, 60, 62)

                rect = pg.Rect(x, y, key_w, key_h)
                pg.draw.rect(self.screen, fill, rect, border_radius=8)

                t = self.key_font.render(ch, True, COL_TEXT)
                self.screen.blit(
                    t,
                    (x + (key_w - t.get_width()) // 2, y + (key_h - t.get_height()) // 2),
                )

                x += key_w + key_gap

    def draw(self):
        self.screen.fill(COL_BG)

        self._draw_centered(self.title_font, "WORDLE REVIVE", 30)
        if self.message:
            self._draw_centered(self.msg_font, self.message, 72)

        self._draw_grid()
        self._draw_keyboard()