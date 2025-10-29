import sys
import os
import pytest

# Add the 'src' directory to the Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from control.pid import PIDController

@pytest.fixture
def pid_controller():
    """Returns a default PIDController for testing."""
    return PIDController(kp=0.5, ki=0.1, kd=0.05, setpoint=10.0, target_reach_index=0)

def test_pid_no_error(pid_controller):
    """Test that with no error, the output is zero (or only the integral part if not zero)."""
    pid_controller.reset()
    state = {'reach_levels': [10.0]}
    # First update to establish previous_error
    pid_controller.update(state, dt=1.0)
    # Second update
    output = pid_controller.update(state, dt=1.0)
    # P=0, D=0. I should be ki*error*dt = 0.
    assert output == 0.0

def test_pid_proportional_term(pid_controller):
    """Test the proportional response to an error."""
    pid_controller.reset()
    state = {'reach_levels': [8.0]} # Error = 10 - 8 = 2.0
    output = pid_controller.update(state, dt=1.0)
    # P = kp * error = 0.5 * 2.0 = 1.0
    # I = ki * error * dt = 0.1 * 2.0 * 1.0 = 0.2
    # D = kd * (error - prev_error) / dt = 0.05 * (2.0 - 0.0) / 1.0 = 0.1
    # Total = 1.0 + 0.2 + 0.1 = 1.3
    assert output == pytest.approx(1.3)

def test_pid_integral_term(pid_controller):
    """Test the integral term accumulating over time."""
    pid_controller.reset()
    state = {'reach_levels': [9.0]} # Error = 1.0
    # First step
    pid_controller.update(state, dt=1.0) # Integral becomes 0.1 * 1.0 * 1.0 = 0.1
    # Second step, same error
    output = pid_controller.update(state, dt=1.0) # Integral becomes 0.1 + (0.1 * 1.0 * 1.0) = 0.2
    # P = 0.5 * 1.0 = 0.5
    # I = 0.2
    # D = 0.05 * (1.0 - 1.0) / 1.0 = 0.0
    # Total = 0.5 + 0.2 = 0.7
    assert output == pytest.approx(0.7)

def test_pid_derivative_term(pid_controller):
    """Test the derivative response to a changing error."""
    pid_controller.reset()
    state1 = {'reach_levels': [8.0]} # Error = 2.0
    pid_controller.update(state1, dt=1.0) # prev_error becomes 2.0

    state2 = {'reach_levels': [9.0]} # Error = 1.0
    output = pid_controller.update(state2, dt=1.0)
    # P = 0.5 * 1.0 = 0.5
    # I = (0.1 * 2.0 * 1.0) + (0.1 * 1.0 * 1.0) = 0.3
    # D = 0.05 * (1.0 - 2.0) / 1.0 = -0.05
    # Total = 0.5 + 0.3 - 0.05 = 0.75
    assert output == pytest.approx(0.75)

def test_pid_output_limits():
    """Test that the output is clipped to the defined limits."""
    controller = PIDController(
        kp=1.0, ki=0.0, kd=0.0, setpoint=10.0,
        output_limits=(-1.0, 1.0), target_reach_index=0
    )

    # Test max limit
    state_high_error = {'reach_levels': [0.0]} # Error = 10.0, raw output = 10.0
    output_max = controller.update(state_high_error, dt=1.0)
    assert output_max == 1.0

    # Test min limit
    state_low_error = {'reach_levels': [20.0]} # Error = -10.0, raw output = -10.0
    output_min = controller.update(state_low_error, dt=1.0)
    assert output_min == -1.0
