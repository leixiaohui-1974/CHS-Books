import pytest
import sys
import os

# Add the 'src' directory to the Python path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from control.pid import PIDController

@pytest.fixture
def basic_pid():
    """A basic PID controller for testing."""
    # The controller needs to know which reach's level to look at in the state dict
    return PIDController(kp=0.5, ki=0.1, kd=0.05, setpoint=10.0, target_reach_index=0)

class TestPIDController:

    def test_initialization(self):
        """Test controller initialization."""
        pid = PIDController(kp=1, ki=2, kd=3, setpoint=100)
        assert pid.kp == 1
        assert pid.ki == 2
        assert pid.kd == 3
        assert pid.setpoint == 100

    def test_proportional_term(self, basic_pid):
        """Test the P component of the controller."""
        state = {'reach_levels': [8.0]}
        output = basic_pid.update(state, dt=1.0)
        # Expected: P=0.5*(10-8)=1.0, I=0.1*2*1=0.2, D=0.05*(2-0)/1=0.1. Total = 1.3
        assert output == pytest.approx(1.3)

    def test_integral_term(self, basic_pid):
        """Test the I component accumulates error."""
        state1 = {'reach_levels': [8.0]}
        basic_pid.update(state1, dt=1.0) # Error=2, integral=2*0.1*1=0.2
        assert basic_pid.integral_term == pytest.approx(0.2)

        state2 = {'reach_levels': [8.0]}
        basic_pid.update(state2, dt=1.0) # Error=2, integral=0.2 + 2*0.1*1=0.4
        assert basic_pid.integral_term == pytest.approx(0.4)

    def test_derivative_term(self, basic_pid):
        """Test the D component responds to change in error."""
        state1 = {'reach_levels': [8.0]}
        output1 = basic_pid.update(state1, dt=1.0)
        assert output1 == pytest.approx(1.3)

        state2 = {'reach_levels': [7.0]}
        output2 = basic_pid.update(state2, dt=1.0)
        # Expected: P=0.5*3=1.5, I=0.2 + 0.1*3*1=0.5, D=0.05*(3-2)/1=0.05. Total = 2.05
        assert output2 == pytest.approx(2.05)

    def test_output_limits(self):
        """Test that the output is clamped to the defined limits."""
        pid = PIDController(kp=10, ki=0, kd=0, setpoint=10.0, output_limits=(0, 5), target_reach_index=0)

        state1 = {'reach_levels': [0.0]}
        output = pid.update(state1, dt=1.0)
        assert output == 5.0

        state2 = {'reach_levels': [20.0]}
        output = pid.update(state2, dt=1.0)
        assert output == 0.0

    def test_action_reverse(self):
        """Test that the reverse action correctly inverts the gains."""
        pid = PIDController(kp=0.5, ki=0.1, kd=0.05, setpoint=10.0, action='reverse', target_reach_index=0)
        # Error = 10 - 12 = -2
        # P = -0.5 * -2 = 1.0
        # I = -0.1 * -2 * 1 = 0.2
        # D = -0.05 * (-2 - 0) / 1 = 0.1
        # Total = 1.3
        state = {'reach_levels': [12.0]}
        output = pid.update(state, dt=1.0)
        assert output == pytest.approx(1.3)


from control.on_off import OnOffController

class TestOnOffController:
    """Unit tests for the OnOffController class."""

    @pytest.fixture
    def on_off_controller(self):
        """A standard OnOffController for testing."""
        return OnOffController(on_level=10.0, off_level=9.0, target_reach_index=0)

    def test_initial_state(self, on_off_controller):
        """Test that the controller initializes to the OFF state."""
        assert not on_off_controller.is_on
        assert on_off_controller.update({'reach_levels': [8.0]}, dt=1.0) == 0.0

    def test_hysteresis_turn_on(self, on_off_controller):
        """Test the turn-on logic."""
        # Level below on_level -> should stay OFF
        assert on_off_controller.update({'reach_levels': [9.5]}, dt=1.0) == 0.0
        assert not on_off_controller.is_on

        # Level at on_level -> should stay OFF
        assert on_off_controller.update({'reach_levels': [10.0]}, dt=1.0) == 0.0
        assert not on_off_controller.is_on

        # Level above on_level -> should turn ON
        assert on_off_controller.update({'reach_levels': [10.1]}, dt=1.0) == 1.0
        assert on_off_controller.is_on

    def test_hysteresis_turn_off(self, on_off_controller):
        """Test the turn-off logic."""
        # First, turn the controller ON
        on_off_controller.is_on = True

        # Level above off_level -> should stay ON
        assert on_off_controller.update({'reach_levels': [9.5]}, dt=1.0) == 1.0
        assert on_off_controller.is_on

        # Level at off_level -> should stay ON
        assert on_off_controller.update({'reach_levels': [9.0]}, dt=1.0) == 1.0
        assert on_off_controller.is_on

        # Level below off_level -> should turn OFF
        assert on_off_controller.update({'reach_levels': [8.9]}, dt=1.0) == 0.0
        assert not on_off_controller.is_on

    def test_reset(self, on_off_controller):
        """Test that the reset method correctly resets the state."""
        # Turn controller on
        on_off_controller.is_on = True
        assert on_off_controller.is_on

        # Reset it
        on_off_controller.reset()
        assert not on_off_controller.is_on
