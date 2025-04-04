import pygame
import random
from button import Button

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 800
screen_height = 400

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Battle")

current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 100
attack = False
potion = False
potion_effect = 15
clicked = False
game_over = 0

# define font
font = pygame.font.SysFont("Georgia", 18)

# load images
background_img = pygame.image.load("img/Background/background.png").convert_alpha()
panel_img = pygame.image.load("img/Icons/panel.png").convert_alpha()
sword_img = pygame.image.load("img/Icons/sword.png").convert_alpha()
potion_img = pygame.image.load("img/Icons/potion.png").convert_alpha()
restart_img = pygame.image.load("img/Icons/restart.png").convert_alpha()
victory_img = pygame.image.load("img/Icons/victory.png").convert_alpha()
defeat_img = pygame.image.load("img/Icons/defeat.png").convert_alpha()
setting_img = pygame.image.load("img/Icons/Buttons/Settings.png").convert_alpha()
volume_img = pygame.image.load("img/Icons/Buttons/Volume.png").convert_alpha()
achievement_img = pygame.image.load(
    "img/Icons/Buttons/Achievements.png"
).convert_alpha()


def draw_text(text, x, y, color, font):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def draw_bg():
    screen.blit(background_img, (0, 0))


def draw_panel():
    lvl_badge = pygame.image.load(
        f"img/Icons/Levels/0{curr_level + 1}.png"
    ).convert_alpha()
    draw_text("Level", 350, 20, (255, 255, 255), font)
    screen.blit(lvl_badge, (405, 23))


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
        # load hurt images
        temp_list = []
        for i in range(3):
            image = pygame.image.load(f"img/{self.name}/Hurt/{i}.png")
            image = pygame.transform.scale(
                image, (image.get_width() * 2, image.get_height() * 2)
            )
            temp_list.append(image)
        self.animation_list.append(temp_list)
        # load death images
        temp_list = []
        for i in range(10):
            image = pygame.image.load(f"img/{self.name}/Death/{i}.png")
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
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        # deal damage to enemy
        rand = random.randint(-5, 5)
        damage = rand + self.strength
        target.hp -= damage

        target.hurt()

        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()

        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def reset(self):
        self.hp = self.max_hp
        self.potions = self.start_potions
        self.alive = True
        self.action = 0
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
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 50, 10))
        pygame.draw.rect(
            screen, (0, 255, 0), (self.x, self.y, 50 * self.hp // self.max_hp, 10)
        )


curr_level = 0
levels = [
    [(550, 295), (700, 295)],
    [(550, 295), (650, 295), (750, 295)],
]

knight = Fighter(200, 290, "Knight", 30, 10, 3)
knight_health_bar = HealthBar(175, 240, knight.hp, knight.max_hp)

bandit_list = []
bandit_healthbar_list = []


def make_level():
    for x, y in levels[curr_level]:
        bandit = Fighter(x, y, "Bandit", 20, 5, 1)
        bandit_health_bar = HealthBar(x - 25, y - 55, bandit.hp, bandit.max_hp)
        bandit_list.append(bandit)
        bandit_healthbar_list.append(bandit_health_bar)


# create button
potion_button = Button(screen, 150, 15, potion_img, 30, 30)
setting_button = Button(screen, 650, 20, setting_img, 30, 30)
achievement_button = Button(screen, 700, 20, achievement_img, 30, 30)
volume_button = Button(screen, 750, 20, volume_img, 30, 30)
restart_button = Button(screen, 330, 120, restart_img, 120, 30)

make_level()

run = True
while run:
    clock.tick(fps)
    draw_bg()
    draw_panel()

    knight.update()
    knight.draw()

    knight_health_bar.draw(knight.hp)

    for i in range(len(bandit_list)):
        bandit_list[i].update()
        bandit_list[i].draw()
        bandit_healthbar_list[i].draw(bandit_list[i].hp)

    # control player actions
    attack = False
    potion = False
    target = None

    # reset mouse
    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos) and bandit.alive:
            # hide mouse
            pygame.mouse.set_visible(False)
            screen.blit(sword_img, pos)
            if clicked:
                attack = True
                target = bandit_list[count]

    # button actions
    setting_button.draw()
    achievement_button.draw()
    volume_button.draw()
    if potion_button.draw() and knight.hp < 25:
        potion = True
    draw_text(
        str(knight.potions),
        170,
        10,
        (255, 255, 255),
        font,
    )

    if game_over == 0:
        # player actions
        if knight.alive:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    if attack and target is not None:
                        knight.attack(target)
                        current_fighter += 1
                        action_cooldown = 0
                    if potion:
                        if knight.potions > 0:
                            # heal
                            if knight.max_hp - knight.hp > potion_effect:
                                heal_amount = potion_effect
                            else:
                                heal_amount = knight.max_hp - knight.hp
                            knight.hp += heal_amount
                            knight.potions -= 1
                            potion = False
                            current_fighter += 1
                            action_cooldown = 0
        else:
            game_over = -1

        # enemy acition
        for count, bandit in enumerate(bandit_list):
            if current_fighter == count + 2:
                if bandit.alive:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        if bandit.hp < bandit.max_hp / 2 and bandit.potions > 0:
                            # heal
                            if bandit.max_hp - bandit.hp > potion_effect:
                                heal_amount = potion_effect
                            else:
                                heal_amount = bandit.max_hp - bandit.hp
                            bandit.hp += heal_amount
                            bandit.potions -= 1
                            current_fighter += 1
                            action_cooldown = 0
                        else:
                            bandit.attack(knight)
                            current_fighter += 1
                            action_cooldown = 0
                else:
                    current_fighter += 1

        # if all fighters have had a turn reset
        if current_fighter > total_fighters:
            current_fighter = 1

    # check if all bandits are dead
    alive_bandits = 0
    for bandit in bandit_list:
        if bandit.alive:
            alive_bandits += 1

    if alive_bandits == 0:
        game_over = 1

    # check game is over
    if game_over != 0:
        if game_over == 1:
            screen.blit(
                victory_img, (screen_width // 2 - victory_img.get_width() // 2, 50)
            )
        else:
            screen.blit(
                defeat_img, (screen_width // 2 - defeat_img.get_width() // 2, 50)
            )
        if restart_button.draw():
            knight.reset()
            for bandit in bandit_list:
                bandit.reset()
            game_over = 0
            action_cooldown = 0
            current_fighter = 1

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
