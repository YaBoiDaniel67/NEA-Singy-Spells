import numpy as np

def RayCast(player, frame, world_map, pixels_per_degree, vertical_res, half_vertical_res, horizontal_res, sky, wall, depth, floor, fov):
    for i in range(horizontal_res): #loops through the amount of pixels horizontally across the screen
        x, y = player.xPos, player.yPos #creates a local copy of the player x and y coords
        player_redundant_ray_angle = np.deg2rad((i / pixels_per_degree) - (fov / 2)) #calculates the angle for the current ray
        ray_angle = player.rotation + player_redundant_ray_angle #calculates the angle of each ray + the players current rotation to get a resultant angle of rotation for the ray
        sin, cos, correctional_cos = np.sin(ray_angle), np.cos(ray_angle), np.cos(player_redundant_ray_angle) #saves the sin and cosine values of ray_angle so they dont have be constatnly recalculated, correctional_cos is used to correct the fish-eye distortion caused by raycasting
        if abs(sin) < 1e-6:
            sin = 1e-6 #prevents any divisions by 0 that could occur
        elif abs(cos) < 1e-6:
            cos = 1e-6 #prevents any divisions by 0 that could occur
        frame[i][:] = sky[int((np.rad2deg(player.rotation) + (i / pixels_per_degree) - (fov / 2)) * (sky.shape[0] / 360)) % sky.shape[0]][:] #calculates how far round in deg (0 - 359) this sky column is, maps this frame index to a given pixel column in the sky bitmap
        mapX, mapY = int(x), int(y) #saves the int of x and y to prevent recalculation, increasing efficiency
        tile_dist_x, tile_dist_y = abs(1 / cos), abs(1 / sin) #calculates how much distance a ray must cross to travel over one tile of space in x or y
        if cos > 0: #if ray is to the right
            step_x = 1 #step to the right
            side_dist_x = (mapX + 1 - player.xPos) * tile_dist_x #calculates distance of player from grid boundary
        else:
            step_x = -1 #step to the left
            side_dist_x = (player.xPos - mapX) * tile_dist_x #calculates distance of player from grid boundary
        if sin > 0: #if ray is pointing down the map
            step_y = 1 #step down
            side_dist_y = (mapY + 1 - player.yPos) * tile_dist_y #calculates distance of player from grid boundary
        else:
            step_y = -1 #step up
            side_dist_y = (player.yPos - mapY) * tile_dist_y #calculates distance of player form grid boundary
        while world_map[mapX][mapY] == 0: #repeats until a wall is found
            if side_dist_x < side_dist_y: #checks which grid boundary is closer
                side_dist_x += tile_dist_x #goes to next vertical boundary
                mapX += step_x #moves 1 tile left or right
                side = 0 #remebers last step was in x
            else: #if horizontal boundary is closer
                side_dist_y += tile_dist_y #goes to next horizontal boundary
                mapY += step_y #moves 1 tile up or down
                side = 1 #remebers last step was in y
        if side == 0: #if last step was x
            distance = abs((mapX - player.xPos + (1 - step_x) / 2) / cos) #calculates shortest distance from player to wall
        else:
            distance = abs((mapY - player.yPos + (1 - step_y) / 2) / sin) #calculates shortest distance from player to wall
        depth[i] = distance #adds the distance of this column to the corresponding index in depth
        x = player.xPos + distance * cos #sets new x, adding on scaled distance
        y = player.yPos + distance * sin #sets new y, adding on scaled distance
        height = int(vertical_res/ (distance * correctional_cos + 1e-6)) #calculates the height of the wall (how many available wall pixels / how far away the wall is * correctional_cos to correct fish eye distortion, add small value to prevent division by 0)
        half_height = int(height / 2) #saved to variable to prevent unnecessary calculations
        pix_x = int((x % 1) * 100) #calculates the x coord of the pixel on the bitmap (size 100 x 100)
        if x % 1 > 0.99 or x % 1 < 0.01: #checks if non-int parts of x are near a whole number
            pix_x = int((y % 1) * 100) #if x is near a whole number, the horizontal coord needs to be the y coord
        wall_top = max(0, half_vertical_res - half_height) #calculates the top of the wall
        wall_bottom = min(vertical_res, half_vertical_res + half_height) #calculate the bottom of the wall
        visible_height = wall_bottom - wall_top #calculates the height of a given wall that is on screen
        pix_column = np.arange(height) #creates an array of vertical points within wall
        shading = 0.2 + (height / half_vertical_res) #calculates the darkening of the wall, proportional to distance
        if shading > 1:
            shading = 1 #corrects shading for very close up walls
        pix_y = ((pix_column / height) * (wall.shape[1])).astype(int) #creates a decimal between 0 and 1, scales that to fit the wall texture, and saves the int of that. Creates a list of the specific texture points for this slice
        cut_wall_texture = max(0, half_height - half_vertical_res) #calculates how much of the texture is cut off the top of the screen
        frame[i][wall_top : wall_bottom] = shading * wall[pix_x][pix_y[cut_wall_texture : cut_wall_texture + visible_height]] #sets the RGB colour values of the specific column, using the wall bitmap
        pix_column = np.arange(half_vertical_res - half_height)  #creates an array of all pixels vertically across screen where floor needs to be filled
        distance = (half_vertical_res / (half_vertical_res - pix_column)) / correctional_cos #creates an array of each pixels distance from the player
        x, y = player.xPos + cos * distance, player.yPos + sin * distance #creates arrays of the x and y position of each pixel
        pix_x, pix_y = ((x % 1) * 100).astype(int), ((y % 1) * 100).astype(int) #calculates each pixel from the texture that is mapped to each specific point in the array, using the non-integer part of the x and y coords (for texture size 100 x 100 pixels)
        shading = 0.2 + 0.8 * (1 - (pix_column / half_vertical_res)) #calculates the amount of shade applied, so further away pixels appear darker, adding to sense of depth
        frame[i][vertical_res - pix_column - 1] = shading[:, None] * floor[pix_x, pix_y] #sets colour of the pixels using the RGB values of the pixel location on the floor bitmap
    return frame, depth