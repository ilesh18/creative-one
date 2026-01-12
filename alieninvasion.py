import pygame
import random
import sys
from pygame.locals import *


pygame.init()


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 50)
BLUE = (0, 150, 255)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 180)

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Alien Invasion: 100-Wave Challenge")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(25, 0), (0, 40), (50, 40)])
        pygame.draw.polygon(self.image, BLUE, [(25, 15), (15, 30), (35, 30)])
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT - 20
        self.speed = 8
        self.lives = 3
        self.shoot_delay = 200
        self.last_shot = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.rect.x = max(0, self.rect.x - self.speed)
        if keys[K_RIGHT]:
            self.rect.x = min(WINDOW_WIDTH - self.rect.width, self.rect.x + self.speed)

    def shoot(self):
        if pygame.time.get_ticks() - self.last_shot > self.shoot_delay:
            self.last_shot = pygame.time.get_ticks()
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, RED, [(20, 0), (0, 30), (40, 30)])
        pygame.draw.line(self.image, YELLOW, (10, 20), (30, 20), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > WINDOW_HEIGHT:
            player.lives -= 1  
            self.kill()
        elif self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((120, 80), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, PURPLE, [(60, 0), (0, 40), (120, 40)], 0)
        pygame.draw.rect(self.image, PURPLE, (20, 40, 80, 40))
        pygame.draw.circle(self.image, RED, (60, 60), 15)
        self.rect = self.image.get_rect()
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.y = -100
        self.speed = 1
        self.lives = 10
        self.direction = 1

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.direction * 2
        if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH:
            self.direction *= -1
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.y = -100

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, BLUE, (0, 0, 4, 16))
        pygame.draw.rect(self.image, WHITE, (1, 5, 2, 10))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -15

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

def spawn_aliens(count, speed):
    for _ in range(count):
        alien = Alien(random.randint(0, WINDOW_WIDTH - 40),
                     random.randint(-200, -40),
                     speed)
        all_sprites.add(alien)
        aliens.add(alien)

def spawn_boss():
    boss = Boss()
    all_sprites.add(boss)
    aliens.add(boss)
    return boss


all_sprites = pygame.sprite.Group()
aliens = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

wave = 1
score = 0
boss = None
spawn_aliens(5, 0.65)  
def draw_hud():
    score_text = font.render(f"Score: {score}", True, WHITE)
    wave_text = font.render(f"Wave: {wave}", True, WHITE)
    lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
    window.blit(score_text, (10, 10))
    window.blit(wave_text, (10, 40))
    window.blit(lives_text, (10, 70))
    if boss:
        boss_hp = font.render(f"BOSS: {boss.lives}/10", True, RED)
        window.blit(boss_hp, (WINDOW_WIDTH - 150, 10))

def show_message(text, color=YELLOW):
    text_surface = font.render(text, True, color)
    window.blit(text_surface, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(1500)


running = True
while running:
    clock.tick(FPS)

    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                player.shoot()
            if event.key == K_r and player.lives <= 0:
                
                all_sprites = pygame.sprite.Group()
                aliens = pygame.sprite.Group()
                bullets = pygame.sprite.Group()
                player = Player()
                all_sprites.add(player)
                wave = 1
                score = 0
                spawn_aliens(5, 0.65)  

    if player.lives <= 0:
        
        window.fill(BLACK)
        game_over_text = font.render("GAME OVER - Press R to restart", True, RED)
        window.blit(game_over_text, (WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2))
        pygame.display.flip()
        continue

    
    if len(aliens) == 0:
        if wave % 5 == 0:  
            boss = spawn_boss()
            show_message("BOSS INCOMING!")
        else:
            spawn_aliens(5, 0.65 + wave * 0.4)  
            wave += 1
            if wave > 1:
                show_message(f"Wave {wave}")

   
    all_sprites.update()

    
    alien_hits = pygame.sprite.groupcollide(aliens, bullets, False, True)
    for alien, _ in alien_hits.items():
        if isinstance(alien, Boss):
            alien.lives -= 1
            if alien.lives <= 0:
                alien.kill()
                score += 500
                boss = None
        else:
            alien.kill()
            score += 100

    if pygame.sprite.spritecollide(player, aliens, False):
        player.lives -= 1
        pygame.time.delay(500)  
   
    window.fill(BLACK)
    all_sprites.draw(window)
    draw_hud()
    pygame.display.flip()

pygame.quit()
sys.exit()
