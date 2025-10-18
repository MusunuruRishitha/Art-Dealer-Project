import os, sys, random, pygame
from pygame import Rect
from game_engine import GameSession
from ui_manager import Button, CardView, AudioBank, WHITE

# --------------------------------
# SETUP
# --------------------------------
WIDTH, HEIGHT = 768, 900
FPS = 60

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎨 The Art Dealer Game")
clock = pygame.time.Clock()

FONT_XL = pygame.font.SysFont(None, 64)
FONT_LG = pygame.font.SysFont(None, 48)
FONT_MD = pygame.font.SysFont(None, 36)
FONT_SM = pygame.font.SysFont(None, 28)

audio = AudioBank()
audio.start_music()

# --------------------------------
# BALLOON
# --------------------------------
class Balloon:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vy = random.uniform(-2.5, -1.5)
        self.vx = random.uniform(-0.5, 0.5)
        path = os.path.join("assets", "balloons", "balloons.png")
        self.image = pygame.image.load(path) if os.path.exists(path) else None
        if self.image:
            self.image = pygame.transform.scale(self.image, (40, 60))
            self.image.set_colorkey((255, 255, 255))

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, (int(self.x), int(self.y)))
        else:
            pygame.draw.circle(surf, (255, 0, 0), (int(self.x), int(self.y)), 12)

# --------------------------------
# MENU
# --------------------------------
def scene_menu() -> str:
    buttons, choice = [], {"level": None}
    def pick(level): choice["level"] = level

    buttons.append(Button(Rect(80, 200, 240, 70), "K–2", lambda: pick("K-2"), FONT_MD, colorful=True))
    buttons.append(Button(Rect(80, 290, 240, 70), "3–5", lambda: pick("3-5"), FONT_MD, colorful=True))
    buttons.append(Button(Rect(80, 380, 240, 70), "6–8", lambda: pick("6-8"), FONT_MD, colorful=True))

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            for b in buttons: b.handle(e, audio)

        if choice["level"]: return choice["level"]

        screen.fill(WHITE)
        title = FONT_XL.render("🎨 The Art Dealer Game", True, (20, 60, 150))
        screen.blit(title, title.get_rect(center=(WIDTH//2, 100)))
        subtitle = FONT_SM.render("A fun way to learn math and logic!", True, (50, 50, 50))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH//2, 160)))

        for b in buttons: b.draw(screen)
        pygame.display.flip(); clock.tick(FPS)

# --------------------------------
# GAME SCENE
# --------------------------------
def scene_game(level: str):
    global go_back
    go_back = False

    session = GameSession(level)
    card_views, balloons, selected = [], [], []
    start_x, start_y, gap_x, gap_y, w, h = 300, 220, 115, 150, 95, 135
    warning_msg = None
    warning_timer = 0

    def rebuild():
        card_views.clear()
        for i, c in enumerate(session.market):
            r, cidx = divmod(i, 4)
            card_views.append(CardView(c, Rect(start_x + cidx * gap_x, start_y + r * gap_y, w, h), FONT_MD))
    rebuild()

    pending_guess = None
    dd_scroll = 0
    dropdown_open = False
    guess_count = 0
    max_guesses = 3
    revealed = False

    def show_warning(msg):
        nonlocal warning_msg, warning_timer
        warning_msg = msg
        warning_timer = pygame.time.get_ticks()
        audio.play_click()
    
    def reveal_answer():
        """Display the dealer's pattern before closing or restarting."""
        dealer_pattern = getattr(session, "dealer_pattern", "Unknown pattern")
        msg = FONT_MD.render(f"🎯 Dealer's pattern was: {dealer_pattern}", True, (0, 120, 0))
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT - 130)))
        pygame.display.flip()
        pygame.time.wait(2500)

    # ------------- EVALUATE BUTTON -------------
    def on_eval():
        if len(selected) != 4:
            show_warning("⚠️ Please select 4 cards!")
            return
        if not pending_guess:
            show_warning("⚠️ Select a pattern first!")
            return

        funcs = session.patterns_for_level()
        pat_fn = funcs.get(pending_guess)
        if not pat_fn:
            show_warning("Pattern not available.")
            return

        # Reset previous highlights
        for cv in card_views:
            cv.last_bought = False

        picked = [session.market[i] for i in selected]
        try:
            ok = bool(pat_fn(picked))
        except Exception:
            ok = False

        for i, cv in enumerate(card_views):
            if i in selected:
                cv.last_bought = ok

        if ok:
            show_warning("✅ Pattern matched!")
        else:
            show_warning("❌ Pattern not matched!")

    # ------------- SUBMIT BUTTON -------------
    def on_submit():
        nonlocal guess_count, revealed, pending_guess
        if len(selected) != 4:
            show_warning("⚠️ Please select 4 cards!")
            return
        if not pending_guess:
            show_warning("⚠️ Select a pattern first!")
            return
        if guess_count >= max_guesses:
            show_warning("⏳ No more guesses left! Restarting round...")
            pygame.time.wait(1000)
            on_restart()
            return

        funcs = session.patterns_for_level()
        pat_fn = funcs.get(pending_guess)
        if not pat_fn:
            show_warning("Pattern not available.")
            return

        # --- Step 1: Evaluate selected cards ---
        picked = [session.market[i] for i in selected]
        try:
            cards_match = bool(pat_fn(picked))
        except Exception:
            cards_match = False

        # --- Step 2: Check dealer pattern ---
        guess_ok = session.make_guess(pending_guess)

        # --- Step 3: Visual feedback ---
        for cv in card_views:
            cv.last_bought = False
        for i in selected:
            card_views[i].last_bought = cards_match

        # --- Step 4: Logic based on correctness ---
        if not cards_match:
            # Don't consume a guess if your 4 cards don’t match the selected pattern
            show_warning("⚠️ Your selected cards don't match the chosen pattern! Try again.")
            return

        # Only count as a real guess if cards_match == True
        guess_count += 1

        # --- Step 5: Evaluate outcome ---
        if cards_match and guess_ok:
            audio.play_success()
            for bx in range(WIDTH // 2, WIDTH - 60, 80):
                balloons.append(Balloon(bx, HEIGHT - 60))
            show_warning("🎉 Perfect! Cards and pattern both match dealer!")
            pygame.time.wait(1000)
            on_restart()
            return
        elif cards_match and not guess_ok:
            show_warning(f"✅ Cards match, ❌ but dealer’s pattern differs ({guess_count}/{max_guesses})")
        elif not cards_match and guess_ok:
            # (This case won’t actually happen now because cards_match False already returned above)
            show_warning(f"❌ Cards don’t match, but ✅ dealer’s pattern correct! ({guess_count}/{max_guesses})")
        else:
            show_warning(f"❌ Both incorrect ({guess_count}/{max_guesses})")

        if guess_count >= max_guesses:
            show_warning("🔁 Out of guesses! Starting new round...")
            reveal_answer()
            pygame.time.wait(1200)
            on_restart()

    # ------------- RESTART -------------
    def on_restart():
        nonlocal pending_guess, guess_count, revealed
        session.restart_round()
        rebuild()
        selected.clear()
        for cv in card_views:
            cv.selected = False
            cv.last_bought = False
        pending_guess = None
        guess_count = 0
        revealed = False
        dd_btn.text = "Select Pattern ▼"

    # ------------- DROPDOWN -------------
    def toggle_dd():
        nonlocal dropdown_open, dd_scroll
        dropdown_open = not dropdown_open
        if dropdown_open:
            dd_scroll = 0
        audio.play_click()

    def choose(name):
        nonlocal dropdown_open, pending_guess
        dropdown_open = False
        if name == "__clear__":
            pending_guess = None
            dd_btn.text = "Select Pattern ▼"
            show_warning("Cleared selection")
            return
        pending_guess = name
        dd_btn.text = f"Pending: {name} ▾"
        show_warning(f"Pattern selected: {name}")

    # ------------- BUTTONS -------------
    base_y = 200
    eval_btn = Button(Rect(40, base_y, 220, 50), "EVALUATE", on_eval, FONT_MD, colorful=True)
    restart_btn = Button(Rect(40, base_y + 70, 220, 50), "RESTART", on_restart, FONT_MD, colorful=True)
    back_btn = Button(Rect(40, base_y + 140, 220, 50), "BACK", lambda: setattr(sys.modules[__name__], "go_back", True), FONT_MD, colorful=True)
    dd_btn = Button(Rect(40, base_y + 210, 220, 50), "Select Pattern ▼", toggle_dd, FONT_MD, colorful=True)
    submit_btn = Button(Rect(40, base_y + 280, 220, 50), "SUBMIT GUESS", on_submit, FONT_MD, colorful=True)
    exit_btn = Button(Rect(WIDTH - 200, HEIGHT - 200, 140, 50), "EXIT GAME", lambda: pygame.quit() or sys.exit(), FONT_MD, colorful=True)

    # ---------------- MAIN LOOP ----------------
    while True:
        base_patterns = sorted(session.patterns_for_level()) or ["all red"]
        pattern_names = ["__clear__"] + base_patterns

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                pos = e.pos
                for i, cv in enumerate(card_views):
                    if cv.hit_test(pos):
                        if not cv.selected and len(selected) >= 4:
                            show_warning("⚠️ Only 4 cards allowed!")
                        else:
                            cv.selected = not cv.selected
                            if cv.selected:
                                if i not in selected: selected.append(i)
                            else:
                                if i in selected: selected.remove(i)
                            for v in card_views: v.last_bought = False
                            audio.play_click()
                for b in [eval_btn, restart_btn, back_btn, dd_btn, submit_btn, exit_btn]:
                    b.handle(e, audio)
                if dropdown_open:
                    for i, name in enumerate(pattern_names):
                        y = base_y + 270 + (i * 42) - dd_scroll
                        r = Rect(40, y, 220, 40)
                        if r.collidepoint(pos):
                            choose(name)
            if e.type == pygame.MOUSEWHEEL and dropdown_open:
                dd_scroll = max(0, dd_scroll - int(e.y * 30))

        if go_back:
            return

        for b in balloons:
            b.update()
        balloons[:] = [b for b in balloons if b.y > -80]

        # DRAW EVERYTHING
        screen.fill(WHITE)
        title = FONT_LG.render(f"Art Dealer Game ({level})", True, (20, 40, 130))
        subtitle = FONT_SM.render("Pick 4 cards matching the dealer’s pattern!", True, (60, 60, 60))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 50)))
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 90)))

        for b in [eval_btn, restart_btn, back_btn, dd_btn, submit_btn, exit_btn]:
            b.draw(screen)

        if dropdown_open:
            clip_rect = Rect(40, base_y + 270, 220, 6 * 42)
            old_clip = screen.get_clip()
            screen.set_clip(clip_rect)
            for i, name in enumerate(pattern_names):
                y = base_y + 270 + (i * 42) - dd_scroll
                r = Rect(40, y, 220, 40)
                pygame.draw.rect(screen, (30, 90, 180), r, border_radius=8)
                pygame.draw.rect(screen, (0, 0, 0), r, 1, border_radius=8)
                display_name = "Clear guess" if name == "__clear__" else name
                lbl = FONT_SM.render(display_name, True, (255, 255, 255))
                screen.blit(lbl, lbl.get_rect(center=r.center))
            screen.set_clip(old_clip)

        for cv in card_views: cv.draw(screen)
        for b in balloons: b.draw(screen)

        if warning_msg and pygame.time.get_ticks() - warning_timer < 2500:
            warn = FONT_MD.render(warning_msg, True, (200, 0, 0))
            screen.blit(warn, warn.get_rect(center=(WIDTH // 2, HEIGHT - 80)))

        pygame.display.flip(); clock.tick(FPS)

# --------------------------------
def main():
    while True:
        lvl = scene_menu()
        scene_game(lvl)

if __name__ == "__main__":
    main()
