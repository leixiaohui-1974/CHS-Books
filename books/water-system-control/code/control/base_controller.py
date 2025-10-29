from abc import ABC, abstractmethod

class BaseController(ABC):
    """
    Abstract base class for all controllers in the simulation.
    """

    def __init__(self, **kwargs):
        """
        Initializes the controller.

        Args:
            **kwargs: Controller-specific parameters.
        """
        # This base constructor can be extended by subclasses
        pass

    @abstractmethod
    def update(self, current_sim_state: dict, dt: float) -> float:
        """
        Calculates the control action for the current time step.

        This method must be implemented by subclasses.

        Args:
            current_sim_state (dict): A dictionary containing the current state of the
                                      simulation relevant to the controller. This may
                                      include keys like 'level', 'flow', etc.
            dt (float): The time delta in seconds since the last update.

        Returns:
            float: The calculated control output (e.g., a gate opening, a pump speed).
        """
        raise NotImplementedError

    def reset(self):
        """
        Resets the controller's internal state to its initial condition.
        Subclasses should override this if they have state to reset.
        """
        pass
