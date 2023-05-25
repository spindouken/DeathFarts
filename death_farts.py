import pygame
import os
import random
import sys
import math


FPS = 60
stage = 1

# Window dimensions
WIN_WIDTH = 650
WIN_HEIGHT = 1150
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
FLOOR = 1000

pygame.font.init()
STAT_FONT = pygame.font.Font("Open 24 Display St.ttf", 50)


# Load images
DEATH_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "dfhalf.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "dfhalf.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "dfhalf.png")))]
OBSTACLE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", f"obstacleBottom_stage{stage}.png")))
OBSTACLE_BOTTOM = OBSTACLE_IMG
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", f"fground_stage{stage}.png")).convert())
BG_IMG = pygame.image.load(os.path.join("imgs", f"bg_stage{stage}.png")).convert()
FART_IMGS = [pygame.image.load(os.path.join("imgs", "cloud_2.png")),
             pygame.image.load(os.path.join("imgs", "GreenCloudS.png")),
             pygame.image.load(os.path.join("imgs", "cloud_2.png")),
             pygame.image.load(os.path.join("imgs", "YellowCloudS.png")),
             pygame.image.load(os.path.join("imgs", "cloud_3.png")),
             pygame.image.load(os.path.join("imgs", "GreenCloudS.png"))]


gen = 0  # Initialize the generation counter
DRAW_LINES = True

class Death:
    IMGS = DEATH_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 5
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.angle = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        self.fart_count = 0  # farts - Initialize the fart counter
        self.fart_imgs = FART_IMGS  # farts - Set the fart images
        self.active_farts = []  # farts - Initialize the list of active farts

    def jump(self):
        self.vel = -9.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        # Calculate displacement
        d = self.vel * self.tick_count + 1.5 * self.tick_count**2

        # Set terminal velocity
        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def fart(self):
        #change angle of fart
        self.active_farts.append(Fart(self.x - 20, self.y + 20, 35))

    def draw_farts(self, win):
        # update list of active farts
        for fart in self.active_farts:
            if fart.is_faded():
                self.active_farts.remove(fart)  # remove fart if it has completely faded away

        # draw remaining active farts
        for fart in self.active_farts:
            fart.draw(win)  # pass death's position to fart's draw method

class Fart:
    """Defines the Fart Clouds that Death emits from his booty"""
    def __init__(self, death_x, death_y, angle):
        # add random deviation to initial angle of fart (angle of self.angle)
        angle_deviation = random.uniform(-20, 20) 
        self.angle = angle + angle_deviation
        # move x axis of fart closer to death (death_x - value)
        self.x = death_x + 35 * math.cos(math.radians(self.angle))
        # move y axis of fart closer to death (+ value at end)
        self.y = death_y + 20 - 60 * math.sin(math.radians(self.angle)) + 145
        self.imgs = []
        for img in FART_IMGS:
            scale = random.uniform(0.6, 1.4)
            scaled_img = pygame.transform.scale(img,
            (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.imgs.append(scaled_img)
        self.img_count = 0
        self.img = self.imgs[0]
        self.timer = 0  # initialize timer to 0
        self.fade_time = 2.0  # time for fart to fade out
        self.opacity = 1.0  # initialize opacity to 100%
        self.initial_size = 50  # Sets initial size of fart image
        self.current_size = self.initial_size  # Stores current size of fart image
        self.size_increase_rate = 50  # Sets size increase rate

        # calculate fart launch speed with random factor
        launch_speed = random.uniform(-10.0, -50.0)

        # calculate horizontal and vertical components of velocity
        # based on angle and launch speed with random components
        angle_rad = math.radians(self.angle)
        self.vx = launch_speed * math.cos(angle_rad) + random.uniform(-1, 1)
        self.vy = -launch_speed * math.sin(angle_rad) + random.uniform(-1, 1)

    def draw(self, win):
        # calculate time since last frame
        dt = 1 / FPS

        # update position based on velocity
        self.x += self.vx * dt
        self.y += self.vy * dt

        # add random drift to velocity
        self.vx += random.uniform(-20, 0)
        # second value as 0 means fart will not fly into face ;]
        self.vy += random.uniform(-40, 40)

        # update opacity based on time elapsed
        self.opacity -= dt / self.fade_time
        if self.opacity < 0:
            self.opacity = 0

        # Update the size of the fart image
        self.current_size += self.size_increase_rate / FPS

        # Scale the image based on the current size and set the alpha value
        scaled_img = pygame.transform.scale(self.img,
        (int(self.current_size), int(self.current_size)))
        alpha = int(255 * self.opacity)
        rotated_img = pygame.transform.rotate(scaled_img, self.angle)
        rotated_img.set_alpha(alpha)
        win.blit(rotated_img, (self.x, self.y))

        # cycle through fart images
        self.img_count += 1
        if self.img_count < 5:
            self.img = self.imgs[0]
        elif self.img_count < 10:
            self.img = self.imgs[1]
        elif self.img_count < 15:
            self.img = self.imgs[2]
        elif self.img_count < 20:
            self.img = self.imgs[3]
        elif self.img_count < 25:
            self.img = self.imgs[4]
        else:
            self.img_count = 0

    def is_faded(self):
        # check if fart has completely faded away
        return self.opacity <= 0

class Obstacle:
    #values below are to change obstacle 
    GAP = 370
    VEL = 5

    def __init__(self, x, stage):
        self.x = x
        self.height = 0
        # alter gap between obstacles
        self.gap = 370
        self.top = 0
        self.bottom = 0
        self.OBSTACLE_BOTTOM = pygame.image.load(os.path.join("imgs", f"obstacleBottom_stage{stage}.png")).convert_alpha()
        self.OBSTACLE_TOP = pygame.transform.flip(self.OBSTACLE_BOTTOM, False, True)
        self.passed = False
        self.set_height()
        self.stage = stage

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.OBSTACLE_TOP.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.OBSTACLE_TOP, (self.x, self.top))
        win.blit(self.OBSTACLE_BOTTOM, (self.x, self.bottom))

    def collide(self, death):
        death_mask = death.get_mask()
        top_mask = pygame.mask.from_surface(self.OBSTACLE_TOP)
        bottom_mask = pygame.mask.from_surface(self.OBSTACLE_BOTTOM)

        top_offset = (self.x - death.x, self.top - round(death.y))
        bottom_offset = (self.x - death.x, self.bottom - round(death.y))

        b_point = death_mask.overlap(bottom_mask, bottom_offset)
        t_point = death_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    VEL = 5.65
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y, stage):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        self.IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", f"fground_stage{stage}.png")).convert())

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

class Background:
    VEL = .5

    def __init__(self, stage):
        self.stage = stage
        self.BG_IMG = pygame.image.load(os.path.join("imgs",
        f"bg_stage{stage}.png")).convert()
        self.WIDTH = self.BG_IMG.get_width()
        self.HEIGHT = self.BG_IMG.get_height()
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.BG_IMG, (self.x1, 0))
        win.blit(self.BG_IMG, (self.x2, 0))

def draw_window(win, deaths, obstacles, base, background, score, gen, obstacle_ind, draw_lines=True, show_labels=True):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param death: a Death object
    :param obstacles: List of obstacles
    :param score: score of the game (int)
    :param gen: current generation
    :param obstacle_ind: index of closest obstacle
    :return: None
    """
    if gen == 0:
        gen = 1

    background.draw(win)  # Draw the scrolling background

    for obstacle in obstacles:
        obstacle.draw(win)

    base.draw(win)
    for death in deaths:
        death.draw(win)
        death.draw_farts(win)
        if draw_lines:
            try:
                pygame.draw.line(win, (191, 31, 24), (death.x+death.img.get_width()/2, death.y + death.img.get_height()/2), (obstacles[obstacle_ind].x + obstacles[obstacle_ind].OBSTACLE_TOP.get_width()/2, obstacles[obstacle_ind].height), 5)
                pygame.draw.line(win, (191, 31, 24), (death.x+death.img.get_width()/2, death.y + death.img.get_height()/2), (obstacles[obstacle_ind].x + obstacles[obstacle_ind].OBSTACLE_BOTTOM.get_width()/2, obstacles[obstacle_ind].bottom), 5)
            except:
                pass

    if show_labels:
        score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(247, 250, 0))
        win.blit(score_label, (10, 10))

        score_label = STAT_FONT.render("Alive: " + str(len(deaths)),1,(247, 250, 0))
        win.blit(score_label, (10, 50))

    score_label = STAT_FONT.render("Score: " + str(score),1,(247, 250, 0))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    pygame.display.update()

def get_current_stage(score):
    # edit x in score // x to change when stage shifts (background & obstacles)
    return (score // 14) % 3 + 1

def start_menu():
    menu_image = pygame.image.load(os.path.join("imgs", "DFMenuFinal.png"))    
    screen_width, screen_height = WIN.get_size()
    image_width, image_height = menu_image.get_size()
    x = (screen_width - image_width) // 2
    y = (screen_height - image_height) // 2

    run = True
    while run:
        WIN.blit(menu_image, (x, y))

        button_font = pygame.font.Font("Gypsy Curse.ttf", 105)
        ai_font = pygame.font.Font("Open 24 Display St.ttf", 45)
        manual_button = button_font.render("Start", 1, (247, 250, 0))
        ai_button = ai_font.render("Watch A.I.", 1, (247, 250, 0))
        leaderboard_button = ai_font.render("Leader Board", 1, (247, 250, 0))

        ai_button_rect = ai_button.get_rect(center=(WIN_WIDTH // 2 - 220, 975 + ai_button.get_height() // 2))
        leaderboard_button_rect = leaderboard_button.get_rect(center=(WIN_WIDTH // 2 + 185, 975 + leaderboard_button.get_height() // 2))


        WIN.blit(manual_button, (WIN_WIDTH // 2 - manual_button.get_width() // 2, 765))
        WIN.blit(ai_button, ai_button_rect.topleft)
        WIN.blit(leaderboard_button, leaderboard_button_rect.topleft)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (WIN_WIDTH // 2 - manual_button.get_width() // 2 <= mouse_x <= WIN_WIDTH // 2 + manual_button.get_width() // 2) and (740 <= mouse_y <= 890):
                    run = False
                    manual_play()
                elif ai_button_rect.collidepoint(mouse_x, mouse_y):
                    run = False
                    local_dir = os.path.dirname(__file__)
                    config_path = os.path.join(local_dir, 'config-feedforward.txt')
                    run_game(config_path)
                elif leaderboard_button_rect.collidepoint(mouse_x, mouse_y):
                    show_leaderboard()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    run = False
                    manual_play()
                if event.key == pygame.K_LALT:
                    run = False
                    manual_play()

def manual_play():
    death = Death(230, 350)
    score = 0

    stage = get_current_stage(score)
    background = Background(stage)
    # delays first obstacle: add + int value to
    # WIN_WIDTH to move obst off screen
    obstacles = [Obstacle(WIN_WIDTH + 200, stage)]
    base = Base(FLOOR, stage)

    clock = pygame.time.Clock()
    win = WIN

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                        death.jump()
                        death.fart()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    game_over_screen(score)

        death.move()
        base.move()
        background.move()

        rem = []
        add_obstacle = False
        for obstacle in obstacles:
            obstacle.move()
            if obstacle.collide(death):
                game_over_screen(score)

            if obstacle.x + obstacle.OBSTACLE_TOP.get_width() < 0:
                rem.append(obstacle)

            if not obstacle.passed and obstacle.x < death.x:
                obstacle.passed = True
                add_obstacle = True

        if add_obstacle:
            score += 1
            obstacles.append(Obstacle(WIN_WIDTH, stage))

            new_stage = get_current_stage(score)
            if new_stage != stage:
                stage = new_stage
                background = Background(stage)

        for r in rem:
            obstacles.remove(r)

        if death.y + death.img.get_height() - 10 >= FLOOR or death.y < -50:
            game_over_screen(score)

        draw_window(win, [death], obstacles, base, background, score, 0, 0, draw_lines=False, show_labels=False)

    print("Game Over!")

class TextInput:
    def __init__(self, x, y, width, height, font, font_size, color, border_color, border_width=1, text=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border_color = border_color
        self.border_width = border_width
        self.font = pygame.font.Font(font, font_size)
        self.color = color
        self.text = text

    def draw(self, surface):
        pygame.draw.rect(surface, self.border_color, (self.x, self.y, self.width, self.height), self.border_width)
        text_surface = self.get_surface()
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        return None

    def get_text(self):
        return self.text

    def get_surface(self):
        return self.font.render(self.text, True, self.color)

def update_leaderboard(name, score):
    leaderboard_file = "leaderboard.txt"
    top_scores = []

    with open(leaderboard_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            entry = line.strip().split(':')
            if len(entry) == 2:
                top_scores.append((entry[0], int(entry[1])))

    top_scores.append((name, score))
    top_scores.sort(key=lambda x: x[1], reverse=True)
    top_scores = top_scores[:100]

    with open(leaderboard_file, 'w') as file:
        for name, score in top_scores:
            file.write(f"{name}:{score}\n")

    return True

def show_leaderboard():
    leaderboard_file = "leaderboard.txt"
    leaderboard = []

    with open(leaderboard_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            entry = line.strip().split(':')
            if len(entry) >= 2:  # Check if entry has at least two items
                leaderboard.append((entry[0], int(entry[1])))

    leaderboard_font = pygame.font.Font("Open 24 Display St.ttf", 50)
    WIN.fill((0, 0, 0))

    name_heading = leaderboard_font.render("Name", 1, (247, 250, 0))
    score_heading = leaderboard_font.render("Score", 1, (247, 250, 0))
    WIN.blit(name_heading, (35, 50))
    WIN.blit(score_heading, (500, 50))

    for index, entry in enumerate(leaderboard[:10]):  # Show top 10 scores
        rank_text = leaderboard_font.render(f"{index + 1}.", 1, (247, 250, 0))
        name_text = leaderboard_font.render(entry[0], 1, (247, 250, 0))
        score_text = leaderboard_font.render(str(entry[1]), 1, (247, 250, 0))

        y = 100 + index * 60
        WIN.blit(rank_text, (35, y))
        WIN.blit(name_text, (85, y))
        WIN.blit(score_text, (500, y))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False

def game_over_screen(score):
    """
    Displays the game over screen and waits for 3 seconds before returning to the start menu
    :param score: the final score of the game
    """
    text_input = TextInput(WIN_WIDTH // 2 - 250, WIN_HEIGHT // 2 + 20, 500, 60, "Open 24 Display St.ttf", 50, (247, 250, 0), (255, 255, 255), border_width=1)
    enter_name_text = pygame.font.Font("Gypsy Curse.ttf", 70).render("Enter your name:", 1, (255, 255, 255))

    clock = pygame.time.Clock()

    # Use a loop to handle user input
    while True:
        # Listen for events in the event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # If the user presses the ESC key, return to the main menu without saving their data
                    start_menu()
                # If the user presses enter, get their name and exit the loop
                if event.key == pygame.K_RETURN:
                    player_name = text_input.get_text()
                    success = update_leaderboard(player_name, score)
                    if success:
                        start_menu()
                    else:
                        # If there was an error updating the leaderboard, display an error message and reset the text input
                        error_text = pygame.font.Font("Open 24 Display St.ttf", 40).render("Error updating Leader Board. Please try again.", 1, (191, 31, 24))
                        WIN.blit(error_text, (WIN_WIDTH // 2 - error_text.get_width() // 2, WIN_HEIGHT // 2 + 150))
                        pygame.display.update()
                        text_input.text = ""

                # Call the handle_event method of the TextInput object to handle the key press
                text_input.handle_event(event)

                if event.key == pygame.K_TAB:
                    manual_play()
                if event.key == pygame.K_LALT:
                    manual_play()

        # Redraw the screen with the updated text input and the "Game Over" text
        WIN.fill((2, 29, 49))
        WIN.blit(enter_name_text, (WIN_WIDTH // 2 - enter_name_text.get_width() // 2, WIN_HEIGHT // 2 - 100))
        text_input.draw(WIN)
        font = pygame.font.Font("Gypsy Curse.ttf", 120)
        small_font = pygame.font.Font("Open 24 Display St.ttf", 35)
        game_over_text = font.render("Game Over", 1, (247, 250, 0))
        score_text = font.render("Score: " + str(score), 1, (247, 250, 0))
        play_again = pygame.font.Font("Gypsy Curse.ttf", 100).render("Play Again?", 1, (247, 250, 0))
        press_tab = pygame.font.Font("Open 24 Display St.ttf", 25).render("Press Tab or Alt", 5, (255, 255, 255))
        esc_text = small_font.render("Press ESC for Main Menu", 1, (255, 255, 255))

        WIN.blit(game_over_text, (WIN_WIDTH // 2 - game_over_text.get_width() // 2, WIN_HEIGHT // 2 - game_over_text.get_height() - 340)) # - value to move up from center (y-value)
        WIN.blit(score_text, (WIN_WIDTH // 2 - score_text.get_width() // 2, WIN_HEIGHT // 2 - 340)) # - value to move up from center (y-value)
        WIN.blit(play_again, (WIN_WIDTH // 2 - play_again.get_width() // 2, WIN_HEIGHT // 2 + 150))
        WIN.blit(esc_text, (WIN_WIDTH // 2 - esc_text.get_width() // 2, 1020))
        WIN.blit(press_tab, (WIN_WIDTH // 2 - esc_text.get_width() // 2 + 100, 850))

        pygame.display.update()

        # Limit the frame rate to reduce CPU usage
        clock.tick(FPS)

        # Wait for 3 seconds
        #pygame.time.delay(1500)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    start_menu()
