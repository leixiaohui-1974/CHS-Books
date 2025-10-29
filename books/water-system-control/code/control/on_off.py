from control.base_controller import BaseController

class OnOffController(BaseController):
    """
    A simple On/Off controller with hysteresis.
    This controller turns a device (like a pump) on or off based on whether
    a measured value is above or below specified thresholds.
    """

    def __init__(self,
                 on_level: float,
                 off_level: float,
                 target_reach_index: int,
                 **kwargs):
        """
        Initializes the On/Off controller.

        Args:
            on_level (float): The level at which to turn the device ON.
            off_level (float): The level at which to turn the device OFF.
            target_reach_index (int): The index of the reach to monitor.
        """
        super().__init__()
        self.on_level = on_level
        self.off_level = off_level
        self.target_reach_index = target_reach_index
        self.is_on = False # Start in the OFF state

    def update(self, current_sim_state: dict, dt: float) -> float:
        """
        Calculates the control action (1 for ON, 0 for OFF).
        """
        try:
            current_level = current_sim_state['reach_levels'][self.target_reach_index]
        except (KeyError, IndexError):
            # Not enough info, maintain current state
            return 1.0 if self.is_on else 0.0

        if self.is_on:
            # If the pump is ON, it only turns off if the level drops below off_level
            if current_level < self.off_level:
                self.is_on = False
        else:
            # If the pump is OFF, it only turns on if the level rises above on_level
            if current_level > self.on_level:
                self.is_on = True

        return 1.0 if self.is_on else 0.0

    def reset(self):
        """Resets the controller's state to OFF."""
        self.is_on = False
