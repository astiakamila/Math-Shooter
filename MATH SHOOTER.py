import sys
import random
import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# =====================================================
# FONT GLOBAL
# =====================================================
font_text_path = "font_text.otf"
font_number_path = "font_number.ttf"

# =====================================================
# FONT HURUF
# =====================================================
font_text = pygame.font.Font(font_text_path, 60)       # Soal, menu, judul
small_text = pygame.font.Font(font_text_path, 40)      # Teks UI kecil
big_text = pygame.font.Font(font_text_path, 70)        # Game over title

# =====================================================
# FONT ANGKA
# =====================================================
font_number = pygame.font.Font(font_number_path, 60)   # Jawaban jatuh
small_number = pygame.font.Font(font_number_path, 40)  # Score, lives
screen = pygame.display.set_mode((0,0), FULLSCREEN)
s_width, s_height = screen.get_size()

# =====================================================
# MENU BACKGROUND IMAGE
# =====================================================
menu_bg = pygame.image.load("game.png")
menu_bg = pygame.transform.scale(menu_bg, (s_width, s_height))

# =====================================================
# IMAGES
# =====================================================
player_ship = "plyship.png"
butterfly_ship = "butterfly.png"

selected_character = player_ship   # Default

# =====================================================
# SOUND EFFECTS
# =====================================================
go_sound = pygame.mixer.Sound("go.wav")
game_over_sound = pygame.mixer.Sound("game_over.wav")

# =====================================================
# MUSIC FILES
# =====================================================
start_screen_music = "cyberfunk.mp3"
gameplay_music = "epicsong.mp3"
game_over_music = "illusoryrealm.mp3"

def play_music(path, loop=-1):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(loop)

# =====================================================
# SCREEN SETUP
# =====================================================
screen = pygame.display.set_mode((0,0), FULLSCREEN)
s_width, s_height = screen.get_size()

clock = pygame.time.Clock()
FPS = 60

background_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()

# =============================
# RESPONSIVE SCALE
# =============================
base_h = 768   # resolusi patokan (misal laptop 14")
scale = s_height / base_h

# =====================================================
# GAME VARIABLES
# =====================================================
player_name = ""
lives = 3
score = 0
current_problem = ""
correct_answer = 0
answers = []
fall_speed = 3
level = 1

op_count_add = 0
op_count_mul = 0

# =====================================================
# BACKGROUND
# =====================================================
class Background(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([x, y])
        self.image.fill("white")
        self.image.set_colorkey("black")
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y += 1
        if self.rect.y > s_height:
            self.rect.y = random.randrange(-10, 0)
            self.rect.x = random.randrange(0, s_width)

import math
class PinkFlowerSky:
    def __init__(self, screen, width, height, flower_count=25):
        self.screen = screen
        self.width = width
        self.height = height
        self.flowers = self.generate_flowers(flower_count)

        self.gradient = pygame.Surface((self.width, self.height)).convert()
        top = (255, 210, 225)
        bottom = (255, 130, 170)
        for y in range(self.height):
            blend = y / self.height
            r = int(top[0] * (1 - blend) + bottom[0] * blend)
            g = int(top[1] * (1 - blend) + bottom[1] * blend)
            b = int(top[2] * (1 - blend) + bottom[2] * blend)
            pygame.draw.line(self.gradient, (r, g, b), (0, y), (self.width, y))

    def generate_flowers(self, count):
        flowers = []
        for _ in range(count):
            flowers.append({
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "radius": random.randint(6, 12),
                "petal_color": random.choice([
                    (255, 170, 200),
                    (255, 140, 180),
                    (255, 200, 230)
                ]),
                "center_color": (255, 255, 180),
                "vx": random.uniform(-0.2, 0.2),
                "vy": random.uniform(0.08, 0.3),
                "rotation": random.uniform(0, 360),
                "spin_speed": random.uniform(-0.2, 0.2)
            })
        return flowers

    def draw_flower(self, f):
        x, y = int(f["x"]), int(f["y"])
        r = f["radius"]
        for i in range(5):
            angle = math.radians(i * 72 + f["rotation"])
            px = x + math.cos(angle) * r
            py = y + math.sin(angle) * r
            pygame.draw.circle(self.screen, f["petal_color"], (int(px), int(py)), max(1, r // 2))
        pygame.draw.circle(self.screen, f["center_color"], (x, y), max(1, r // 2))

    def update(self):
        for f in self.flowers:
            f["x"] += f["vx"]
            f["y"] += f["vy"]
            f["rotation"] += f["spin_speed"]
            if f["y"] > self.height + 20:
                f["y"] = -10
                f["x"] = random.randint(0, self.width)
            if f["x"] < -20:
                f["x"] = self.width + 10
            elif f["x"] > self.width + 20:
                f["x"] = -10

    def draw(self):
        self.screen.blit(self.gradient, (0, 0))
        for f in self.flowers:
            self.draw_flower(f)

# =====================================================
# PLAYER
# =====================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey("black")
        self.upper_limit = 500

    def update(self):
        mouse = pygame.mouse.get_pos()
        new_x = mouse[0] - self.rect.width // 2
        new_y = mouse[1] - self.rect.height // 2

        if new_y < self.upper_limit:
            new_y = self.upper_limit
        if new_y > s_height - self.rect.height:
            new_y = s_height - self.rect.height

        self.rect.x = new_x
        self.rect.y = new_y

# =====================================================
# FALLING ANSWERS
# =====================================================
class FallingAnswer:
    def __init__(self, value, x):
        self.value = value
        self.x = x
        self.y = -60
        self.speed = fall_speed

    def draw(self):
        shadow = font_number.render(str(self.value), True, (0,0,0))
        text_main = font_number.render(str(self.value), True, (247, 41, 103))

        screen.blit(shadow, (self.x+3, self.y+3))
        screen.blit(text_main, (self.x, self.y))

    def update(self):
        self.y += self.speed

# =====================================================
# PROBLEM GENERATOR
# =====================================================
def create_problem():
    global current_problem, correct_answer, answers
    answers = []

    # -------------------------------
    # Range angka per level
    # -------------------------------
    if level == 1:
        min_num, max_num = 0, 9
    elif level == 2:
        min_num, max_num = 11, 19
    else:
        min_num, max_num = 21, 30

    # -------------------------------
    # Pilih operasi acak
    # -------------------------------
    operation = random.choice(["+", "-", "*", "/"])

    # -------------------------------
    # OPERASI + dan -
    # -------------------------------
    if operation in ["+", "-"]:
        a = random.randint(min_num, max_num)
        b = random.randint(min_num, max_num)

        if operation == "+":
            correct_answer = a + b
            current_problem = f"{a} + {b}"
        else:
            if b > a:
                a, b = b, a
            correct_answer = a - b
            current_problem = f"{a} - {b}"

    # -------------------------------
    # OPERASI PERKALIAN (dipermudah)
    # -------------------------------
    elif operation == "*":

        if level == 1:
            a = random.randint(1, 9)
            b = random.randint(1, 9)

        elif level == 2:
            a = random.randint(2, 9)
            b = random.randint(11, 19)

        else:
            a = random.randint(3, 9)
            b = random.randint(21, 30)

        correct_answer = a * b
        current_problem = f"{a} × {b}"

    # -------------------------------
    # OPERASI PEMBAGIAN (selalu bulat)
    # -------------------------------
    else:
        correct_answer = random.randint(min_num, max_num)
        divisor = random.randint(2, 9)
        a = correct_answer * divisor
        current_problem = f"{a} ÷ {divisor}"

    # -------------------------------
    # Generate 5 pilihan jawaban
    # -------------------------------
    answers.clear()
    wrong_answers = set()

    # -------------------------------
    # Range salah dibuat wajar
    # -------------------------------
    low = max(0, correct_answer - 15)
    high = correct_answer + 15

    # -------------------------------
    # Buat 4 jawaban salah yang masuk akal
    # -------------------------------
    while len(wrong_answers) < 4:
        w = random.randint(low, high)
        if w != correct_answer:
            wrong_answers.add(w)

    # -------------------------------
    # Gabungkan dan acak
    # -------------------------------
    final_choices = [correct_answer] + list(wrong_answers)
    random.shuffle(final_choices)

    # -------------------------------
    # Tempat jatuh angka
    # -------------------------------
    positions = [
    int(s_width * 0.15),
    int(s_width * 0.32),
    int(s_width * 0.50),
    int(s_width * 0.68),
    int(s_width * 0.85)
]
    random.shuffle(positions)

    for i, value in enumerate(final_choices):
        answers.append(FallingAnswer(value, positions[i]))

# =====================================================
# UI
# =====================================================
def vh(percent):
    return int(s_height * percent)

def vw(percent):
    return int(s_width * percent)

def draw_ui():
    score_text = small_number.render(f"Score: {score}", True, (255,255,255))
    lives_text = small_number.render(f"Lives: {lives}", True, (255,0,0))
    level_text = small_number.render(f"Level: {level}", True, (0,200,255))

    # -------------------------------
    # TEKS SOAL DENGAN BAYANGAN
    # -------------------------------
    main_color = (247, 41, 103)     # warna teks utama (magenta)
    shadow_color = (0, 0, 0)        # warna bayangan (hitam)
    
    problem_main = font_number.render(current_problem, True, main_color)
    problem_shadow = font_number.render(current_problem, True, shadow_color)

    # -------------------------------
    # Posisi teks
    # -------------------------------
    px = s_width // 2 - 60
    py = 20

    # -------------------------------
    # Tampilkan bayangan (geser 3px ke kanan & bawah)
    # -------------------------------
    screen.blit(problem_shadow, (px + 3, py + 3))

    # -------------------------------
    # Tampilkan teks utama
    # -------------------------------
    screen.blit(problem_main, (px, py))
    screen.blit(score_text, (20, 20))
    screen.blit(lives_text, (20, 60))
    screen.blit(level_text, (20, 100))

def draw_menu_background():
    screen.blit(menu_bg, (0, 0))

def draw_centered(text_surface, y):
    rect = text_surface.get_rect(center=(s_width // 2, y))
    screen.blit(text_surface, rect)

# =====================================================
# MAIN GAME CLASS
# =====================================================
class Game:
    def __init__(self):
        self.name_input_screen()
        self.character_select()  
        self.level_select()
        self.start_screen()
        self.run_game()
    
    # -------------------------------
    # PLAYER NAME INPUT SCREEN
    # -------------------------------
    def name_input_screen(self):
        global player_name

        play_music(start_screen_music)
        input_text = ""
        active = True

        while active:
            draw_menu_background()

            title = font_text.render("ENTER YOUR NAME", True, (255, 255, 0))
            draw_centered(title, vh(0.25))

            name_surface = small_text.render(input_text if input_text else "_", True, "white")
            draw_centered(name_surface, vh(0.4))

            info = small_text.render("Press ENTER to Continue", True, (200, 200, 200))
            draw_centered(info, vh(0.55))

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_RETURN and input_text.strip() != "":
                        player_name = input_text
                        return

                    elif event.key == K_BACKSPACE:
                        input_text = input_text[:-1]

                    else:
                        if len(input_text) < 12 and event.unicode.isprintable():
                            input_text += event.unicode

            pygame.display.update()
            clock.tick(60)

    # -------------------------------
    # CHARACTER SELECT
    # -------------------------------

    def character_select(self):
        global selected_character, background_type

        play_music(start_screen_music)
        selected = 1
        img1 = pygame.image.load(player_ship).convert_alpha()
        img2 = pygame.image.load(butterfly_ship).convert_alpha()


        while True:
            draw_menu_background()

            # ==== TITLE ====
            title = font_text.render("SELECT YOUR SHIP", True, (255, 255, 0))
            title_y = vh(0.18)


            # ==== LOAD IMAGES ====
            img1 = pygame.image.load(player_ship)
            img2 = pygame.image.load(butterfly_ship)

            # ==== POSISI TENGAH KIRI & KANAN ====
            center_y_img = vh(0.45)
            center_y_text = vh(0.6)

            left_x  = vw(0.35)   # posisi kiri (simetris)
            right_x = vw(0.65)   # posisi kanan (simetris)

            # ==== GAMBAR KARAKTER ====
            img1_rect = img1.get_rect(center=(left_x, center_y_img))
            img2_rect = img2.get_rect(center=(right_x, center_y_img))

            screen.blit(img1, img1_rect)
            screen.blit(img2, img2_rect)

            # ==== TEKS NAMA KARAKTER ====
            text1 = small_text.render("PLANE", True, "yellow" if selected == 1 else "white")
            text2 = small_text.render("BUTTERFLY", True, "yellow" if selected == 2 else "white")

            text1_rect = text1.get_rect(center=(left_x, center_y_text))
            text2_rect = text2.get_rect(center=(right_x, center_y_text))

            screen.blit(text1, text1_rect)
            screen.blit(text2, text2_rect)

            # ==== TEKS BAWAH (DITENGAH) ====
            confirm = small_text.render("PRESS ENTER TO CONFIRM", True, "white")
            draw_centered(title, int(s_height * 0.2))


        # Controls
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        selected = 1
                    if event.key == K_RIGHT:
                        selected = 2
                    if event.key == K_RETURN:
                        if selected == 1:
                            selected_character = player_ship
                            background_type = "stars"
                        else:
                            selected_character = butterfly_ship
                            background_type = "flowers"
                        return

            pygame.display.update()

    # -------------------------------
    # START SCREEN
    # -------------------------------
    def start_text(self):
        title = font_text.render("MATH SHOOTER", True, (255, 255, 0))
        press_start = small_text.render("ENTER to Start", True, (255, 255, 255))
        press_exit = small_text.render("ESC to Quit", True, (200, 200, 200))
        press_level = small_text.render("L to Change Level", True, (150, 200, 255))

        draw_centered(title, vh(0.35))
        draw_centered(press_start, vh(0.45))
        draw_centered(press_exit, vh(0.52))
        draw_centered(press_level, vh(0.6))


    def start_screen(self):
        play_music(start_screen_music)
        global lives, score, fall_speed

        lives = 3
        score = 0
        fall_speed = 2

        while True:
            draw_menu_background()
            self.start_text()

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if event.key == K_RETURN:
                        return
                    if event.key == K_l:
                        self.level_select()
                        return

            pygame.display.update()

    # -------------------------------
    # LEVEL SELECT
    # -------------------------------
    def level_select(self):
        global level

        selected = 1
        play_music(start_screen_music)

        while True:
            draw_menu_background()
            title = font_text.render("SELECT LEVEL", True, (255, 255, 0))
            draw_centered(title, vh(0.2))

            levels = ["Easy", "Medium", "Hard"]

            for i, txt in enumerate(levels):
                color = "yellow" if (i+1) == selected else "white"
                text_render = small_text.render(txt, True, color)
                draw_centered(text_render, vh(0.4) + i * vh(0.07))

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_UP:
                        selected = max(1, selected - 1)
                    if event.key == K_DOWN:
                        selected = min(3, selected + 1)
                    if event.key == K_RETURN:
                        level = selected
                        return

            pygame.display.update()

    # -------------------------------
    # CREATE BACKGROUND
    # -------------------------------
    def create_background(self):
        global background_object
        background_group.empty()

        if background_type == "stars":
            for i in range(50):
                size = random.randint(1, 5)
                star = Background(size, size)
                star.rect.x = random.randrange(0, s_width)
                star.rect.y = random.randrange(0, s_height)
                background_group.add(star)
                sprite_group.add(star)
        else:
            background_object = PinkFlowerSky(screen, s_width, s_height)

    # -------------------------------
    # CREATE PLAYER
    # -------------------------------
    def create_player(self):
        self.player = Player(selected_character)
        player_group.add(self.player)
        sprite_group.add(self.player)

    # -------------------------------
    # UPDATE RENDER
    # -------------------------------
    def run_update(self):
        if background_type == "flowers":
            background_object.update()
            background_object.draw()
            player_group.draw(screen)
            player_group.update()
        else:
            sprite_group.draw(screen)
            sprite_group.update()

    # -------------------------------
    # GAME OVER SCREEN
    # -------------------------------
    def game_over_text(self, selected):
        global highscore
        big = big_text
        small = small_text

        center_y = vh(0.4)

        title = big.render("GAME OVER", True, "red")
        draw_centered(title, center_y - vh(0.12))

    # Tampilkan score
        score_text = small_number.render(
        f"{player_name}'s score : {score}", True, "white"
        )
        draw_centered(score_text, center_y - vh(0.04))

        menu = ["Restart", "Main Menu", "Quit"]
        for i, m in enumerate(menu):
            color = "yellow" if i == selected else "white"
            txt = small.render(m, True, color)
            draw_centered(txt, vh(0.45) + i * vh(0.08))

    def game_over_screen(self):
        global lives, score, fall_speed, answers, op_count_add, op_count_mul

        pygame.mixer.music.stop()
        game_over_sound.play()
        pygame.time.delay(1200)

        pygame.mixer.music.load(game_over_music)
        pygame.mixer.music.play(-1)

        selected = 0

        while True:
            draw_menu_background()
            self.game_over_text(selected)

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_UP:
                        selected = (selected - 1) % 3

                    if event.key == K_DOWN:
                        selected = (selected + 1) % 3

                    if event.key == K_RETURN:
                        # Restart
                        if selected == 0:
                            # RESET STATE (tidak memanggil self.run_game() di sini)
                            lives = 3
                            score = 0
                            fall_speed = 3
                            answers = []
                            op_count_add = 0
                            op_count_mul = 0

                            background_group.empty()
                            player_group.empty()
                            sprite_group.empty()

                            # Persiapkan game baru lalu kembali ke run_game()
                            self.create_background()
                            self.create_player()
                            create_problem()

                            play_music(gameplay_music)
                            return  # Kembali ke run_game() yang akan melanjutkan loop

                        # Main Menu → balik ke menu, lalu setelah user mulai, kembali ke run_game()
                        elif selected == 1:
                            pygame.mixer.music.stop()
                            self.name_input_screen()
                            self.character_select()
                            self.level_select()
                            self.start_screen()

                            # Setelah user tekan ENTER di start_screen, siapkan ulang game seperti Restart
                            lives = 3
                            score = 0
                            fall_speed = 2
                            answers = []
                            op_count_add = 0
                            op_count_mul = 0

                            background_group.empty()
                            player_group.empty()
                            sprite_group.empty()

                            self.create_background()
                            self.create_player()
                            create_problem()

                            play_music(gameplay_music)
                            return

                        # Quit
                        elif selected == 2:
                            pygame.quit()
                            sys.exit()

            pygame.display.update()
            clock.tick(FPS)

    # -------------------------------
    # PAUSE MENU
    # -------------------------------
    def pause_menu(self):
        selected = 0
        options = ["Resume", "Restart", "Main Menu", "Quit"]

        while True:
            draw_menu_background()

            title = font_text.render("PAUSED", True, (255, 255, 0))
            draw_centered(title, vh(0.3))

            for i, op in enumerate(options):
                color = "yellow" if i == selected else "white"
                txt = small_text.render(op, True, color)
                draw_centered(txt, vh(0.45) + i * vh(0.08))


            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_UP:
                        selected = (selected - 1) % 4
                    if event.key == K_DOWN:
                        selected = (selected + 1) % 4
                    if event.key == K_RETURN:
                        if selected == 0:
                            return "resume"
                        if selected == 1:
                            return "restart"
                        if selected == 2:
                            return "menu"
                        if selected == 3:
                            pygame.quit(); sys.exit()

            pygame.display.update()
            clock.tick(60)

    # -------------------------------
    # MAIN GAME LOOP
    # -------------------------------
    def run_game(self):
        global lives, score, fall_speed, answers

        play_music(gameplay_music)

        background_group.empty()
        player_group.empty()
        sprite_group.empty()

        self.create_background()
        self.create_player()
        create_problem()

        while True:
            dt = clock.tick(FPS)

            screen.fill("black")
            self.run_update()
            draw_ui()

            # Update & draw answers
            for ans in list(answers):
                ans.update()
                ans.draw()

                # Collision check (gunakan titik pada posisi answer)
                if self.player.rect.collidepoint(ans.x, ans.y):
                    if ans.value == correct_answer:
                        go_sound.play()
                        score += 1
                    else:
                        lives -= 1

                    create_problem()
                    break

                # Jika lewat bawah layar
                if ans.y > s_height:
                    lives -= 1
                    create_problem()
                    break

            # Adjust fall speed berdasarkan score
            if score < 6:
                fall_speed = 2
            elif score < 11:
                fall_speed = 3
            elif score < 16:
                fall_speed = 4
            else:
                fall_speed = 5

            for ans in answers:
                ans.speed = fall_speed

            # Cek game over di luar loop jawaban
            if lives <= 0:
                self.game_over_screen()
                # Setelah game_over_screen() selesai, ia sudah menyiapkan game baru atau menu
                # Lanjutkan loop (game baru)
                continue

            # Event handling (satu tempat)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_p:
                        action = self.pause_menu()

                        if action == "resume":
                            pass
                        elif action == "restart":
                            lives = 3
                            score = 0
                            fall_speed = 2
                            answers = []
                            background_group.empty()
                            player_group.empty()
                            sprite_group.empty()
                            self.create_background()
                            self.create_player()
                            create_problem()
                        elif action == "menu":
                            pygame.mixer.music.stop()

                            # Balik ke menu dulu
                            self.name_input_screen()
                            self.character_select()
                            self.level_select()
                            self.start_screen()

                            # Setelah user mulai game lagi → reset state game
                            lives = 3
                            score = 0
                            fall_speed = 2
                            answers = []

                            background_group.empty()
                            player_group.empty()
                            sprite_group.empty()

                            self.create_background()
                            self.create_player()
                            create_problem()

                            play_music(gameplay_music)
                    
                            continue
        
            pygame.display.flip()

# =====================================================
# MAIN
# =====================================================
def main():
    Game()

if __name__ == "__main__":
    main()
