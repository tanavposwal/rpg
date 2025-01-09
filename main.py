import pygame
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Battle")

current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 100

# define font
font = pygame.font.SysFont("Inter", 26)

# load images
background_img = pygame.image.load("img/Background/background.png").convert_alpha()
panel_img = pygame.image.load("img/Icons/panel.png").convert_alpha()


def draw_text(text, x, y, color, font):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_bg():
    screen.blit(background_img, (0, 0))


def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    # show stats
    draw_text(
        f"HP: {knight.hp}/{knight.max_hp}",
        40,
        screen_height - bottom_panel + 30,
        (255, 255, 255),
        font,
    )
    draw_text(
        f"Strength: {knight.strength}",
        40,
        screen_height - bottom_panel + 60,
        (255, 255, 255),
        font,
    )
    draw_text(
        f"Potions: {knight.potions}",
        40,
        screen_height - bottom_panel + 90,
        (255, 255, 255),
        font,
    )


class Fighter:
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.x = x
        self.y = y
        self.name = name
        self.hp = max_hp
        self.max_hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # 0 - idle, 1 - attack, 2 - hurt, 3 - dead
        self.update_time = pygame.time.get_ticks()
        # load idle images
        temp_list = []
        for i in range(8):
            image = pygame.image.load(f"img/{self.name}/Idle/{i}.png")
            image = pygame.transform.scale(
                image, (image.get_width() * 2, image.get_height() * 2)
            )
            temp_list.append(image)
        self.animation_list.append(temp_list)
        # load attack images
        temp_list = []
        for i in range(8):
            image = pygame.image.load(f"img/{self.name}/Attack/{i}.png")
            image = pygame.transform.scale(
                image, (image.get_width() * 2, image.get_height() * 2)
            )
            temp_list.append(image)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        animation_cooldown = 100
        # handle aniamtion
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        # deal damage to enemy
        rand = random.randint(-5, 5)
        damage = rand + self.strength
        target.hp -= damage

        if target.hp < 1:
            target.hp = 0
            target.alive = False

        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()


class HealthBar:
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 170, 20))
        pygame.draw.rect(
            screen, (0, 255, 0), (self.x, self.y, 170 * self.hp // self.max_hp, 20)
        )


knight = Fighter(200, 290, "Knight", 30, 10, 3)
knight_health_bar = HealthBar(
    190, screen_height - bottom_panel + 35, knight.hp, knight.max_hp
)

bandit1 = Fighter(550, 295, "Bandit", 20, 6, 1)
bandit1_health_bar = HealthBar(
    500, screen_height - bottom_panel + 35, bandit1.hp, bandit1.max_hp
)
bandit2 = Fighter(700, 295, "Bandit", 20, 6, 1)
bandit2_health_bar = HealthBar(
    500, screen_height - bottom_panel + 80, bandit2.hp, bandit2.max_hp
)

# health bar above bandit
bandit_list = []
bandit_list.append(bandit1)
bandit_list.append(bandit2)

run = True
while run:

    clock.tick(fps)
    draw_bg()
    draw_panel()

    knight.update()
    knight.draw()

    knight_health_bar.draw(knight.hp)
    bandit1_health_bar.draw(bandit1.hp)
    bandit2_health_bar.draw(bandit2.hp)

    for bandit in bandit_list:
        bandit.update()
        bandit.draw()

    if knight.alive:
        if current_fighter == 1:
            action_cooldown += 1
            if action_cooldown >= action_wait_time:
                knight.attack(bandit1)
                current_fighter += 1
                action_cooldown = 0

    # enemy acition
    for count, bandit in enumerate(bandit_list):
        if current_fighter == count + 2:
            if bandit.alive:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    bandit.attack(knight)
                    current_fighter += 1
                    action_cooldown = 0
            else:
                current_fighter += 1

    # if all fighters have had a turn reset
    if current_fighter > total_fighters:
        current_fighter = 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
