from machine import Signal, Pin
import mled

pixelart = {
    'heart':  0x00367F7F3E1C0800,
    'pacman': 0x3c4221111121423c,
    'ghost':  0x3C7E99DDFFFFFFDB
}

ani_heart_pulse = [
    (0, pixelart['heart']),
    (1, None),
    (2, None),
    (3, None),
    (4, None),
    (5, None),
    (6, None),
    (7, None),
    (6, None),
    (5, None),
    (4, None),
    (3, None),
    (2, None),
    (1, None),
    (0, None),
    (0, 0x00)
]

ani_pacman_pulse = [
    (0, pixelart['pacman']),
    (1, None),
    (2, None),
    (3, None),
    (4, None),
    (5, None),
    (6, None),
    (7, None),
    (6, None),
    (5, None),
    (4, None),
    (3, None),
    (2, None),
    (1, None),
    (0, None),
    (0, 0x00)
]

ani_ghost_pulse = [
    (0, pixelart['ghost']),
    (1, None),
    (2, None),
    (3, None),
    (4, None),
    (5, None),
    (6, None),
    (7, None),
    (6, None),
    (5, None),
    (4, None),
    (3, None),
    (2, None),
    (1, None),
    (0, None),
    (0, 0x00)
]

class Example:

    boards = {
        'd1_mini': (13, 14),
        'mh_et_live_minikit': (23, 18)
    }

    def main(self, model):
        self.matrix = mled.driver(self.boards[model][0], self.boards[model][1])
        self.test()
        self.animate()

    def test(self):
        self.matrix.clear()
        self.matrix.setIntensity(7)
        for y in range(0, 8):
            for x in range(0, 8):
                self.matrix.pixel(x, y, self.matrix.ON)
                self.matrix.display()

        for y in range(0, 8):
            for x in range(0, 8):
                self.matrix.pixel(x, y, self.matrix.OFF)
                self.matrix.display()

    def animate(self):
        ani = mled.animation(self.matrix)
        ani.loop(0, 64, ani_heart_pulse + ani_pacman_pulse + ani_ghost_pulse)


app = Example()
app.main('d1_mini')