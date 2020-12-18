import time
import random
from rpi_ws281x import Color, PixelStrip, ws

WIDTH=800
HEIGHT=600

# LED strip configuration:
LED_COUNT = 12        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
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

eye_color = Color (0, 0, 20)
nose_color = Color (10, 5, 0)
chase_color = Color(0, 30, 0)
score_color = Color (10,0,0)
base_color = Color (10,10,10)

snowman = Actor("snowman.png", center=(400,300))

# Speed for the LEDs must be greater than 0 (larger = faster)
speed = 1
# Where the bright LED is
chase_pos = 0
key_pressed = False

# Create PixelStrip object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
# Intialize the library (must be called once before other functions).
strip.begin()

# How long has expired since last reset
game_timing = 0
game_delay = 1/speed

score = 0

state = "pregame"

def draw():
    screen.fill((192,192,192))
    snowman.draw()

def update(dt):
    global state, game_timing, chase_pos, score, game_delay
    game_timing += dt
    if (state == "pregame"):
        if (game_timing > game_delay):
            display_pre ()
            game_timing = 0
    if (state == "gameover"):
        show_score(score)
    if (state == "game"):
        chk_game_key()
        if (game_timing > game_delay):
            state = upd_game()
            game_timing = 0
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
    return random.randint (0,LED_COUNT-1)

# Before game starts show random body colour and correct face colour
def display_pre ():
    for i in range(9):
        strip.setPixelColor(i, Color(random.randint(0,10),random.randint(0,10),random.randint(0,10)))
    strip.setPixelColor(nose_pos, nose_color)
    strip.setPixelColor(left_eye_pos, eye_color)
    strip.setPixelColor(right_eye_pos, eye_color)
    strip.show()

# Before game starts show random body colour and correct face colour
def show_score (score):
    for i in range(0,score):
        strip.setPixelColor(i, score_color)
    for i in range(score, 9):
        strip.setPixelColor(i, base_color)
    strip.setPixelColor(nose_pos, nose_color)
    strip.setPixelColor(left_eye_pos, eye_color)
    strip.setPixelColor(right_eye_pos, eye_color)
    strip.show()

def set_all_color (set_color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, set_color)
    strip.show()

def flash_led (led_no, set_color):
    for i in range(5):
        strip.setPixelColor(led_no, set_color)
        strip.show()
        time.sleep(0.2)
        strip.setPixelColor(led_no, Color(0,0,0))
        strip.show()
        time.sleep(0.2)


def chk_game_key():
    global chase_pos, score, state, game_delay, game_timing
    score_point = False
    if (chase_pos == left_eye_pos and keyboard[left_eye_key]):
        strip.setPixelColor(left_eye_pos, eye_color)
        score_point = True
    elif (chase_pos == right_eye_pos and keyboard[right_eye_key]):
        strip.setPixelColor(right_eye_pos, eye_color)
        score_point = True
    elif (chase_pos == nose_pos and keyboard[nose_key]):
        strip.setPixelColor(nose_pos, nose_color)
        score_point = True
    # none of states where button should be pressed so button press is invalid
    # prevents cheating by holding the button down constantly
    elif (keyboard[left_eye_key] or keyboard[right_eye_key] or keyboard[nose_key]):
        state = "gameover"
    if (score_point == True):
        strip.show()
        score += 1
        chase_pos = 0
        time.sleep(2)
        game_delay = 1/(speed+(score/4))
        game_timing = 0
        if (score >= 12):
            print ("Game over - maximimum")
            state = "gameover"

def upd_game():
    global chase_pos

    # Set to pale white colour
    set_all_color(Color(10,10,10))
    # About to move position - check to see if missed this press
    if (chase_pos == left_eye_pos or chase_pos == right_eye_pos or chase_pos == nose_pos):
        print ("Game over - score "+str(score))
        return ("gameover")
    chase_pos = move_pos(chase_pos)
    strip.setPixelColor (chase_pos, chase_color)
    strip.show()
    return state


