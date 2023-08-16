from st3m.application import Application, ApplicationContext
from st3m.ui.view import BaseView, ViewManager
from st3m.input import InputState
from ctx import Context
import st3m.run
import leds

class MyDemo(Application):
    def __init__(self, app_ctx: ApplicationContext) -> None:
        super().__init__(app_ctx)
        self.paused = False
        self.LEDS = [[23, 69, 255] for i in range(40)]
        for i in range(len(self.LEDS)):
            leds.set_rgb(i, self.LEDS[i][0], self.LEDS[i][1], self.LEDS[i][2])
        self.brighness = 0 # 0 to 255
        self.brighness_inc = True

    def draw(self, ctx: Context) -> None:
        # Paint the background black
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()

        if self.paused:
            # Red square
            ctx.rgb(255, 0, 0).rectangle(-20, -20, 40, 40).fill()
        else:
            # Green square
            ctx.rgb(0, 255, 0).rectangle(-20, -20, 40, 40).fill()

        leds.set_brightness(self.brighness)
        leds.update()

    def think(self, ins: InputState, delta_ms: int) -> None:
        super().think(ins, delta_ms)

        if self.input.buttons.app.middle.pressed:
            self.paused = not self.paused

        if not self.paused:
            # LED fading
            step = int(delta_ms / 10)
            if self.brighness_inc:
                self.brighness += step
            else:
                self.brighness -= step

            if self.brighness > 255:
                self.brighness = 255
                self.brighness_inc = False
            elif self.brighness < 0:
                self.brighness = 0
                self.brighness_inc = True

if __name__ == '__main__':
    # Continue to make runnable via mpremote run.
    st3m.run.run_view(MyDemo(ApplicationContext()))