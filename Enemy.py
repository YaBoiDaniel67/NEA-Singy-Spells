import time
import numpy as np

class enemy:
    def __init__(self, damage, health, speed, size, x, y, animation_list, attack_rate, animation_rate, enemy_list):
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
        self.animation_rate = animation_rate
        self.last_attack_time = time.monotonic()
        self.attack_rate = attack_rate
        self.texture = self.animation_list[self.current_animation_index]
        enemy_list.append(self)

    def update_animation(self):
        if time.monotonic() - self.animation_rate > self.last_animation_update:
            self.last_animation_update = time.monotonic()
            self.current_animation_index = (self.current_animation_index + 1) % len(self.animation_list)
            self.texture = self.animation_list[self.current_animation_index]

    def special(self, on_screen_objects):
        return

    def attack(self, player):
        if np.sqrt((self.x - player.xPos) ** 2 + (self.y - player.yPos) ** 2) < 0.5:
            if time.monotonic() > self.last_attack_time + self.attack_rate:
                self.last_attack_time = time.monotonic()
                player.take_damage(self.damage)

    def take_damage(self, damage, enemy_list, on_screen_objects):
        self.health -= damage
        if self.health <= 0:
            enemy_list.remove(self)
            on_screen_objects.remove(self)


    def move(self, player, world_map):
        player_distance = np.sqrt((self.x - player.xPos) ** 2 + (self.y - player.yPos) ** 2)
        ray_angle = np.arctan2(player.yPos - self.y, player.xPos - self.x)
        sin, cos = np.sin(ray_angle), np.cos(ray_angle) #saves the sin and cosine values of ray_angle so they dont have be constatnly recalculated
        if sin == 0:
            sin = 1e-6 #prevents any divisions by 0 that could occur
        elif cos == 0:
            cos = 1e-6 #prevents any divisions by 0 that could occur
        mapX, mapY = int(self.x), int(self.y) #saves the int of x and y to prevent recalculation, increasing efficiency
        tile_dist_x, tile_dist_y = abs(1 / cos), abs(1 / sin) #calculates how much distance a ray must cross to travel over one tile of space in x or y
        if cos > 0: #if ray is to the right
            step_x = 1 #step to the right
            side_dist_x = (mapX + 1 - self.x) * tile_dist_x #calculates distance of enemy from grid boundary
        else:
            step_x = -1 #step to the left
            side_dist_x = (self.x - mapX) * tile_dist_x #calculates distance of enemy from grid boundary
        if sin > 0: #if ray is pointing down the map
            step_y = 1 #step down
            side_dist_y = (mapY + 1 - self.y) * tile_dist_y #calculates distance of enemy from grid boundary
        else:
            step_y = -1 #step up
            side_dist_y = (self.y - mapY) * tile_dist_y #calculates distance of enemy form grid boundary
        clear_path = False
        side = 0
        while True: #repeats until a wall is found
            if side == 0: #if last step was x
               distance = abs((mapX - self.x + (1 - step_x) / 2) / cos) #calculates shortest distance from enemy to wall
            else:
               distance = abs((mapY - self.y + (1 - step_y) / 2) / sin) #calculates shortest distance from enemy to wall
            if distance >= player_distance:
                clear_path = True
                break
            if not world_map[mapX][mapY] == 0:
                break
            if side_dist_x < side_dist_y: #checks which grid boundary is closer
                side_dist_x += tile_dist_x #goes to next vertical boundary
                mapX += step_x #moves 1 tile left or right
                side = 0 #remebers last step was in x
            else: #if horizontal boundary is closer
                side_dist_y += tile_dist_y #goes to next horizontal boundary
                mapY += step_y #moves 1 tile up or down
                side = 1 #remebers last step was in y
        if clear_path and np.sqrt((self.x - player.xPos) ** 2 + (self.y - player.yPos) ** 2) > 0.5:
            self.x += ((player.xPos - self.x) / player_distance) * self.speed
            self.y += ((player.yPos - self.y) / player_distance) * self.speed