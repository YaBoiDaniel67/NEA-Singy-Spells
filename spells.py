import pygame
import numpy as np
import Variables as var

spells = {"Fireball": {
          "melody_ID": 0,}
}

def get_ray_angle():
   mouseX, mouseY = pygame.mouse.get_pos()
   redundant_ray_angle = np.deg2rad((mouseX / var.pixels_per_degree) - 30)
   projectile_angle = var.player_rotation + redundant_ray_angle
   return projectile_angle

class Fireball:
  def __init__(self):
     self.damage = 20.0
     self.speed = 1.0
     self.x = var.xPos
     self.y = var.yPos
     self.ray_angle = get_ray_angle()

def find_spell():
    if len(var.potential_melody) > 0:
      for spell_name, spell in spells.items():
          if spell["melody_ID"] == var.potential_melody[-1]:
             cast_spell(spell_name)

def cast_spell(spell_name):
   match spell_name:
      case "Fireball":
         spawn_fireball()

def spawn_fireball():
   var.projectiles.append(Fireball())

def draw_on_screen(frame, object):
   angle_to_projectile_from_player = np.arctan2(object.y - var.yPos, object.x - var.xPos)
   redundant_angle = angle_to_projectile_from_player - var.player_rotation
   redundant_angle = (redundant_angle + np.pi) % (2 * np.pi) - np.pi
   screenX = int((np.rad2deg(redundant_angle) + 30) * var.pixels_per_degree)
   if 0 < screenX < var.horizontal_res:
    distance = np.sqrt((object.x - var.xPos) ** 2 + (object.y - var.yPos)** 2)
    height = int((var.vertical_res / (distance * np.cos(redundant_angle) + 1e-6)) * 0.2)
    top, bottom = max(0, var.halfvertical_res - height // 2), min(var.vertical_res, var.halfvertical_res + height // 2)

   return frame