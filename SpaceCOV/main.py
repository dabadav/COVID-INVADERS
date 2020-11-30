import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 1000, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WUHAN VIRUS INVADERS")

# Load images
PURPLE_COV_SHIP = pygame.image.load(os.path.join("assets", "covid.png"))
BLUE_COV_SHIP = pygame.image.load(os.path.join("assets", "covid2.png"))
GREEN_COV_SHIP = pygame.image.load(os.path.join("assets", "covid3.png"))

##BOOST images
HEALTH_BOOST = pygame.image.load(os.path.join("assets", "health2.png"))
#MODO_SEXSO  = pygame.image.load(os.path.join("assets", ""))

# Player player
BALQUI_SHIP = pygame.image.load(os.path.join("assets", "balqui2.png"))
BALQUI_BOOST_SHIP = pygame.image.load(os.path.join("assets", "balquiBoost.png"))
BALQUI_m = pygame.image.load(os.path.join("assets", "balqui2m.png"))
BALQUI_mX = pygame.image.load(os.path.join("assets", "balqui2mX.png"))
# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "vred.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "vgreen.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "vblue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "v2.png"))
YELLOW_BOOST_LASER = pygame.image.load(os.path.join("assets", "v2boost.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background2.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    Boosted = False
    Boost_Cooldown = 5
    Boost_t = 0

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = BALQUI_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (PURPLE_COV_SHIP, RED_LASER),
                "green": (GREEN_COV_SHIP, GREEN_LASER),
                "blue": (BLUE_COV_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class Boost(Ship):
    BOOSTS_MAP = {
            "health": HEALTH_BOOST
            #"power": (GREEN_COV_SHIP, GREEN_LASER),
            }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img = self.BOOSTS_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.x += vel

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 3

    time = [0,0]
    time_c = 0

    main_font = pygame.font.SysFont("comicsans", 40)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    boosts = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        level_label = main_font.render(f"LEVEL {level}", 1, (255,255,255))
        time_label  = main_font.render(f"{time[0]:0=2d}:{time[1]:0=2d}", 1, (255,255,255))
        
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(time_label, (WIDTH - time_label.get_width() - 10, 1000-level_label.get_height()))

        for count in range(3):
            WIN.blit(BALQUI_m, (10+(count*50), 940))
        for countx in range(3-lives):
            WIN.blit(BALQUI_mX, (10+((2-countx)*50), 940))

        for enemy in enemies:
            enemy.draw(WIN)
        for boost in boosts:
            boost.draw(WIN)

        player.draw(WIN)
        
        if player.Boosted == True: 
            if time[1] >= player.Boost_t+player.Boost_Cooldown:
                player.ship_img = BALQUI_SHIP
                player.laser_img = YELLOW_LASER
                player.COOLDOWN = 30
                player.Boost_t = 0
                player.Boosted = False

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()


    while run:
        clock.tick(FPS)
        redraw_window()
        
        time_c += 1
        if time_c == FPS: 
            time[1] += 1
            if time[1] == 60:
                time[0] += 1
                time[1] = 0
            time_c = 0

        if not boosts:
            if time[1]==20 and not player.Boosted:
                healthB = Boost(0, 500, "health")
                boosts.append(healthB)

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        
        if len(enemies) == 0:
            level += 1
            wave_length += 5

            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                lives -= 1
                enemies.remove(enemy)
                  
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        for boost in boosts[:]:
            boost.move(enemy_vel)
            if collide(boost, player):
                player.Boosted = True
                player.Boost_t = time[1]
                player.ship_img = BALQUI_BOOST_SHIP
                player.laser_img = YELLOW_BOOST_LASER
                player.COOLDOWN = 10
                if player.health <= 50:
                    player.health += 50
                elif player.health > 50:
                    player.health = 100
                boosts.remove(boost)

        player.move_lasers(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
