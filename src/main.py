import sys
import contextlib
import math
import os

"""
simply: dont show pygame message
"""
with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame

class Player:
    def __init__(self, x, y, dirX, dirY, planeX, planeY, worldMap, fov=60):
        self.posX = x
        self.posY = y
        self.dirX = dirX
        self.dirY = dirY
        self.planeX = planeX
        self.planeY = planeY
        self.worldMap = worldMap
        self.set_fov(fov)

    def set_fov(self, fov):
        self.fov = fov
        if self.fov < 1:
            self.fov = 1
        if self.fov > 180:
            self.fov = 180
        rad_fov = math.radians(self.fov / 2)
        self.planeX = self.dirY * math.tan(rad_fov)
        self.planeY = -self.dirX * math.tan(rad_fov)

    def move(self, direction):
        moveSpeed = 0.1
        newPosX = self.posX
        newPosY = self.posY

        if direction == "FORWARD":
            newPosX += self.dirX * moveSpeed
            newPosY += self.dirY * moveSpeed
        elif direction == "BACKWARD":
            newPosX -= self.dirX * moveSpeed
            newPosY -= self.dirY * moveSpeed
        elif direction == "LEFT":
            self.rotate(0.1)
        elif direction == "RIGHT":
            self.rotate(-0.1)

        if self.is_walkable(newPosX, newPosY):
            self.posX = newPosX
            self.posY = newPosY

    def is_walkable(self, x, y):
        mapX = int(x)
        mapY = int(y)
        return self.worldMap[mapX][mapY] == 0

    def rotate(self, angle):
        oldDirX = self.dirX
        self.dirX = self.dirX * math.cos(angle) - self.dirY * math.sin(angle)
        self.dirY = oldDirX * math.sin(angle) + self.dirY * math.cos(angle)
        oldPlaneX = self.planeX
        self.planeX = self.planeX * math.cos(angle) - self.planeY * math.sin(angle)
        self.planeY = oldPlaneX * math.sin(angle) + self.planeY * math.cos(angle)

class Raycaster:
    def __init__(self, screen, mapData, player):
        self.screen = screen
        self.map = mapData
        self.player = player

    def draw_line(self, x1, y1, x2, y2, color):
        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2))

    def render(self):
        screenWidth, screenHeight = self.screen.get_size()
        for x in range(screenWidth):
            cameraX = 2 * x / float(screenWidth) - 1
            rayDirX = self.player.dirX + self.player.planeX * cameraX
            rayDirY = self.player.dirY + self.player.planeY * cameraX
            mapX = int(self.player.posX)
            mapY = int(self.player.posY)

            deltaDistX = abs(1 / (rayDirX + 1e-10))
            deltaDistY = abs(1 / (rayDirY + 1e-10))

            if rayDirX < 0:
                stepX = -1
                sideDistX = (self.player.posX - mapX) * deltaDistX
            else:
                stepX = 1
                sideDistX = (mapX + 1.0 - self.player.posX) * deltaDistX

            if rayDirY < 0:
                stepY = -1
                sideDistY = (self.player.posY - mapY) * deltaDistY
            else:
                stepY = 1
                sideDistY = (mapY + 1.0 - self.player.posY) * deltaDistY

            hit = 0
            while hit == 0:
                if sideDistX < sideDistY:
                    sideDistX += deltaDistX
                    mapX += stepX
                    side = 0
                else:
                    sideDistY += deltaDistY
                    mapY += stepY
                    side = 1

                if 0 <= mapX < len(self.map) and 0 <= mapY < len(self.map[0]) and self.map[mapX][mapY] > 0:
                    hit = 1
                elif mapX < 0 or mapX >= len(self.map) or mapY < 0 or mapY >= len(self.map[0]):
                    break

            if hit == 1:
                if side == 0:
                    perpWallDist = (mapX - self.player.posX + (1 - stepX) / 2) / (rayDirX + 1e-10)
                else:
                    perpWallDist = (mapY - self.player.posY + (1 - stepY) / 2) / (rayDirY + 1e-10)

                lineHeight = int(screenHeight / (perpWallDist + 1e-10))
                drawStart = -lineHeight // 2 + screenHeight // 2
                if drawStart < 0:
                    drawStart = 0
                drawEnd = lineHeight // 2 + screenHeight // 2
                if drawEnd >= screenHeight:
                    drawEnd = screenHeight - 1

                if self.map[mapX][mapY] == 1:
                    color = (216, 191, 216) if side == 0 else (221, 160, 221)
                    self.draw_line(x, drawStart, x, drawEnd, color)
                else:
                    raise NotImplementedError

class Game:
    def __init__(self, map_file=None):
        pygame.init()
        self.debug = True
        self.screenWidth = 800
        self.screenHeight = 600
        self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        pygame.display.set_caption("penguindoo raycaster engine")
        self.clock = pygame.time.Clock()
        self.mapWidth = 10
        self.mapHeight = 10
        self.tileSize = 64
        self.minimapSize = 200
        self.minimapScale = self.minimapSize // self.mapWidth
        self.wallColor = (0, 0, 0)
        self.spaceColor = (255, 255, 255)
        self.minimap = pygame.Surface((self.minimapSize, self.minimapSize))
        if map_file:
            self.worldMap = self.load_map(map_file)
        else:
            self.worldMap = [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                [1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 1, 1, 1, 0, 1],
                [1, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            ]

        self.player = Player(3.0, 3.0, -1.0, 0.0, 0.0, 0.66, self.worldMap)
        self.raycaster = Raycaster(self.screen, self.worldMap, self.player)
    
    def load_map(self, map_file):
        with open(map_file, 'r') as f:
            map_data = [list(map(int, line.strip())) for line in f.readlines()]
        return map_data

    def render_minimap(self):
        self.minimap.fill((0,0,0))
        for y in range(self.mapHeight):
            for x in range(self.mapWidth):
                cell_color = self.wallColor if self.worldMap[y][x] else self.spaceColor
                pygame.draw.rect(self.minimap, cell_color, (x * self.minimapScale, y * self.minimapScale, self.minimapScale, self.minimapScale))

        player_x = max(0, min(int(self.player.posX * self.minimapScale), self.mapWidth * self.minimapScale - 4))
        player_y = max(0, min(int(self.player.posY * self.minimapScale), self.mapHeight * self.minimapScale - 4))
        pygame.draw.rect(self.minimap, (255, 0, 0), (player_y, player_x, 4, 4))

    def run(self):
        isRunning = True
        target_fps = 30
        while isRunning:
            self.clock.tick(target_fps)
            fps = int(self.clock.get_fps())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    isRunning = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.player.move("FORWARD")
            if keys[pygame.K_s]:
                self.player.move("BACKWARD")
            if keys[pygame.K_a]:
                self.player.move("LEFT")
            if keys[pygame.K_d]:
                self.player.move("RIGHT")
            if keys[pygame.K_q]:
                self.player.set_fov(self.player.fov - 1)
            if keys[pygame.K_e]:
                self.player.set_fov(self.player.fov + 1)

            self.screen.fill((0, 0, 0))
            self.render_minimap()
            self.raycaster.render()

            self.screen.blit(self.minimap, (self.screenWidth - self.minimapSize, 0))
            if (self.debug == True):
                self.render_text(f"FPS: {fps}", 10, 10, (255, 255, 255))
                self.render_text(f"FOV: {self.player.fov}", 10, 40, (255, 255, 255))
                self.render_text(f"posX: {self.player.posX}", 10, 70, (255, 255, 255))
                self.render_text(f"posY: {self.player.posY}", 10, 100, (255, 255, 255))
            pygame.display.flip()

        pygame.quit()

    def render_text(self, text, x, y, color):
        font = pygame.font.Font(os.path.join("assets", "arial.ttf"), 24)
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        map_file = sys.argv[1]
        game = Game(map_file)
    else:
        game = Game()
    game.debug=False
    game.run()
else:
    print("Raycaster 0.1.0\nAuthor: `windowsbuild3r`\nPlease give credit!")