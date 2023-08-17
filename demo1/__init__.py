import random
from st3m.application import Application, ApplicationContext
from st3m.ui.view import BaseView, ViewManager
from st3m.input import InputState
from ctx import Context
import st3m.run
import leds


class MyDemo(Application):
    COLORS_PAUSED = [
        [200, 0, 0],
        [200, 200, 0],
        [0, 200, 0],
        [0, 200, 200],
        [0, 0, 200],
    ]
    COLOR_GRID_ACTIVE = [210, 220, 250]
    COLOR_GRID_INACTIVE = [99, 13, 42]
    GRID_SIZE = 24
    INITIAL_CELLS = 128
    LEDS = 40
    RAINBOW_SHIFT_PER_FRAME = 19

    def __init__(self, app_ctx: ApplicationContext) -> None:
        super().__init__(app_ctx)

        self.COLORS_RAINBOW = generate_rainbow_colors(self.LEDS)

        self.grid = fill_some_cells(
            generate_empty_grid(self.GRID_SIZE), self.INITIAL_CELLS
        )
        self.speed = 2

        self.frame_counter = 0
        self.paused = False
        self.brightness = 0
        self.brightness_inc = True
        self.brightness_rainbow = 255
        self.brightness_step = 16
        self.colors_paused_idx = 0

        leds.set_slew_rate(1)
        self.leds_running()

    def draw(self, ctx: Context) -> None:
        # Paint the background black
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()

        if not self.paused and self.frame_counter % self.speed == 0:
            self.evolve()

        cell_color = (
            self.COLOR_GRID_INACTIVE
            if self.paused
            else self.COLORS_RAINBOW[self.frame_counter % self.LEDS]
        )
        self.draw_grid(ctx, cell_color)

        self.frame_counter += 1

    def think(self, ins: InputState, delta_ms: int) -> None:
        super().think(ins, delta_ms)

        if self.input.buttons.app.middle.pressed:
            self.paused = not self.paused

        if self.paused:
            if self.input.buttons.app.left.pressed:
                self.colors_paused_idx = (self.colors_paused_idx - 1) % len(
                    self.COLORS_PAUSED
                )
            if self.input.buttons.app.right.pressed:
                self.colors_paused_idx = (self.colors_paused_idx + 1) % len(
                    self.COLORS_PAUSED
                )
        else:
            if self.input.buttons.app.left.pressed:
                self.brightness_rainbow = max(
                    self.brightness_rainbow - self.brightness_step, 10
                )
            if self.input.buttons.app.right.pressed:
                self.brightness_rainbow = min(
                    self.brightness_rainbow + self.brightness_step, 255
                )

        if self.paused:
            leds.set_slew_rate(3)
            step = max(int(delta_ms / 17), 1)
            self.leds_fade(step, 10, 90)
            self.leds_paused()
        else:
            leds.set_slew_rate(1)
            self.brightness = self.brightness_rainbow
            self.leds_running()

        leds.set_brightness(self.brightness)
        leds.update()

    def leds_fade(self, step, min, max) -> None:
        if self.brightness_inc:
            self.brightness += step
        else:
            self.brightness -= step

        if self.brightness < min:
            self.brightness = min
            self.brightness_inc = True
        elif self.brightness > max:
            self.brightness = max
            self.brightness_inc = False

    def leds_paused(self) -> None:
        leds.set_all_rgb(
            self.COLORS_PAUSED[self.colors_paused_idx][0],
            self.COLORS_PAUSED[self.colors_paused_idx][1],
            self.COLORS_PAUSED[self.colors_paused_idx][2],
        )

    def leds_running(self) -> None:
        if self.frame_counter % self.RAINBOW_SHIFT_PER_FRAME != 0:
            return

        for i in range(self.LEDS):
            leds.set_rgb(
                i,
                self.COLORS_RAINBOW[i][0],
                self.COLORS_RAINBOW[i][1],
                self.COLORS_RAINBOW[i][2],
            )

        self.COLORS_RAINBOW.insert(0, self.COLORS_RAINBOW.pop())

    def evolve(self) -> None:
        # clone the grid
        new_grid = []
        for row in self.grid:
            new_grid.append(row.copy())

        alive_cells = 0

        # count neighbors and apply rules
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                num_neighbors = self.count_neighbors(x, y)
                if self.grid[y][x]:
                    if num_neighbors < 2 or num_neighbors > 3:
                        new_grid[y][x] = False
                else:
                    if num_neighbors == 3:
                        new_grid[y][x] = True
                        alive_cells += 1

        # write back grid or generate a new one if everything is dead
        self.grid = (
            new_grid
            if alive_cells > 0
            else fill_some_cells(
                generate_empty_grid(self.GRID_SIZE), self.INITIAL_CELLS
            )
        )

    def count_neighbors(self, x, y) -> int:
        num_neighbors = 0
        for y_offset in range(-1, 2):
            for x_offset in range(-1, 2):
                if y_offset == 0 and x_offset == 0:
                    continue
                if (
                    y + y_offset >= 0
                    and y + y_offset < self.GRID_SIZE
                    and x + x_offset >= 0
                    and x + x_offset < self.GRID_SIZE
                ):
                    if self.grid[y + y_offset][x + x_offset]:
                        num_neighbors += 1
        return num_neighbors

    def draw_grid(self, ctx: Context, color) -> None:
        cell_size = round(240 / self.GRID_SIZE)

        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                grid_x = x * cell_size - 120
                grid_y = y * cell_size - 120
                if self.grid[y][x]:
                    ctx.rgb(color[0], color[1], color[2]).rectangle(
                        grid_x, grid_y, cell_size, cell_size
                    ).fill()
                else:
                    ctx.gray(0.4).rectangle(
                        grid_x, grid_y, cell_size, cell_size
                    ).stroke()


def generate_rainbow_colors(num_colors):
    rainbow_colors = []
    for i in range(num_colors):
        angle = 2 * 3.14159 * i / num_colors  # Angle in radians
        red = int((1 + 0.5 * (1 - abs((angle / 3.14159) % 2 - 1))) * 255)
        green = int((1 + 0.5 * (1 - abs((angle / 3.14159 - 2 / 3) % 2 - 1))) * 255)
        blue = int((1 + 0.5 * (1 - abs((angle / 3.14159 - 4 / 3) % 2 - 1))) * 255)
        rainbow_colors.append([red, green, blue])
    return rainbow_colors


def generate_empty_grid(size):
    row = [False for _ in range(size)]
    grid = []
    for _ in range(size):
        grid.append(row.copy())
    return grid


def fill_some_cells(grid, num_cells):
    for _ in range(num_cells):
        x = random.randint(0, len(grid) - 1)
        y = random.randint(0, len(grid) - 1)
        grid[y][x] = True

    return grid


if __name__ == "__main__":
    # Continue to make runnable via mpremote run.
    st3m.run.run_view(MyDemo(ApplicationContext()))
