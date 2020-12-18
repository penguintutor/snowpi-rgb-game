import time
import random

WIDTH=800
HEIGHT=600

# LED strip configuration:
LED_COUNT = 12        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 20  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0

# The keys are reversed (left and right refer to the snowman, but controller is held facing opposite)
# Left button on controller = right_eye_key - Right button on controller = left_eye_key
left_eye_pos = 10
left_eye_key = keys.A
right_eye_pos = 11
right_eye_key = keys.Y
nose_pos = 9
nose_key = keys.B
start_key = keys.X
quit_key = keys.Q

# Colors should be 0 to 192 (or 255 for very bright)
eye_color = (0, 0, 192)
nose_color = (192, 97, 0)
chase_color = (0, 255, 0)
score_color = (192,0,0)
base_color = (192,192,192)
white_color = (192,192,192)

snowman_shape = Actor("snowman-shape.png", topleft=(0,200))

# Speed for the LEDs must be greater than 0 (larger = faster)
speed = 1
# Where the bright LED is
chase_pos = 0
key_pressed = False


# How long has expired since last reset
game_timing = 0
game_delay = 1/speed

# list of x,y positions of pixels on screen
pixel_pos = [
    (340, 500),
    (326, 460),
    (340, 420),
    (400, 500),
    (400, 460),
    (400, 420),  
    (460, 500),
    (474, 460),
    (460, 420),
    (400, 350),
    (420, 320),
    (380, 320)
    ]

# These are updated as required and will then be drawn during each refresh
pixel_color = [(200,200,200)] * 12

score = 0

state = "pregame"

def draw():
    screen.fill((180,199,220))
    snowman_shape.draw()
    if (state == "pregame"):
        draw_start()
    elif (state == "game" or state == "gamepoint"):
        draw_game()
    elif (state == "gameover"):
    	draw_gameover()
    draw_pixels()
    screen.draw.text("SnowPi RGB Game", centerx=400, top=50, fontsize=60, color=(0,0,255), shadow=(1,1), scolor=(0,0,0))

def draw_game():
    screen.draw.text("Score "+str(score), centerx=400, top=100, fontsize=40, color=(0,0,0))

def draw_gameover():
    screen.draw.text("Game Over", centerx=400, top=100, fontsize=40, color=(0,0,0))
    if (score >= 12):
    	screen.draw.text("You Win!", centerx=400, top=140, fontsize=40, color=(0,0,0))
    else:
    	screen.draw.text("Score "+str(score), centerx=400, top=140, fontsize=40, color=(0,0,0))
    screen.draw.text("Press "+start_key.name+" to play again", centerx=400, top=180, fontsize=40, color=(0,0,0))

def draw_start():
    screen.draw.text("Press "+start_key.name+" to start", centerx=400, top=100, fontsize=40, color=(0,0,0))

def draw_pixels():
    for i in range (len(pixel_pos)):
        screen.draw.filled_circle(pixel_pos[i], 10, (pixel_color[i]))


def update(dt):
    global state, game_timing, chase_pos, score, game_delay
    game_timing += dt
    # check if quit key pressed
    if (keyboard[quit_key]):
    	quit()
    if (state == "pregame"):
        if (game_timing > game_delay):
            display_pre ()
            game_timing = 0
    elif (state == "gameover"):
        show_score(score)
    elif (state == "game"):
        chk_game_key()
        if (game_timing > game_delay):
            state = upd_game()
            game_timing = 0
    elif (state == "gamepoint"):
    	# 2 second delay before resuming game
    	if (game_timing > 2):
    		game_timing = 0
    		state = "game"
    # start using the start key
    if (state == "gameover" or state == "pregame"):
        if (keyboard[start_key]):
            state = "game"
            # reset LED (so not start with face)
            chase_pos = 0
            # reset score
            score = 0
            game_delay = 1/speed

# Move the position of the active LED
# Currently returns random, but could be updated to follow certain patterns
def move_pos (current_pos):
	new_pos = current_pos
	# Must return different value to current position
	while (new_pos == current_pos):
		new_pos = random.randint (0,LED_COUNT-1)
	return new_pos
    

# Don't set pixel directly - instead use this which can update screen and/or pixel as required
def set_pixel (pos, this_pixel_color):
    global pixel_color
    pixel_color[pos] = this_pixel_color

# Before game starts show random body colour and correct face colour
def display_pre ():
    for i in range(9):
        set_pixel(i, (random.randint(0,192),random.randint(0,192),random.randint(0,192)))
    set_pixel(nose_pos, nose_color)
    set_pixel(left_eye_pos, eye_color)
    set_pixel(right_eye_pos, eye_color)
    

# Before game starts show random body colour and correct face colour
def show_score (score):
    for i in range(0,score):
        set_pixel(i, score_color)
    for i in range(score, 9):
        set_pixel(i, base_color)
    set_pixel(nose_pos, nose_color)
    set_pixel(left_eye_pos, eye_color)
    set_pixel(right_eye_pos, eye_color)
    

# Sets all pixels to a colour - set_color should be an rgb tuple
def set_all_color (set_color):
    for i in range(len(pixel_pos)):
        set_pixel(i, set_color)
    

def flash_led (led_no, set_color):
    for i in range(5):
        set_pixel(led_no, set_color)
        
        time.sleep(0.2)
        set_pixel(led_no, 0,0,0)
        
        time.sleep(0.2)


def chk_game_key():
    global chase_pos, score, state, game_delay, game_timing
    score_point = False
    if (score >= 12):
        state = "gameover"
    if (chase_pos == left_eye_pos and keyboard[left_eye_key]):
        set_pixel(left_eye_pos, eye_color)
        score_point = True
    elif (chase_pos == right_eye_pos and keyboard[right_eye_key]):
        set_pixel(right_eye_pos, eye_color)
        score_point = True
    elif (chase_pos == nose_pos and keyboard[nose_key]):
        set_pixel(nose_pos, nose_color)
        score_point = True
    # none of states where button should be pressed so button press is invalid
    # prevents cheating by holding the button down constantly
    elif (keyboard[left_eye_key] or keyboard[right_eye_key] or keyboard[nose_key]):
        state = "gameover"
    if (score_point == True):
        
        score += 1
        chase_pos = 0
        # convert speed and score into delay
        game_delay = 1/(speed+(score/4))
        game_timing = 0
        state = "gamepoint"


def upd_game():
    global chase_pos

    set_all_color(white_color)
    # About to move position - check to see if missed this press
    if (chase_pos == left_eye_pos or chase_pos == right_eye_pos or chase_pos == nose_pos):
        return ("gameover")
    set_pixel (chase_pos, (white_color))
    chase_pos = move_pos(chase_pos)
    set_pixel (chase_pos, chase_color)
    
    return state


