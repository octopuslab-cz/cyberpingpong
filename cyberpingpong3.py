# 1D pong2   - single/two-player game (uPy v1.18 on 2022-06-10: ok)
# OctopusLAB - big display board & DoIt ESP32, 1/2 buttons

from time import sleep, sleep_ms
from machine import Pin
from utils.pinout import set_pinout
from components.button import Button
from components.rgb import Rgb 
import colors_rgb as rgb

print("init")
WSMAX = 60
DELAY_MS = 10
ws = Rgb(17,WSMAX)
isdisp7 = True

min_position = 1
default_min_position = min_position
max_position = 42

acceleration = 0.85
smash_threshold_delay = 50

# single player contstants
tolerance = 3
shorten = True
speedup = True
dynamic_speedup = False

boundary_color = (0,50,0)
score_color = (50,0,0)
ball_color = (80,0,190)

button1 = Button(Pin(39, Pin.IN), release_value=0) # ok1: release_value=1
button2 = Button(Pin(34, Pin.IN), release_value=0)
#switch = Pin(34, Pin.OUT)
#switch = Pin(27, Pin.IN)

single_player = True
single_player = False
if False and switch.value():
    single_player = False
    # double player contstants
    tolerance = 5
    shorten = False
    speedup = True
    dynamic_speedup = True

def get_new_delay(delay, hit_distance):
    global single_player
    global speedup
    global acceleration
    global dynamic_speedup
    global tolerance
    global smash_threshold_delay

    ret = None

    if not speedup:
        ret = delay

    if single_player:
        ret = delay * acceleration
    else:
        if dynamic_speedup:
            half = tolerance // 2 + tolerance % 2
            if hit_distance == half:
                # nochange
                ret = delay
                if isdisp7:
                    d7.show(f"{hit_distance} {0.0}")               
            else:
                #speedup or slowdown
                acc_factor = (half - hit_distance) / (half - 1)
                real_acc = 1 - acc_factor * (1 - acceleration)
                if hit_distance == 1 and delay > smash_threshold_delay:
                    delay = smash_threshold_delay
                ret = delay * real_acc
                print("------------------------------")
                print("delay", delay, "->", ret)
                print("hit_distance", hit_distance)
                print("acc_factor", acc_factor)
                print("direction", direction)
                print("real_acc", real_acc)
                if isdisp7:
                    d7.show(f"{hit_distance} {acc_factor}")               
        else:
            ret = delay * acceleration
    return int(ret)


print("single_player", single_player)
print("shorten", shorten)
print("speedup", speedup)

built_in_led = Pin(2, Pin.OUT)

built_in_led.on()
sleep_ms(20)
built_in_led.off()

print("test RGB")
ws.color((50,0,0),5)
sleep(0.3)
ws.color((0,50,0),5)
sleep(0.3)
ws.color((0,0,50),5)
sleep(0.3)
ws.color((0,0,0),5)

if isdisp7:
    from display7 import display7init
    d7 = display7init()
    d7.intensity = 15

@button1.on_press # ok1: on_release
def player1():
    global button1_pressed
    button1_pressed = True

@button2.on_press
def player2():
    global button2_pressed
    button2_pressed = True
    
    
def start_clear():
    for i in range(WSMAX):
        ws.color((0,0,0), i)
    ws.color(boundary_color, min_position-1)
    ws.color(boundary_color, max_position+1)


def pattern_lost(num_pat):
    for _ in range(num_pat):
        for i in range(min_position, max_position + 1):
           ws.color((i*2,0,0), i)
           sleep_ms(5)
        sleep_ms(100)
        for i in range(min_position, max_position + 1):
           ws.color((0,0,0), i)
    

print("start")


def draw(ws, new_position, old_position):
    ball_color_dynamic = (60+new_position,0,190)
    ws.color(ball_color_dynamic, new_position)
    ws.color((0,0,0), old_position)

start_clear()

position = min_position
score = 0
score_1 = 0
score_2 = 0
delay = 100
direction = 1  # or -1
button1_pressed = False
button2_pressed = False

while True:
    hit = False
    hit_distance = None
    if button2_pressed:
        button2_pressed = False
        print("button2")
        #built_in_led.on()
        #sleep_ms(3)
        #built_in_led.off()
        if not single_player and position > max_position - tolerance and direction > 0:
            direction *= -1
            hit = True
            hit_distance = max_position - position


    if button1_pressed:
        button1_pressed = False
        print("button1")
        #built_in_led.on()
        #sleep_ms(3)
        #built_in_led.off()
        if position < min_position + tolerance and direction < 0:
            direction *= -1
            if single_player:
                score += 1
                if isdisp7:
                    d7.show(f" - {score} - ")
            hit = True
            hit_distance = position - min_position + 1

    old_position = position

    if single_player:
        if position == max_position:
            direction *= -1
        if position < min_position:
            lost = true
            print(f"You've lost, your score is {score}")
            if isdisp7:
                d7.show(f"---{score}---")

            pattern_lost(3)
            for i in range(5):
                ws.color(ball_color, (i+1)*8)
                sleep(1)
            start_clear()
            if isdisp7:
                d7.show("octopus")
            # clear shortened field            
            for i in range(min_position):
                ws.color((0,0,0), default_min_position + i)
            # clear store behind field            
            for i in range(score):
                ws.color((0,0,0), max_position+1+1+i)

            min_position = default_min_position
            position = min_position

            #ws.color(boundary_color, min_position-1)
            #ws.color(boundary_color, max_position+1)

            score = 0
            direction = 1
            delay = 100
            continue

    else:
        # two players
        if position < min_position or position > max_position:
            if position < min_position:
                score_2 += 1
                direction = 1
                position = min_position
            if position > max_position:
                score_1 += 1        
                direction = -1
                position = max_position

            start_clear()
            print(f"score: {score_1} - {score_2}")
            if isdisp7:
                d7.show(f"{score_1} - {score_2}")

            delay = 100
            pattern_lost(3)
            continue

    position += direction


    draw(ws, position, old_position)
    if hit:
        if single_player:
            ws.color(score_color, max_position+1+score)
            print(f"Score {score}")
        if speedup:
            delay = get_new_delay(delay, hit_distance)
        if shorten:
            ws.color(boundary_color, min_position)
            min_position += 1

    sleep_ms(delay)

