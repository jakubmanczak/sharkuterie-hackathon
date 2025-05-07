from enum import Enum
from src.common import load_texture

class TileType(Enum):
    CARPET = {
        "texture_path": "./assets/textures/dywan.png",
        "wall_collision": False,
        "spawn_enemies": False
    }
    WALL01 = {
        "texture_path": "./assets/textures/sciana.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL_CUL = {
        "texture_path": "./assets/textures/sciana_cul.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL_L = {
        "texture_path": "./assets/textures/sciana_boczna_left.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL_CLL = {
        "texture_path": "./assets/textures/sciana_cll.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL_CUR = {
        "texture_path": "./assets/textures/sciana_cur.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL_R = {
        "texture_path": "./assets/textures/sciana_boczna_right.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL_CLR = {
        "texture_path": "./assets/textures/sciana_clr.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL_DOWN = {
        "texture_path": "./assets/textures/sciana_dol.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL_DOOR = {
        "texture_path": "./assets/textures/drzwi.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    PAPERSTACK = {
        "texture_path": "./assets/textures/papers.png",
        "wall_collision": False,
        "spawn_enemies": False
    }
    DESKCLEAN = {
        "texture_path": "./assets/textures/stol.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    DESKWITHPAPERS = {
        "texture_path": "./assets/textures/stol_PAPIERy.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    TABLE_BL = {
        "texture_path": "./assets/textures/table_p_bl.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    TABLE_BR = {
        "texture_path": "./assets/textures/table_br.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    TABLE_TL = {
        "texture_path": "./assets/textures/table_p_tl.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    TABLE_TR = {
        "texture_path": "./assets/textures/table_tr.png",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL02 = {
        "texture_path": "./assets/textures/lvl3/IMG_4666.PNG",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL02_CUL = {
        "texture_path": "./assets/textures/lvl3/IMG_4665.PNG",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL02_L = {
        "texture_path": "./assets/textures/lvl3/IMG_4669.PNG",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL02_CLL = {
        "texture_path": "./assets/textures/lvl3/IMG_4664.PNG",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL02_CUR = {
        "texture_path": "./assets/textures/lvl3/IMG_4662.PNG",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL02_R = {
        "texture_path": "./assets/textures/lvl3/IMG_4667.PNG",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL02_CLR = {
        "texture_path": "./assets/textures/lvl3/IMG_4663.PNG",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL02_DOWN = {
        "texture_path": "./assets/textures/lvl3/IMG_4668.PNG",
        "wall_collision": True,
        "spawn_enemies": False
    }
    WALL02_DOOR = {
        "texture_path": "./assets/textures/lvl3/IMG_4674.PNG",
        "wall_collision": True,
        "spawn_enemies": False
    }

    def __init__(self, data):
        self.texture_path = data["texture_path"]
        self.wall_collision = data["wall_collision"]
        self.spawn_enemies = data["spawn_enemies"]

    @property
    def texture(self):
        return load_texture(self.texture_path)
