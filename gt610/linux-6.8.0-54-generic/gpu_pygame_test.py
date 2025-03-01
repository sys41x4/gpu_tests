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
