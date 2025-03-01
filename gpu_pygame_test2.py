import pygame
from OpenGL.GL import *

pygame.init()
display = (800, 600)
pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)

renderer = glGetString(GL_RENDERER).decode("utf-8")
vendor = glGetString(GL_VENDOR).decode("utf-8")
version = glGetString(GL_VERSION).decode("utf-8")

print(f"✅ OpenGL Renderer: {renderer}")
print(f"✅ OpenGL Vendor: {vendor}")
print(f"✅ OpenGL Version: {version}")
