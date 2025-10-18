import os, pygame
WHITE = (255, 255, 255)

# ----------------------------
# BUTTON CLASS
# ----------------------------
class Button:
    def __init__(self, rect, text, action, font, colorful=False):
        self.rect = rect
        self.text = text
        self.action = action
        self.font = font
        self.enabled = True
        self.colorful = colorful

    def draw(self, surf):
        mx, my = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mx, my)
        if self.colorful:
            base_color = (60, 110, 230) if hover else (40, 90, 200)
            pygame.draw.rect(surf, base_color, self.rect, border_radius=12)
            pygame.draw.rect(surf, (0, 0, 0), self.rect, 2, border_radius=12)
        else:
            color = (150, 150, 150) if hover else (120, 120, 120)
            pygame.draw.rect(surf, color, self.rect, border_radius=8)

        lbl = self.font.render(self.text, True, (255, 255, 255))
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))

    def handle(self, event, audio):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                audio.play_click()
                self.action()

# ----------------------------
# CARD VIEW
# ----------------------------
class CardView:
    def __init__(self, card, rect, font):
        self.card = card
        self.rect = rect
        self.font = font
        self.image = None
        self.selected = False
        self.last_bought = False

        # Load image from assets/cards/
        path = os.path.join("assets", "cards", f"{card}.png")
        if os.path.exists(path):
            img = pygame.image.load(path)
            self.image = pygame.transform.scale(img, (rect.width, rect.height))

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surf, (200, 200, 200), self.rect, border_radius=8)
            txt = self.font.render(self.card, True, (0, 0, 0))
            surf.blit(txt, txt.get_rect(center=self.rect.center))
        if self.selected:
            pygame.draw.rect(surf, (255, 215, 0), self.rect, 5, border_radius=10)
        elif self.last_bought:
            pygame.draw.rect(surf, (0, 200, 0), self.rect, 5, border_radius=10)
        else:
            pygame.draw.rect(surf, (0, 0, 0), self.rect, 1, border_radius=10)

    def hit_test(self, pos):
        return self.rect.collidepoint(pos)

# ----------------------------
# AUDIO
# ----------------------------
class AudioBank:
    def __init__(self):
        self.sounds = {}
        click_path = os.path.join("assets", "sounds", "sfx_click.wav")
        success_path = os.path.join("assets", "sounds", "sfx_success.wav")
        if os.path.exists(click_path):
            self.sounds["click"] = pygame.mixer.Sound(click_path)
        if os.path.exists(success_path):
            self.sounds["success"] = pygame.mixer.Sound(success_path)

    def play_click(self):
        if "click" in self.sounds:
            self.sounds["click"].play()

    def play_success(self):
        if "success" in self.sounds:
            self.sounds["success"].play()

    def start_music(self):
        path = os.path.join("assets", "sounds", "bg_music.mp3")
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
