import pygame
import time
import random
import cv2
import numpy as np
from imutils.video import VideoStream
import imutils
import math

pygame.init()

window_width = 500
window_height = 750

gd = pygame.display.set_mode((window_width,window_height))

car_img = pygame.image.load('car.png') 
carimg = pygame.transform.scale(car_img,(100,150))
other_car_img = pygame.image.load('other_car.png')
othercarimg = pygame.transform.scale(other_car_img,(100,150))
background_img = pygame.image.load('background.jpg')
button_img = pygame.image.load('button.png')

clock = pygame.time.Clock()

camera = cv2.VideoCapture(0)

greenLower = (39, 37, 208)
greenUpper = (102, 116, 255)

class Background():
      def __init__(self):
            self.bgimage = pygame.image.load('background_main.jpg')
            self.rectBGimg = self.bgimage.get_rect()
 
            self.bgY1 = 0
            self.bgX1 = 0
 
            self.bgY2 = -self.rectBGimg.height
            self.bgX2 = 0
 
            self.moving_speed = 15
         
      def update(self):
        self.bgY1 += self.moving_speed
        self.bgY2 += self.moving_speed
        if self.bgY1 >= self.rectBGimg.height:
            self.bgY1 = -self.rectBGimg.height+25
        if self.bgY2 >= self.rectBGimg.height:
            self.bgY2 = -self.rectBGimg.height+25
             
      def render(self):
        gd.blit(self.bgimage, (self.bgX1, self.bgY1))
        gd.blit(self.bgimage, (self.bgX2, self.bgY2))


def car(x,y):
    gd.blit(carimg,(x,y))

def gameintro():

    intro_over = False

    while intro_over == False : 

        gd.blit(background_img,(0,0))
        button()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                pygame.quit()
                quit()

def button():
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    gd.blit(button_img,(120,630))
    pygame.display.update()
    if mouse[0] > 120 and mouse[0] < 380 and mouse[1] > 630 and mouse[1] < 700 and click[0] == 1:
        gameloop()
    else:
        pass

def message(size,message,color,x_mess,y_mess):
    font = pygame.font.SysFont(None,size)
    screen_text = font.render(message,True,color)
    gd.blit(screen_text,(x_mess,y_mess))
    pygame.display.update()
    time.sleep(1)

def crash(x):
    if x < 30 or x > 370:
        message(100,"CRASHED!",(0,0,0),70,350)
        gameintro()

def other_car(y_other,yo):
    if y_other == -120:
        x_other = random.randrange(30,370)
        yo.clear()
        yo.append(x_other)

    gd.blit(othercarimg,(yo[0],y_other))
     
def car_crash(x,y,x_en,y_en):
    if ( (x < x_en+90) and (x_en+100 < x+100) and ( ((y < y_en+140) and (y_en+140 < y+150)) or ((y < y_en) and (y_en < y+150)) ) ) or ( ( (x < x_en) and (x_en < x+80) ) and ( ( (y<y_en+130) and (y_en+130<y+150) ) or ( (y<y_en) and (y_en<y+150)) ) ):
        message(100,"CRASHED!",(0,0,0),70,350)
        gameintro()

def score(count):
    font = pygame.font.SysFont(None,50)
    screen_text = font.render("SCORE:" +str(count),True,(255,255,0))
    gd.blit(screen_text,(0,0))

def gameloop():

    x = 200
    y = 570
    x_change = 0
    y_change = 0

    yo = []
    y_en = -120

    block = 15

    ctr = 0

    game_over = False

    back_ground = Background()

    while game_over == False:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                pygame.quit()
                quit()

        _, img = camera.read()
        img = cv2.flip(img, 1)

        blurred = cv2.GaussianBlur(img, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        cnts = cv2.findContours(
            mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnts = imutils.grab_contours(cnts)

        center1 = None
        center2 = None

        # only proceed if at least one contour was found
        if len(cnts) > 1:
        
            sorted(cnts,reverse=True,key=cv2.contourArea)
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c1 = cnts[0]
            ((x1, y1), radius1) = cv2.minEnclosingCircle(c1)
            M1 = cv2.moments(c1)
            center1 = (int(M1["m10"] / M1["m00"]), int(M1["m01"] / M1["m00"]))
            c2 = cnts[1]
            ((x2, y2), radius2) = cv2.minEnclosingCircle(c2)
            M2 = cv2.moments(c2)
            center2 = (int(M2["m10"] / M2["m00"]), int(M2["m01"] / M2["m00"]))
            # only proceed if the radius meets a minimum size
            if radius1 > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(img, (int(x1), int(y1)), int(radius1),
                        (0, 255, 255), 2)
                cv2.circle(img, center1, 5, (0, 0, 255), -1)

            if radius2 > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(img, (int(x2), int(y2)), int(radius2),
                        (0, 255, 255), 2)
                cv2.circle(img, center2, 5, (0, 0, 255), -1)

        if center1 != None and center2 != None:
            if center2[0] != center1[0]:
                deg = math.degrees(math.atan((center2[1]-center1[1])/(center2[0]-center1[0])))

                if 75 < deg < 90 or  -90 < deg < -75:
                    x_change = 0
                else :
                    x_change = -block*deg/90
            
            else :
                x_change = 0

        else : 
            x_change = 0

        cv2.imshow("Ouput", img)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            camera.release()
            cv2.destroyAllWindows()
            break

        x = x + x_change

        crash(x)

        back_ground.update()
        back_ground.render()

        car(x,y)

        if y_en > window_height:
            y_en = -120
            ctr = ctr+1

        score(ctr)
        other_car(y_en,yo)

        car_crash(x,y,yo[0],y_en)

        y_en += 10

        clock.tick(30) #fps

        pygame.display.update()

gameintro()



pygame.quit()
quit()