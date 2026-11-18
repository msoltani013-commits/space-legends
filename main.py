import pygame
import random
import json
import os
import math

pygame.init()

# SCREEN
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = screen.get_size()
pygame.display.set_caption("SPACE LEGENDS")
clock = pygame.time.Clock()

# COLORS
BLACK = (4, 5, 22)
WHITE = (245, 250, 255)
CYAN = (40, 225, 255)
PURPLE = (170, 65, 255)
RED = (255, 65, 75)
GOLD = (255, 210, 40)
GREEN = (50, 240, 130)
ORANGE = (255, 135, 35)
GRAY = (120, 130, 155)

# FONTS
font = pygame.font.Font(None, max(24, int(H * .035)))
small = pygame.font.Font(None, max(19, int(H * .027)))
big = pygame.font.Font(None, max(48, int(H * .075)))
title = pygame.font.Font(None, max(42, int(H * .085)))

# SAVE
SAVE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "galaxy_mobile_save.json"
)

data = {
    "coins": 0,
    "best": 0,
    "owned": [0],
    "selected": 0
}

try:
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    if isinstance(loaded, dict):
        data.update(loaded)
except Exception:
    pass

if not isinstance(data.get("owned"), list):
    data["owned"] = [0]

if 0 not in data["owned"]:
    data["owned"].append(0)

try:
    data["coins"] = max(0, int(data["coins"]))
    data["best"] = max(0, int(data["best"]))
except Exception:
    data["coins"] = 0
    data["best"] = 0


def save():
    try:
        temp_file = SAVE_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(temp_file, SAVE_FILE)
    except Exception:
        pass


# SHIPS
ships = [
    {"name": "NOVA", "price": 0, "color": CYAN, "speed": 18},
    {"name": "PHANTOM", "price": 80, "color": PURPLE, "speed": 21},
    {"name": "INFERNO", "price": 150, "color": ORANGE, "speed": 24},
    {"name": "GALAXY", "price": 250, "color": GOLD, "speed": 27}
]

try:
    data["selected"] = int(data["selected"])
except Exception:
    data["selected"] = 0

if not 0 <= data["selected"] < len(ships):
    data["selected"] = 0

data["owned"] = [
    x for x in data["owned"]
    if isinstance(x, int) and 0 <= x < len(ships)
]

if 0 not in data["owned"]:
    data["owned"].append(0)

if data["selected"] not in data["owned"]:
    data["selected"] = 0

save()


# FUNCTIONS
def make_button(x, y, w, h):
    return pygame.Rect(
        int(x - w / 2),
        int(y - h / 2),
        int(w),
        int(h)
    )


def draw_text(text, x, y, f=font, color=WHITE):
    image = f.render(str(text), True, color)
    rect = image.get_rect(center=(int(x), int(y)))
    screen.blit(image, rect)


def draw_button(rect, text, color):
    pygame.draw.rect(screen, (12, 15, 40), rect.move(0, 5), border_radius=15)
    pygame.draw.rect(screen, color, rect, border_radius=15)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=15)
    draw_text(text, rect.centerx, rect.centery, font, WHITE)


# BACKGROUND
stars = []

for _ in range(100):
    stars.append([
        random.randint(0, W),
        random.randint(0, H),
        random.randint(1, 3),
        random.uniform(1, 3)
    ])


def background():
    screen.fill(BLACK)

    pygame.draw.circle(
        screen, (18, 10, 55),
        (W // 5, H // 3), int(W * .35)
    )

    pygame.draw.circle(
        screen, (10, 20, 55),
        (W * 4 // 5, H * 2 // 3), int(W * .40)
    )

    for star in stars:
        pygame.draw.circle(
            screen, (120, 155, 210),
            (int(star[0]), int(star[1])), star[2]
        )
        star[1] += star[3]

        if star[1] > H:
            star[1] = 0
            star[0] = random.randint(0, W)


# SHIP DRAWING
def draw_ship(x, y, color, scale=1):
    points = [
        (int(x), int(y - 30 * scale)),
        (int(x - 24 * scale), int(y + 22 * scale)),
        (int(x), int(y + 12 * scale)),
        (int(x + 24 * scale), int(y + 22 * scale))
    ]

    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, WHITE, points, 2)

    pygame.draw.circle(
        screen, (15, 45, 100),
        (int(x), int(y - 4 * scale)),
        max(3, int(7 * scale))
    )

    pygame.draw.polygon(
        screen, ORANGE,
        [
            (int(x - 7 * scale), int(y + 20 * scale)),
            (int(x), int(y + 37 * scale)),
            (int(x + 7 * scale), int(y + 20 * scale))
        ]
    )


# GAME DATA
player = pygame.Rect(
    W // 2 - int(W * .045),
    int(H * .76),
    int(W * .09),
    int(H * .075)
)

rocks = []
coins = []
bullets = []
powerups = []
particles = []

score = 0
lives = 3
shield = 0

rock_timer = 0
coin_timer = 0
bullet_timer = 0
power_timer = 0

game_speed = 5
state = "menu"


# BUTTONS
play_button = make_button(W / 2, H * .53, W * .65, H * .075)
shop_button = make_button(W / 2, H * .63, W * .65, H * .075)
settings_button = make_button(W / 2, H * .73, W * .65, H * .075)

left_button = pygame.Rect(
    int(W * .06), int(H * .84),
    int(W * .35), int(H * .10)
)

right_button = pygame.Rect(
    int(W * .59), int(H * .84),
    int(W * .35), int(H * .10)
)

pause_button = pygame.Rect(
    int(W * .82), int(H * .025),
    int(W * .14), int(H * .055)
)

shop_left = make_button(W * .25, H * .77, W * .30, H * .09)
shop_right = make_button(W * .75, H * .77, W * .30, H * .09)
shop_buy = make_button(W / 2, H * .87, W * .65, H * .075)
shop_back = make_button(W / 2, H * .96, W * .50, H * .06)

settings_back = make_button(W / 2, H * .72, W * .70, H * .09)
settings_menu = make_button(W / 2, H * .84, W * .70, H * .09)

resume_button = make_button(W / 2, H * .62, W * .70, H * .085)
pause_menu_button = make_button(W / 2, H * .74, W * .70, H * .085)


# RESET
def reset_game():
    global score, lives, shield
    global rock_timer, coin_timer, bullet_timer
    global power_timer, game_speed

    rocks.clear()
    coins.clear()
    bullets.clear()
    powerups.clear()
    particles.clear()

    score = 0
    lives = 3
    shield = 0

    rock_timer = 0
    coin_timer = 0
    bullet_timer = 0
    power_timer = 0

    game_speed = 5
    player.centerx = W // 2
    player.centery = int(H * .76)


# PARTICLES
def explosion(x, y, color):
    for _ in range(12):
        angle = random.random() * math.tau
        speed = random.uniform(1, 4)

        particles.append([
            float(x), float(y),
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            25, color
        ])


# MENU
def draw_menu():
    background()

    draw_text("SPACE LEGENDS", W / 2, H * .13, title, CYAN)
    draw_text("GALAXY WAR", W / 2, H * .20, font, PURPLE)

    index = data["selected"]
    draw_ship(W / 2, H * .34, ships[index]["color"], 1.5)

    draw_button(play_button, "START GAME", (20, 140, 90))
    draw_button(shop_button, "SHIP SHOP", (90, 50, 170))
    draw_button(settings_button, "SETTINGS", (45, 75, 150))

    draw_text("BEST: " + str(data["best"]), W / 2, H * .86, font, GOLD)
    draw_text("COINS: " + str(data["coins"]), W / 2, H * .92, font, GOLD)


# SHOP
def draw_shop():
    background()

    draw_text("SHIP SHOP", W / 2, H * .13, title, CYAN)
    draw_text("COINS: " + str(data["coins"]), W / 2, H * .23, font, GOLD)

    index = data["selected"]
    ship = ships[index]

    draw_ship(W / 2, H * .43, ship["color"], 2.2)
    draw_text(ship["name"], W / 2, H * .57, big, ship["color"])

    if index in data["owned"]:
        label = "OWNED"
        color = GREEN
    else:
        label = "BUY: " + str(ship["price"])
        color = GOLD

    draw_text(label, W / 2, H * .66, font, color)

    draw_button(shop_left, "<", (50, 75, 150))
    draw_button(shop_right, ">", (50, 75, 150))
    draw_button(shop_buy, "BUY / SELECT", (20, 130, 90))
    draw_button(shop_back, "BACK", (90, 50, 170))


# SETTINGS
def draw_settings():
    background()

    draw_text("SETTINGS", W / 2, H * .20, title, CYAN)

    draw_text(
        "SPACE LEGENDS",
        W / 2, H * .35, big, PURPLE
    )

    draw_text(
        "BEST SCORE: " + str(data["best"]),
        W / 2, H * .45, font, GOLD
    )

    draw_text(
        "YOUR COINS: " + str(data["coins"]),
        W / 2, H * .52, font, GOLD
    )

    draw_button(settings_back, "BACK", (50, 75, 150))
    draw_button(settings_menu, "MAIN MENU", (20, 130, 90))


# HUD
def draw_hud():
    draw_text("SCORE " + str(score), W * .23, H * .035, small, WHITE)
    draw_text("LIVES " + str(lives), W * .23, H * .075, small, RED)
    draw_text("COINS " + str(data["coins"]), W * .66, H * .035, small, GOLD)

    if shield > 0:
        draw_text("SHIELD", W / 2, H * .12, small, CYAN)


# UPDATE GAME
def update_game(move_left, move_right):
    global score, lives, shield
    global rock_timer, coin_timer, bullet_timer
    global power_timer, game_speed, state

    speed = ships[data["selected"]]["speed"]

    if move_left:
        player.x -= speed

    if move_right:
        player.x += speed

    player.x = max(0, min(W - player.width, player.x))

    rock_timer += 1
    rock_interval = max(12, 38 - score // 100)

    if rock_timer > rock_interval:
        rock_timer = 0
        size = random.randint(int(W * .055), int(W * .095))

        rocks.append(
            pygame.Rect(
                random.randint(0, W - size),
                -size, size, size
            )
        )

    coin_timer += 1

    if coin_timer > 180:
        coin_timer = 0
        coins.append(
            pygame.Rect(
                random.randint(15, W - 35),
                -25, 22, 22
            )
        )

    power_timer += 1

    if power_timer > 550:
        power_timer = 0
        powerups.append(
            pygame.Rect(
                random.randint(15, W - 40),
                -30, 28, 28
            )
        )

    bullet_timer += 1

    if bullet_timer > 16:
        bullet_timer = 0
        bullets.append(
            pygame.Rect(
                player.centerx - 3,
                player.top - 15, 6, 18
            )
        )

    for rock in rocks[:]:
        rock.y += int(game_speed)

        if rock.top > H:
            rocks.remove(rock)

        elif player.colliderect(rock):
            rocks.remove(rock)
            explosion(rock.centerx, rock.centery, RED)

            if shield > 0:
                shield = 0
            else:
                lives -= 1

                if lives <= 0:
                    state = "gameover"
                    data["best"] = max(data["best"], score)
                    save()

    for coin in coins[:]:
        coin.y += int(game_speed)

        if coin.top > H:
            coins.remove(coin)

        elif player.colliderect(coin):
            coins.remove(coin)
            data["coins"] += 1
            score += 25
            save()
            explosion(coin.centerx, coin.centery, GOLD)

    for power in powerups[:]:
        power.y += 4

        if power.top > H:
            powerups.remove(power)

        elif player.colliderect(power):
            powerups.remove(power)
            shield = 600

    if shield > 0:
        shield -= 1

    for bullet in bullets[:]:
        bullet.y -= 11

        if bullet.bottom < 0:
            bullets.remove(bullet)
            continue

        for rock in rocks[:]:
            if bullet.colliderect(rock):
                if bullet in bullets:
                    bullets.remove(bullet)

                if rock in rocks:
                    rocks.remove(rock)

                score += 5
                explosion(rock.centerx, rock.centery, ORANGE)
                break

    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 1

        if p[4] <= 0:
            particles.remove(p)

    game_speed = min(13, 5 + score / 1000)


# DRAW GAME
def draw_game():
    background()

    for rock in rocks:
        pygame.draw.circle(screen, GRAY, rock.center, rock.width // 2)
        pygame.draw.circle(screen, WHITE, rock.center, rock.width // 2, 2)

    for coin in coins:
        pygame.draw.circle(screen, GOLD, coin.center, 11)
        pygame.draw.circle(screen, WHITE, coin.center, 11, 2)

    for power in powerups:
        pygame.draw.rect(screen, CYAN, power, border_radius=7)
        draw_text("+", power.centerx, power.centery, font, BLACK)

    for bullet in bullets:
        pygame.draw.rect(screen, CYAN, bullet, border_radius=4)

    for p in particles:
        pygame.draw.circle(
            screen, p[5],
            (int(p[0]), int(p[1])),
            max(1, p[4] // 6)
        )

    index = data["selected"]
    draw_ship(player.centerx, player.centery, ships[index]["color"])

    if shield > 0:
        pygame.draw.circle(
            screen, CYAN,
            player.center, int(W * .07), 3
        )

    draw_hud()

    draw_button(left_button, "<", (35, 65, 140))
    draw_button(right_button, ">", (35, 65, 140))
    draw_button(pause_button, "||", (100, 50, 150))


# GAME OVER
def draw_gameover():
    background()

    draw_text("GAME OVER", W / 2, H * .32, title, RED)
    draw_text("SCORE: " + str(score), W / 2, H * .45, big, WHITE)
    draw_text("BEST: " + str(data["best"]), W / 2, H * .56, font, GOLD)
    draw_text("TAP TO PLAY AGAIN", W / 2, H * .75, font, GREEN)
    draw_text("TAP TOP TO MENU", W / 2, H * .83, small, CYAN)


# INPUT
active_fingers = {}
mouse_down = False
mouse_position = (0, 0)

# MAIN LOOP
running = True

while running:
    clock.tick(60)
    tapped = None

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if state == "playing":
                    state = "paused"
                elif state == "paused":
                    state = "playing"
                elif state != "menu":
                    state = "menu"
                else:
                    running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                tapped = event.pos
                mouse_down = True
                mouse_position = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_down = False

        if event.type == pygame.MOUSEMOTION:
            mouse_position = event.pos

        if event.type == pygame.FINGERDOWN:
            pos = (int(event.x * W), int(event.y * H))
            tapped = pos
            active_fingers[event.finger_id] = pos

        if event.type == pygame.FINGERMOTION:
            active_fingers[event.finger_id] = (
                int(event.x * W), int(event.y * H)
            )

        if event.type == pygame.FINGERUP:
            active_fingers.pop(event.finger_id, None)

    # MENU
    if state == "menu":
        draw_menu()

        if tapped:
            if play_button.collidepoint(tapped):
                reset_game()
                state = "playing"

            elif shop_button.collidepoint(tapped):
                state = "shop"

            elif settings_button.collidepoint(tapped):
                state = "settings"

    # SHOP
    elif state == "shop":
        draw_shop()

        if tapped:
            if shop_back.collidepoint(tapped):
                state = "menu"

            elif shop_left.collidepoint(tapped):
                data["selected"] = (data["selected"] - 1) % len(ships)

            elif shop_right.collidepoint(tapped):
                data["selected"] = (data["selected"] + 1) % len(ships)

            elif shop_buy.collidepoint(tapped):
                index = data["selected"]

                if index in data["owned"]:
                    data["selected"] = index

                elif data["coins"] >= ships[index]["price"]:
                    data["coins"] -= ships[index]["price"]
                    data["owned"].append(index)
                    data["selected"] = index

                save()

    # SETTINGS
    elif state == "settings":
        draw_settings()

        if tapped:
            if settings_back.collidepoint(tapped):
                state = "menu"

            elif settings_menu.collidepoint(tapped):
                state = "menu"

    # PLAYING
    elif state == "playing":

        if tapped and pause_button.collidepoint(tapped):
            state = "paused"

        else:
            keys = pygame.key.get_pressed()

            move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

            for pos in active_fingers.values():
                if left_button.collidepoint(pos):
                    move_left = True

                if right_button.collidepoint(pos):
                    move_right = True

            if mouse_down:
                if left_button.collidepoint(mouse_position):
                    move_left = True

                if right_button.collidepoint(mouse_position):
                    move_right = True

            if tapped:
                if left_button.collidepoint(tapped):
                    move_left = True

                if right_button.collidepoint(tapped):
                    move_right = True

            update_game(move_left, move_right)

        draw_game()

    # PAUSED
    elif state == "paused":
        draw_game()

        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        draw_text("PAUSED", W / 2, H * .35, title, CYAN)

        draw_button(resume_button, "RESUME", (20, 130, 90))
        draw_button(pause_menu_button, "MAIN MENU", (90, 50, 170))

        if tapped:
            if resume_button.collidepoint(tapped):
                state = "playing"

            elif pause_menu_button.collidepoint(tapped):
                save()
                state = "menu"

    # GAME OVER
    elif state == "gameover":
        draw_gameover()

        if tapped:
            if tapped[1] < H * .25:
                state = "menu"
            else:
                reset_game()
                state = "playing"

    pygame.display.flip()

save()
pygame.quit()
