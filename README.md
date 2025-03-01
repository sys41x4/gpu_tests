# Want to always use gpu hardware rendering use below variable to enable gpu  rendering by default
```bash
export LIBGL_ALWAYS_SOFTWARE=0
```
Enable noveau module to be loaded at boot
```
echo "nouveau" | sudo tee -a /etc/modules
```
# As now nvidia properitery driver isn't supported for older gpu cards
# you need to use noveau drivers only

# Enable noveau drivers in boot
file_name: /etc/default/grub
```text
# If you change this file, run 'update-grub' afterwards to update
# /boot/grub/grub.cfg.
# For full documentation of the options in this file, see:
#   info -f grub -n 'Simple configuration'

GRUB_DEFAULT=0
GRUB_TIMEOUT_STYLE=hidden
GRUB_TIMEOUT=0
GRUB_DISTRIBUTOR=`( . /etc/os-release; echo ${NAME:-Ubuntu} ) 2>/dev/null || echo Ubuntu`
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nouveau.modeset=1"
GRUB_CMDLINE_LINUX=""
...

# Check if there is noveau enable in blacklist if so comment it out on that file
The File is usually /etc/modprobe.d/nvidia-installer-disable-nouveau.conf
```
grep -i nouveau /etc/modprobe.d/*
```

```
# Checking video memory usage
glxinfo | grep -i "Video memory"
Video memory: 2030MB
Dedicated video memory: 2030 MB
Currently available dedicated video memory: 1624 MB


# Testing if the gpu is using 
1. run the sensors in one side for monitoring
```bash
>>> watch sensors
```
2. get rendering providers
```bash
>>> xrandr --listproviders
Providers: number : 1
Provider 0: id: 0x43 cap: 0x9, Source Output, Sink Offload crtcs: 2 outputs: 3 associated providers: 0 name:modesetting
```
```bash
>>> lspci -nnk | grep -iA2 vga 
03:00.0 VGA compatible controller [0300]: NVIDIA Corporation GF119 [GeForce GT 610] [10de:104a] (rev a1)
	Subsystem: NVIDIA Corporation GF119 [GeForce GT 610] [10de:0915]
	Kernel driver in use: nouveau
```

With Vsync run below application and watch for memory and temperature changes in glxinfo and sensors
This will make sure that the gpu is working
```glmark2```

Using raw flames other than vsync | These effects will all be seen in sensors and glxinfo
```
LIBGL_DEBUG=verbose vblank_mode=0 glxgears
```

```
DRI_PRIME=1 __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nouveau __VK_LAYER_NV_optimus=NVIDIA_only glxgear
```

Use below python script to check for availability and task execution through gpu

```python
import pygame
from pygame.locals import *
import OpenGL.GL as gl
import subprocess

def check_gpu_opengl():
    """Check which GPU OpenGL is using"""
    pygame.init()
    pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)  # Create OpenGL context

    try:
        renderer = gl.glGetString(gl.GL_RENDERER).decode()
        vendor = gl.glGetString(gl.GL_VENDOR).decode()
        version = gl.glGetString(gl.GL_VERSION).decode()

        print(f"✅ OpenGL Renderer: {renderer}")
        print(f"✅ OpenGL Vendor: {vendor}")
        print(f"✅ OpenGL Version: {version}")

        return renderer
    except Exception as e:
        print(f"❌ OpenGL check failed: {e}")
        return None
    finally:
        pygame.quit()  # Close the OpenGL context

def check_xrandr():
    """Check GPU providers using xrandr"""
    try:
        result = subprocess.run(["xrandr", "--listproviders"], capture_output=True, text=True)
        print("🖥  xrandr Output:\n" + result.stdout)
        return result.stdout
    except Exception as e:
        print(f"❌ Failed to run xrandr: {e}")
        return None

def check_nvidia_smi():
    """Check if NVIDIA GPU is detected"""
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        print("🎮 NVIDIA GPU Detected:\n" + result.stdout)
        return result.stdout
    except FileNotFoundError:
        print("❌ NVIDIA-SMI not found. Is the NVIDIA driver installed?")
    except Exception as e:
        print(f"❌ Failed to run nvidia-smi: {e}")
    return None

if __name__ == "__main__":
    print("\n🔍 Checking GPU availability...\n")

    # Check OpenGL Renderer
    renderer = check_gpu_opengl()

    # Check GPU providers with xrandr
    check_xrandr()

    # Check if NVIDIA GPU is available
    check_nvidia_smi()

    # Final summary
    if renderer and "nouveau" in renderer.lower():
        print("\n🚨 System is using the Nouveau driver. PRIME offloading may not work correctly.")
    elif renderer:
        print("\n✅ GPU is being used for OpenGL rendering.")
    else:
        print("\n❌ No GPU detected for OpenGL rendering.")
```


# Run a high intense gpu tasks to notice significant changes in glxinfo memory utilization changes

```python
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
```

##### Stress test gpu usage using python script | Below script will provide a memory difference of7mb in gpu memory

```python
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
```


##### Stress test gpu usage using python script | Below script will provide a memory difference of 40mb in gpu memory 
Remember below command is quite resource intensive for gpu and may freeze your monitor

```python
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
num_points = 10_000  # More points to consume GPU memory
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

```
