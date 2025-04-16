import pygame
import random
import sys
import os

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

DUCK_WIDTH = 50
DUCK_HEIGHT = 30
CROSSHAIR_SIZE = 20

# Adjusted Y positions for two rows (further apart)
ROW1_Y = 150
ROW2_Y = 400

# Increased speeds (pixels per frame)
ROW1_SPEED = 5    # moves right
ROW2_SPEED = -5   # moves left

# Game conditions
TOTAL_SHOTS = 20     # 20-shot countdown
GAME_DURATION = 30   # 30-second timer

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)

# Regular point values for ducks (only used if not 0-point)
POINT_VALUES = [5, 10, 15]

# --- Resource path helper for PyInstaller ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Duck Class ---
class Duck:
    def __init__(self, x, y, speed, image):
        self.rect = pygame.Rect(x, y, DUCK_WIDTH, DUCK_HEIGHT)
        self.speed = speed
        self.image = pygame.transform.scale(image, (DUCK_WIDTH, DUCK_HEIGHT))
        self.points = 0
        self.hit = False
        self.reset_properties()

    def reset_properties(self):
        self.points = 0 if random.random() < 0.5 else random.choice(POINT_VALUES)
        self.hit = False

    def reset_position(self):
        if self.speed > 0:
            self.rect.x = -DUCK_WIDTH
        else:
            self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x += self.speed
        if self.speed > 0 and self.rect.left > SCREEN_WIDTH:
            self.reset_position()
            self.reset_properties()
        elif self.speed < 0 and self.rect.right < 0:
            self.reset_position()
            self.reset_properties()

    def draw(self, screen, font):
        screen.blit(self.image, self.rect)
        text = font.render(str(self.points), True, BLACK)
        text_pos = (self.rect.x, self.rect.y - text.get_height())
        screen.blit(text, text_pos)

# --- Crosshair Class ---
class Crosshair:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, CROSSHAIR_SIZE, CROSSHAIR_SIZE)
        self.speed = 5

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def draw(self, screen):
        center = self.rect.center
        pygame.draw.circle(screen, BLACK, center, CROSSHAIR_SIZE // 2, 2)
        pygame.draw.line(screen, BLACK, (center[0] - CROSSHAIR_SIZE, center[1]), (center[0] + CROSSHAIR_SIZE, center[1]), 2)
        pygame.draw.line(screen, BLACK, (center[0], center[1] - CROSSHAIR_SIZE), (center[0], center[1] + CROSSHAIR_SIZE), 2)

# --- Main Game Function ---
def run_game():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Carnival Duck Shooter")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    try:
        background = pygame.image.load(resource_path("assets/images/background.jpg")).convert()
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print("Background image not found or error loading image:", e)
        pygame.quit()
        sys.exit()

    try:
        duck1_image = pygame.image.load(resource_path("assets/images/Duck1.jpg")).convert_alpha()
        duck2_image = pygame.image.load(resource_path("assets/images/Duck2.jpg")).convert_alpha()
    except pygame.error as e:
        print("Duck images not found or error loading image:", e)
        pygame.quit()
        sys.exit()

    try:
        hit_sound = pygame.mixer.Sound(resource_path("assets/sounds/hit.wav"))
        miss_sound = pygame.mixer.Sound(resource_path("assets/sounds/miss.mp3"))
    except pygame.error as e:
        print("Sound files not found or error loading sound:", e)
        pygame.quit()
        sys.exit()

    ducks = []
    spacing = SCREEN_WIDTH // 5
    for i in range(5):
        x = i * spacing
        duck_top = Duck(x, ROW1_Y, ROW1_SPEED, duck1_image)
        ducks.append(duck_top)
        duck_bottom = Duck(x, ROW2_Y, ROW2_SPEED, duck2_image)
        ducks.append(duck_bottom)

    crosshair = Crosshair()

    score = 0
    shots_remaining = TOTAL_SHOTS
    start_ticks = pygame.time.get_ticks()
    game_over = False

    while not game_over:
        clock.tick(FPS)
        elapsed_seconds = (pygame.time.get_ticks() - start_ticks) / 1000
        remaining_time = max(0, GAME_DURATION - int(elapsed_seconds))
        if remaining_time <= 0:
            game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and shots_remaining > 0:
                    shot_hit = False
                    for duck in ducks:
                        if not duck.hit and crosshair.rect.colliderect(duck.rect):
                            score += duck.points
                            duck.hit = True
                            shot_hit = True
                    if shot_hit:
                        hit_sound.play()
                    else:
                        miss_sound.play()
                    shots_remaining -= 1
                    if shots_remaining == 0:
                        game_over = True

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]: dx = -1
        if keys[pygame.K_RIGHT]: dx = 1
        if keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_DOWN]: dy = 1
        crosshair.move(dx, dy)

        for duck in ducks:
            duck.update()

        screen.blit(background, (0, 0))
        for duck in ducks:
            duck.draw(screen, font)
        crosshair.draw(screen)

        score_text = font.render(f"Score: {score}", True, WHITE)
        shots_text = font.render(f"Shots: {shots_remaining}", True, WHITE)
        timer_text = font.render(f"Time: {remaining_time}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(shots_text, (SCREEN_WIDTH - shots_text.get_width() - 10, 10))
        screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 10))

        pygame.display.flip()

    return score

# --- Start Screen ---
def show_start_screen():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Carnival Duck Shooter")
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    title_text = font.render("Carnival Duck Shooter", True, WHITE)
    instruction_text = small_font.render("Press ENTER to Start", True, WHITE)

    while True:
        screen.fill(BLACK)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

# --- Game Over and Restart Function ---
def game_over_screen(score):
    screen = pygame.display.get_surface()
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    game_over_text = font.render("Game Over!", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = small_font.render("Press ENTER to Play Again", True, WHITE)

    while True:
        screen.fill(BLACK)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

# --- Main Loop ---
def main():
    pygame.init()
    pygame.font.init()
    while True:
        show_start_screen()
        score = run_game()
        game_over_screen(score)

if __name__ == '__main__':
    main()
