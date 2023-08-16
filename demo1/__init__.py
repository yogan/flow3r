from st3m.application import Application, ApplicationContext
from st3m.ui.view import BaseView, ViewManager
from st3m.input import InputState
from ctx import Context
import st3m.run
import leds

class MyDemo(Application):
    COLOR_PAUSED = [200, 0, 0]
    LEDS = 40
    RAINBOW_SHIFT_PER_FRAME = 19

    def __init__(self, app_ctx: ApplicationContext) -> None:
        super().__init__(app_ctx)

        self.COLORS_RAINBOW = generate_rainbow_colors(self.LEDS)

        self.frame_counter = 0
        self.paused = False
        self.brightness = 0
        self.brightness_inc = True

        leds.set_slew_rate(1)
        self.leds_running()

    def draw(self, ctx: Context) -> None:
        # Paint the background black
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()

        if self.paused:
            # Red square
            ctx.rgb(255, 0, 0).rectangle(-20, -20, 40, 40).fill()
        else:
            # Green square
            ctx.rgb(0, 255, 0).rectangle(-20, -20, 40, 40).fill()

        self.frame_counter += 1

    def think(self, ins: InputState, delta_ms: int) -> None:
        super().think(ins, delta_ms)

        if self.input.buttons.app.middle.pressed:
            self.paused = not self.paused

        if self.paused:
            leds.set_slew_rate(3)
            step = max(int(delta_ms / 17), 1)
            self.leds_fade(step, 10, 90)
            self.leds_paused()
        else:
            leds.set_slew_rate(1)
            self.brightness = 255
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
        leds.set_all_rgb(self.COLOR_PAUSED[0],
                         self.COLOR_PAUSED[1],
                         self.COLOR_PAUSED[2])

    def leds_running(self) -> None:
        if self.frame_counter % self.RAINBOW_SHIFT_PER_FRAME != 0:
            return

        for i in range(self.LEDS):
            leds.set_rgb(i, self.COLORS_RAINBOW[i][0],
                            self.COLORS_RAINBOW[i][1],
                            self.COLORS_RAINBOW[i][2])

        self.COLORS_RAINBOW.insert(0, self.COLORS_RAINBOW.pop())


def generate_rainbow_colors(num_colors):
    rainbow_colors = []
    for i in range(num_colors):
        angle = 2 * 3.14159 * i / num_colors  # Angle in radians
        red = int((1 + 0.5 * (1 - abs((angle / 3.14159) % 2 - 1))) * 255)
        green = int((1 + 0.5 * (1 - abs((angle / 3.14159 - 2 / 3) % 2 - 1))) * 255)
        blue = int((1 + 0.5 * (1 - abs((angle / 3.14159 - 4 / 3) % 2 - 1))) * 255)
        rainbow_colors.append([red, green, blue])
    return rainbow_colors


if __name__ == '__main__':
    # Continue to make runnable via mpremote run.
    st3m.run.run_view(MyDemo(ApplicationContext()))