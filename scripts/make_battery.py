"""Regenerate the current LAVA II battery JSON and authored wrapper textures."""
from refine_battery import component, textures

if __name__ == "__main__":
    textures()
    component()
