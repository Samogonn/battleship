from random import randrange
from time import sleep

class BoardException(Exception):
    pass

class BoardOutException(BoardException):

    def __str__(self):
        return 'Вы стреляете мимо доски. Попробуйте еще раз.'


class BoardUsedException(BoardException):

    def __str__(self):
        return 'Вы уже стреляли в эту клетку. Попробуйте еще раз.'

class BoardWrongShipException(BoardException):
    pass


class Dot():

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship():
    def __init__(self, l, bow, o):
        self.l = l
        self.lives = l
        self.bow = bow
        self.o = o

    @property
    def dots(self):
        dots = [Dot(self.bow.x, self.bow.y)]

        for i in range(self.l - 1):
            if self.o:
                dots.append(Dot(dots[i].x + 1, dots[i].y))
            else:
                dots.append(Dot(dots[i].x, dots[i].y + 1))
        return dots

    def shooten(self, shot):
        return shot in self.dots


class Board():

    def __init__(self, size=6, hid=False):
        self.size = size
        self.hid = hid

        self.field = [['O'] * size for _ in range(size)]

        self.ships = []
        self.busy = []

        self.count = 0

    # def __str__(self):
    #     res = ''
    #     res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
    #     for i, row in enumerate(self.field):
    #         res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'

    #     if self.hid:
    #         res = res.replace('■', 'O')
    #     return res

    def out(self, dot):
        return dot.x not in range(self.size) or dot.y not in range(self.size)

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException
        for dot in ship.dots:
            self.field[dot.x][dot.y] = '■'
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                dot = Dot(d.x + dx, d.y + dy)
                if not self.out(dot) and not dot in self.busy:
                    if verb:
                        self.field[dot.x][dot.y] = '.'
                    self.busy.append(dot)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException
        if dot in self.busy:
            raise BoardUsedException

        self.busy.append(dot)

        for ship in self.ships:
            if dot in ship.dots:
                self.field[dot.x][dot.y] = 'X'
                ship.lives -= 1
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print('Корабль ранен')
                    return True

        self.field[dot.x][dot.y] = 'T'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []

class Player():
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        while True:
            dot = Dot(randrange(self.enemy.size), randrange(self.enemy.size))
            if dot not in self.enemy.busy:
                print(f'Компьютер стреляет по точке {dot.x + 1} {dot.y + 1}')
                return dot

class User(Player):
    def ask(self):
        while True:
            x = input('Введите координату по вертикали: ')
            y = input('Введите координату по горизонтали: ')
            if not x.isdigit() or not y.isdigit():
                print('Введите числа!')
                continue

            return Dot(int(x) - 1, int(y) - 1)

class Game():
    def __init__(self, size=6):
        self.size = size
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        self.user_board = self.random_board()
        self.ai_board = self.random_board()
        self.ai_board.hid = True

        self.ai = AI(self.ai_board, self.user_board)
        self.user = User(self.user_board, self.ai_board)

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(l, Dot( randrange(self.size), randrange(self.size)), randrange(2))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def print_boards(self):
        res = '        Доска пользователя               Доска компьютера\n'
        res += f"    {' | '.join(map(str, range(1, self.size + 1)))} |         {' | '.join(map(str, range(1, self.size + 1)))} | "
        for i, row_1, row_2 in zip(range(self.size), self.user_board.field, self.ai_board.field):
            if self.ai_board.hid:
                row_2 = ['O' if el == '■' else el for el in row_2]
            res += f'\n{i + 1} | ' + ' | '.join(row_1) + ' |' + '     ' + f'{i + 1} | ' + ' | '.join(row_2) + ' |'
        return res

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")

    def loop(self):
        move = 0
        while True:
            print(self.print_boards())
            if move % 2 == 0:
                print('Ходит пользователь')
                repeat = self.user.move()
            else:
                print('Ходит компьютер')
                sleep(2)
                repeat = self.ai.move()
            if repeat:
                move -= 1
            if self.ai.board.count == 7:
                print('Вы выиграли!')
                break
            if self.user.board.count == 7:
                print('Вы проиграли.')
                break

            move += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
# g.ai.board.hid = False
g.start()
