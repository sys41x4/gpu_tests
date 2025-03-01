import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import time

NUM_OBJECTS = 100000  # Increase to load GPU

def generate_objects():
    return np.random.uniform(-10, 10, (NUM_OBJECTS, 3))

def draw_objects(objects):
    glBegin(GL_POINTS)
    for obj in objects:
        glVertex3fv(obj)
    glEnd()

pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0, 0, -20)

objects = generate_objects()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    start = time.time()
    
    glRotatef(0.5, 1, 1, 1)  
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_objects(objects)
    
    pygame.display.flip()
    
    end = time.time()
    print(f"Frame time: {end - start:.4f} sec")  # Monitor frame rate

