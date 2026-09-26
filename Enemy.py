import time
import numpy as np

class enemy:
    def __init__(self, damage, health, speed, size, x, y, animation_list, attack_rate):
        self.damage = damage
        self.health = health
        self.speed = speed
        self.size = size
        self.type = "enemy"
        self.x = x
        self.y= y
        self.animation_list = animation_list
        self.current_animation_index = 0
        self.last_animation_update = time.monotonic()
        self.last_attack_time = time.monotonic()
        self.attack_rate = attack_rate
        self.texture = self.animation_list[self.current_animation_index]

    def update_animation(self):
        if time.monotonic() / self.speed > self.last_animation_update:
            self.current_animation_index = (self.current_animation_index + 1) % len(self.animation_list)
            self.texture = self.animation_list[self.current_animation_index]

    def special(self, on_screen_objects):
        return

    def attack(self, player):
        if np.sqrt((self.x - player.xPos) ** 2 + (self.y - player.yPos) ** 2) < 0.5:
            if time.monotonic() > self.last_attack_time + self.attack_rate:
                self.last_attack_time = time.monotonic()
                player.take_damage(self.damage)

    def move(self, player, world_map):
        