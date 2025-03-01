import pygame
from OpenGL.GL import *
import numpy as np

pygame.init()
display = (1920, 1080)  # Larger resolution to increase usage
pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
glClearColor(0, 0, 0, 1)

# Create a shader program
vertex_shader = """
#version 130
in vec2 position;
in vec4 color;
out vec4 vColor;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    vColor = color;
}
"""

fragment_shader = """
#version 130
in vec4 vColor;
out vec4 FragColor;
void main() {
    FragColor = vColor;  
}
"""

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader))
    return shader

program = glCreateProgram()
vs = compile_shader(vertex_shader, GL_VERTEX_SHADER)
fs = compile_shader(fragment_shader, GL_FRAGMENT_SHADER)
glAttachShader(program, vs)
glAttachShader(program, fs)
glLinkProgram(program)

# Generate 10 million points
num_points = 10_000_00  # More points to consume GPU memory
vertices = np.random.uniform(-1, 1, (num_points, 2)).astype(np.float32)
colors = np.random.uniform(0, 1, (num_points, 4)).astype(np.float32)  # RGBA color for each vertex

vao = glGenVertexArrays(1)
glBindVertexArray(vao)

vbo = glGenBuffers(2)  # Two buffers: one for positions, one for colors

# Upload position data
glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

position = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(position)
glVertexAttribPointer(position, 2, GL_FLOAT, False, 0, None)

# Upload color data
glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_STATIC_DRAW)

color_loc = glGetAttribLocation(program, "color")
glEnableVertexAttribArray(color_loc)
glVertexAttribPointer(color_loc, 4, GL_FLOAT, False, 0, None)

# Allocate GPU memory for framebuffers (10 MB per buffer)
framebuffers = glGenFramebuffers(4)  # Allocate 4 framebuffers for more memory usage
for fb in framebuffers:
    glBindFramebuffer(GL_FRAMEBUFFER, fb)
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 1920, 1080, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0)

glBindFramebuffer(GL_FRAMEBUFFER, 0)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(program)
    glBindVertexArray(vao)
    glDrawArrays(GL_POINTS, 0, num_points)
    
    pygame.display.flip()
