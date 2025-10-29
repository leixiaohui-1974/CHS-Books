from control.base_controller import BaseController

class PIDController(BaseController):
    """
    A standard PID (Proportional-Integral-Derivative) controller.
    """

    def __init__(self,
                 kp: float,
                 ki: float,
                 kd: float,
                 setpoint: float,
                 output_limits=(None, None),
                 windup_limit=None,
                 target_reach_index: int = None,
                 action: str = 'direct',
                 **kwargs):
        """
        Initializes the PID controller.
        """
        super().__init__()
        # Reverse gains for reverse action (e.g., controlling an upstream gate based on downstream level)
        self.kp = -kp if action == 'reverse' else kp
        self.ki = -ki if action == 'reverse' else ki
        self.kd = -kd if action == 'reverse' else kd

        self.setpoint = setpoint
        self.target_reach_index = target_reach_index

        if output_limits is None:
            self.min_output, self.max_output = None, None
        else:
            self.min_output, self.max_output = output_limits
        self.windup_limit = windup_limit

        # Initialize state variables
        self.integral_term = 0.0
        self.previous_error = 0.0
        self.last_output = None

    def update(self, current_sim_state: dict, dt: float) -> float:
        """
        Calculates the control variable value for the current time step.
        """
        if dt <= 0:
            return self.last_output if self.last_output is not None else 0.0

        try:
            current_value = current_sim_state['reach_levels'][self.target_reach_index]
        except (KeyError, IndexError):
            # Not enough information to calculate, return last known output
            return self.last_output if self.last_output is not None else 0.0

        error = self.setpoint - current_value

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup
        self.integral_term += self.ki * error * dt
        if self.windup_limit is not None:
            self.integral_term = max(-self.windup_limit, min(self.windup_limit, self.integral_term))
        i_term = self.integral_term

        # Derivative term
        # To avoid derivative kick, some implementations use the change in measurement
        # instead of the change in error. Here we use the simpler change in error.
        error_derivative = (error - self.previous_error) / dt
        d_term = self.kd * error_derivative

        # Combine terms to get the raw output
        output = p_term + i_term + d_term

        # Clamp the output to the defined limits
        if self.min_output is not None:
            output = max(self.min_output, output)
        if self.max_output is not None:
            output = min(self.max_output, output)

        # Update state for the next iteration
        self.previous_error = error
        self.last_output = output

        return output

    def reset(self):
        """Resets the controller's internal state."""
        self.integral_term = 0.0
        self.previous_error = 0.0
        self.last_output = None
