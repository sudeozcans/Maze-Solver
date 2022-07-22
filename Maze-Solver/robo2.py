import json
import numpy as np
import random
class Robo(object):
    class Kare(object):
        def __init__(self):
            self.value=0

    def __init__(self,moves):
        self.first_x, self.first_y=0,0
        self.x, self.y=0,0
        self.last_x,self.last_y=0,0
        self.rotation=0
        self.movement=0
        self.moves=moves
        self.sensors = []
        self.is_beginning = True
        self.is_reversing = False

        self.dir="up"
        self.path_dict="path.json"
        open(self.path_dict, "w").close()

        self.dict_rotation={'up': ['left', 'right'],
                            'right': ['up', 'down'],
                            'down': ['right', 'left'],
                            'left': ['down', 'up']}

        self.vec={'up': [0, 1],
                'right': [1, 0],
                'down': [0, -1],
                'left': [-1, 0]}

        self.opposite = {'up': 'down',
                        'right': 'left',
                        'down': 'up',
                        'left': 'right'}
        self.dir_to_rotation = {
        dir: {directions[0]: -90, directions[1]: 90}
        for dir, directions in self.dict_rotation.items()}
        
        self.rot_matrices = {'left': np.array([(0, 1), (-1, 0)]),
                            'forward': np.array([(1, 0), (0, 1)]),
                            'right': np.array([(0, -1), (1, 0)])}
        self.wall = {'up': 1,
                    'right': 2,
                    'down': 4,
                    'left': 8}

        self.maze_map = [[0 for _ in range(moves)] for _ in range(moves)]
        self.path_map = [[self.Kare() for _ in range(moves)] for _ in range(moves)]

        # self.policy_grid = [['' for _ in range(self.moves)] for _ in
        #                     range(self.moves)]

        self.UNVISITED = 0
        self.VISITED = 1
        self.DOUBLE_VISITED = 2

    def next_move(self,sensors):
        self.rotation = 0
        self.movement = 0
        self.sensors = sensors

        self.explore()
        self.log_location()
        self.rotate()
        self.move(self.movement)

        return self.rotation, self.movement

    def reverse(self):
        self.is_reversing = True
        self.rotation = 90

    def check_open_directions(self):
        open_directions=[]
        if self.sensors[0] > 0:
            open_directions.append('left')
        if self.sensors[1] > 0:
            open_directions.append('forward')
        if self.sensors[2] > 0:
            open_directions.append('right')
        return open_directions

    def get_paths(self, open_directions, value):
        movement_vec = np.array(self.vec[self.dir])

        paths = []
        for direction in open_directions:
            dir_vec = np.dot(movement_vec, self.rot_matrices[direction])
            next_loc = (self.x + dir_vec[0], self.y + dir_vec[1])
            if (not (next_loc[0], next_loc[1]) == (
            self.last_x, self.last_y) and
                    self.path_is(value, next_loc[0], next_loc[1])):
                paths.append(direction)

        return paths

    def mark_path(self, new_value=None):
        if new_value is None:
            self.path_map[self.x][self.y].value += 1
        else:
            self.path_map[self.x][self.y].value = new_value

    def path_is(self, value, x=None, y=None):
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        return self.path_map[x][y].value == value


    def follow_path(self, direction):
        if direction == "left":
            self.rotation = -90
            self.movement = 1
        elif direction == "forward":
            self.rotation = 0
            self.movement = 1
        elif direction == "right":
            self.rotation = 90
            self.movement = 1

    def rotate(self):
        if type(self.rotation) is str:
            return
        
        if self.rotation == -90:
            self.dir = self.dict_rotation[self.dir][0]
        elif self.rotation == 90:
            self.dir = self.dict_rotation[self.dir][1]
        elif self.rotation == 0:
            pass

    def movement_allowed(self):
        if self.rotation == -90:
            return self.sensors[0] > 0
        elif self.rotation == 90:
            return self.sensors[2] > 0
        elif self.rotation == 0:
            return self.sensors[1] > 0
        else:
            return False

    def move(self, distance):
        if type(distance) is str:
            return
        
        self.last_x, self.last_y = self.x, self.y
        while distance > 0:
            if self.movement_allowed():
                if self.dir == "up":
                    self.y += 1
                elif self.dir == "down":
                    self.y -= 1
                elif self.dir == "right":
                    self.x += 1
                elif self.dir == "left":
                    self.x -= 1

                distance -= 1

            else:
                distance = 0
    # def end_exploration(self):
        
    #     self.dir = "up"
    #     self.x, self.y = self.first_x, self.first_y

    #     self.mode = "search"

    #     # Set the reset signals
    #     self.movement = "Reset"
    #     self.rotation = "Reset"

    def log_location(self):
        with open(self.path_dict, 'a') as file_object:
            out_data = [self.x, self.y, self.path_map[self.x][self.y].value,
                        self.dir]
            json.dump(out_data, file_object)
            file_object.write('\n')



    def update_map(self, open_directions):
        movement_vec = np.array(self.vec[self.dir])

        for direction in open_directions:
            global_dir = None
            if direction == 'left':
                global_dir = self.dict_rotation[self.dir][0]
            elif direction == 'right':
                global_dir = self.dict_rotation[self.dir][1]
            elif direction == 'forward':
                global_dir = self.dir

            wall_value = self.wall[global_dir]
            self.maze_map[self.x][self.y] |= wall_value
            dir_vec = np.dot(movement_vec, self.rot_matrices[direction])
            wall_value = self.wall[self.opposite[global_dir]]
            self.maze_map[self.x + dir_vec[0]][
                self.y + dir_vec[1]] |= wall_value

    def explore(self):
        if self.is_beginning:
            self.is_beginning = False

        if self.is_reversing:
            self.rotation = 90
            self.movement = 1
            self.is_reversing = False
            return

        open_directions = self.check_open_directions()
        self.update_map(open_directions)

        if len(open_directions) == 0:
            self.reverse()
            self.mark_path(self.DOUBLE_VISITED)

        elif len(open_directions) == 1:
            self.follow_path(open_directions[0])
            self.mark_path()

        elif len(open_directions) > 1:
            if self.path_is(self.UNVISITED):
                unvisited_paths = self.get_paths(open_directions, self.UNVISITED)
                if len(unvisited_paths) > 0:
                    self.follow_path(random.choice(unvisited_paths))
                    self.mark_path()

                else:
                    self.reverse()
                    self.mark_path(self.DOUBLE_VISITED)

            elif self.path_is(self.VISITED):
                if self.path_is(self.DOUBLE_VISITED, self.last_x, self.last_y):
                    unvisited_paths = self.get_paths(open_directions, self.UNVISITED)
                    visited_paths = self.get_paths(open_directions, self.VISITED)
                    if len(unvisited_paths) > 0:
                        self.follow_path(random.choice(unvisited_paths))
                    else:
                        self.follow_path(random.choice(visited_paths))
                        self.mark_path()
                else:
                    self.reverse()