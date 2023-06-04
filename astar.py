# written by Anmol Gulati
import pygame
import math
from queue import PriorityQueue

WIDTH = 800  # square
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Visualizer")

RED = (255, 0, 0)  # already looked at node
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)  # not yet looked at node, can be visited
BLACK = (0, 0, 0)  # barrier, algorithm has to avoid
PURPLE = (128, 0, 128)  # path
ORANGE = (255, 165, 0)  # start node
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def getPosition(self):  # row column order
        return self.row, self.col

    def isClosed(self):  # update node to red meaning already looked at
        return self.color == RED

    def isOpen(self):
        return self.color == GREEN

    def isBarrier(self):
        return self.color == BLACK

    def isStart(self):
        return self.color == ORANGE

    def isEnd(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def updateNeighbours(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].isBarrier():  # Down
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier():  # Up
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].isBarrier():  # Right
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].isBarrier():  # Left
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


# in A* alg, h(n) gives shortest estimated distance of node N to end node
def h(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return abs(x2 - x1) + abs(y2 - y1)


def reconstruct_path(cameFrom, current, draw):
    while current in cameFrom:
        current = cameFrom[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    openSet = PriorityQueue()
    openSet.put((0, count, start))
    cameFrom = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.getPosition(), end.getPosition())

    openSet_hash = {start}

    while not openSet.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = openSet.get()[2]
        openSet_hash.remove(current)

        if current == end:
            reconstruct_path(cameFrom, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                cameFrom[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.getPosition(), end.getPosition())
                if neighbor not in openSet_hash:
                    count += 1
                    openSet.put((f_score[neighbor], count, neighbor))
                    openSet_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()


def makeGrid(rows, width):
    grid = []
    width_of_cubes = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, width_of_cubes, rows)
            grid[i].append(node)

    return grid


def drawGrid(win, rows, width):
    width_of_cubes = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * width_of_cubes), (width, i * width_of_cubes))  # draw horizontal lines
        for j in range(rows):  # draw vertical lines
            pygame.draw.line(win, GREY, (j * width_of_cubes, 0), (j * width_of_cubes, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    drawGrid(win, rows, width)
    pygame.display.update()


def squareClicked(position, rows, width):
    width_of_cubes = width // rows
    y, x = position
    col = x // width_of_cubes
    row = y // width_of_cubes

    return row, col


def main(win, width):
    ROWS = 50
    grid = makeGrid(ROWS, width)
    start = None
    end = None
    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # left mouse button
                pos = pygame.mouse.get_pos()
                row, col = squareClicked(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:  # cant have start and end in same place
                    start = node
                    start.make_start()
                elif not end and node != start:  # cant have start and end in same place
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # right mouse button
                pos = pygame.mouse.get_pos()
                row, col = squareClicked(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.updateNeighbours(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = makeGrid(ROWS, width)

    pygame.quit()  # stop game


main(WIN, WIDTH)
