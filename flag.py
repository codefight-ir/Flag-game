# -*- coding: utf-8 -*-
import random
from contextlib import contextmanager
from battlefield.engine import TurnEngine


class Flag(TurnEngine):
    turns = 200

    def __init__(self, *args):
        super(Flag, self).__init__(*args)
        self.map = Map(*self.robots)
        self.map.populate()

    def step(self, robot):
        with self.map.view_as(robot):
            result = yield self.map.draw()
            result = self.map.move(robot, result)
            if result:
                if result == '$':
                    robot.score += 1
                elif result == '!':
                    robot.score -= 1

    def end(self):
        return {i.name: i.score for i in self.robots}


class Map:
    FLAG = '$'
    BOMB = '!'
    WALL = '#'

    def __init__(self, robot1, robot2):
        self.width = random.randrange(20, 50, 2)
        self.height = random.randrange(20, 50, 2)
        self.transition = random.choice(['V', 'H', 'C'])
        self._map = {}
        for i in range(self.width):
            for j in range(self.height):
                self._map[i, j] = ' '
        self.robot1 = robot1
        self.robot2 = robot2
        self.robot1.position = (random.randint(0, self.width - 1),
                                random.randint(0, self.height - 1))
        self.robot2.position = self.mirror(self.robot1.position)
        self._map[self.robot1.position] = 'R'
        self._map[self.robot2.position] = 'R'

    def mirror(self, point):
        if self.transition == 'V':
            return self.width - 1 - point[0], point[1]
        elif self.transition == 'H':
            return point[0], self.height - 1 - point[1]
        elif self.transition == 'C':
            return self.width - 1 - point[0], self.height - 1 - point[1]

    @contextmanager
    def view_as(self, robot):
        self.set('Y', [robot.position])
        yield
        self.set('R', [robot.position])

    def draw(self):
        result = ''
        for j in range(self.height):
            for i in range(self.width):
                result += self._map[i, j]
            result += '\n'
        return result

    def populate(self):
        clean_env = (list(self.neighbours(self.robot1.position).values())
                     + list(self.neighbours(self.robot2.position).values()))
        wall_count = (self.width * self.height) // 10
        while wall_count >= 0:
            p = (random.randint(0, self.width - 1),
                 random.randint(0, self.height - 1))
            if self._map[p] != ' ' or p in clean_env:
                continue
            mp = self.mirror(p)
            self._map[p] = self.WALL
            self._map[mp] = self.WALL
            wall_count -= 2

        flag_count = (self.width * self.height) // 20
        while flag_count >= 0:
            p = (random.randint(0, self.width - 1),
                 random.randint(0, self.height - 1))
            if self._map[p] != ' ' or p in clean_env:
                continue
            mp = self.mirror(p)
            self._map[p] = self.FLAG
            self._map[mp] = self.FLAG
            flag_count -= 2

        bomb_count = (self.width * self.height) // 20
        while bomb_count >= 0:
            p = (random.randint(0, self.width - 1),
                 random.randint(0, self.height - 1))
            if self._map[p] != ' ' or p in clean_env:
                continue
            mp = self.mirror(p)
            self._map[p] = self.BOMB
            self._map[mp] = self.BOMB
            bomb_count -= 2

    def neighbours(self, point):
        return {'UL': (point[0] - 1, point[1] - 1),
                'L': (point[0] - 1, point[1]),
                'DL': (point[0] - 1, point[1] + 1),
                'U': (point[0], point[1] - 1),
                'D': (point[0], point[1] + 1),
                'UR': (point[0] + 1, point[1] - 1),
                'R': (point[0] + 1, point[1]),
                'DR': (point[0] + 1, point[1] + 1)}

    def set(self, value, points):
        for point in points:
            self._map[point] = value

    def move(self, robot, to):
        new_pos = self.neighbours(robot.position).get(to)
        val = self._map.get(new_pos)
        if val and val != '#' and val != 'R':
            self.set(' ', [robot.position])
            robot.position = new_pos
            return val

    def set_border(self, borders, value):
        if 'TOP' in borders:
            for i in range(self.width):
                self._map[i, 0] = value
        if 'RIGHT' in borders:
            for j in range(self.height):
                self._map[self.width - 1, j] = value
        if 'BOTTOM' in borders:
            for i in range(self.width):
                self._map[i, self.height - 1] = value
        if 'LEFT' in borders:
            for j in range(self.height):
                self._map[0, j] = value
            pass
