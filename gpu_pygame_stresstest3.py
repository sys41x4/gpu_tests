import pygame
from OpenGL.GL import *
import numpy as np

pygame.init()
display = (800, 600)
pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
glClearColor(0, 0, 0, 1)

# Create a shader program
vertex_shader = """
#version 130
in vec2 position;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
}
"""

fragment_shader = """
#version 130
out vec4 FragColor;
void main() {
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red color
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

# Generate random points
vertices = np.random.uniform(-1, 1, (100000, 2)).astype(np.float32)

vao = glGenVertexArrays(1)
glBindVertexArray(vao)

vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

position = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(position)
glVertexAttribPointer(position, 2, GL_FLOAT, False, 0, None)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(program)
    glBindVertexArray(vao)
    glDrawArrays(GL_POINTS, 0, len(vertices))
    
    pygame.display.flip()
