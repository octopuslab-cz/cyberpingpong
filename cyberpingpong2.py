# pong1 - single player

print("-> imports")
from time import sleep, sleep_ms
from machine import Pin
from utils.pinout import set_pinout
from components.rgb import Rgb 
import colors_rgb as rgb
from components.button import Button


WSMAX = 60
DELAY_MS = 10
ws = Rgb(27,WSMAX)  #dev3
isdisp7 = True

min_position = 1
default_min_position = min_position
max_position = 40
acceleration = 0.85
tolerance = 3
shorten = True
speedup = True
boundary_color = (0,50,0)
score_color = (50,0,0)

button1 = Button(Pin(32, Pin.IN), release_value=0) # ok1: release_value=1
button2 = Button(Pin(26, Pin.IN), release_value=0)

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

@button1.on_press # ok1: on_release
def player1():
    global button1_pressed
    button1_pressed = True

@button2.on_press
def player2():
    print("button2")
    global button2_pressed
    button2_pressed = True

print("start")

def draw(ws, new_position, old_position):
    ball_color = (10,0,50)
    ws.color(ball_color, new_position)
    ws.color((0,0,0), old_position)

for i in range(WSMAX):
    ws.color((0,0,0), i)
ws.color(boundary_color, min_position-1)
ws.color(boundary_color, max_position+1)

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
            
        sleep(5)
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

