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
tolerance = 3
shorten = True
speedup = True
boundary_color = (0,50,0)
score_color = (50,0,0)
ball_color = (80,0,190)

button1 = Button(Pin(39, Pin.IN), release_value=0) # ok1: release_value=1
button2 = Button(Pin(34, Pin.IN), release_value=0)
switch = Pin(27, Pin.OUT)

single_player = True
if switch.value():
    single_player = False
print("single_player",single_player)

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
    print("button2")
    global button2_pressed
    button2_pressed = True
    
    
def start_clear():
    for i in range(WSMAX):
        ws.color((0,0,0), i)
    ws.color(boundary_color, min_position-1)
    ws.color(boundary_color, max_position+1)


def pattern_lost(num_pat):
    for pat in range(num_pat):
        for i in range(WSMAX-1):
           ws.color((i*2,0,0), i+1)
           sleep_ms(5)
        sleep_ms(100)
        for i in range(WSMAX-1):
           ws.color((0,0,0), i+1)
    

print("start")


def draw(ws, new_position, old_position):
    ball_color_dynamic = (60+new_position,0,190)
    ws.color(ball_color_dynamic, new_position)
    ws.color((0,0,0), old_position)

start_clear()

position = min_position
score = 0
speed = 100
direction = 1  # or -1
button1_pressed = False
button2_pressed = False

while True:
    hit = False
    if button2_pressed:
        button2_pressed = False
        print("button2")
        built_in_led.on()
        sleep_ms(3)
        built_in_led.off()
        if not single_player:
            print("ToDo: multi")
    
    if button1_pressed:
        button1_pressed = False
        print("button1")
        built_in_led.on()
        sleep_ms(3)
        built_in_led.off()
        if position < min_position + tolerance and direction < 0:
            direction *= -1
            score += 1
            hit = True
            if isdisp7:
               d7.show(f" - {score} - ")

    old_position = position
    if position == max_position:
        direction *= -1
    position += direction
    
    if position < min_position:
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
            
        for i in range(min_position):
            ws.color((0,0,0), default_min_position + i)
        for i in range(score):
            ws.color((0,0,0), max_position+1+1+i)

        min_position = default_min_position
        position = min_position

        #ws.color(boundary_color, min_position-1)
        #ws.color(boundary_color, max_position+1)

        score = 0
        direction = 1
        speed = 100
        
        continue
    
    draw(ws, position, old_position)
    if hit:
        ws.color(score_color, max_position+1+score)
        print(f"Score {score}")
        if speedup:
            speed = int(speed * acceleration)
        if shorten:
            ws.color(boundary_color, min_position)
            min_position += 1

    sleep_ms(speed)

