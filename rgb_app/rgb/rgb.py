import numpy as np
from scipy import ndimage

class RGB:

    def __init__(
        self,
        growth_rate,
        predation_rate,
        predation_efficiency
    ):
        """
        Initializes conditions for RGB simulation

        growth_rate <float>: independant growth rate of a species
        predation_rate <float>: rate at which a species will be
            eliminated by its predator
        predation_efficiency <float>: rate at which predation converts
            into population growth for the predator species.
        """
        a = growth_rate
        g = -growth_rate / 255
        b = -predation_rate
        d = predation_rate * predation_efficiency
        self._a = a
        self._A = np.array([
            [g, d, b],
            [b, g, d],
            [d, b, g]
        ])

    def diff(self, v):
        """
        Calcualates dv/dt

        dv/dt = _av + v * A(v)

        v <np.ndarray>: vector with shape (3),
            or array of such vectors
        return dv/dt <np.ndarray> vector or array
            of vectors with same shape as input
        """
        return v * (self._a + np.matvec(self._A, v))

    def get_next(self, v):
        """
        Calculates next step in simulation, v + dv/dt

        v <np.ndarray>: vector with shape (3),
            or array of such vectors
        return v + dv/dt <np.ndarray> vector or array
            of vectors with same shape as input
        """
        v_next = v + self.diff(v)
        # filter negative values to prevent divergent behavior
        return v_next * (v_next > 0)

class RGBField(RGB):

    def __init__(
        self,
        growth_rate,
        predation_rate,
        predation_efficiency,
        sigma
    ):
        """
        Initializes conditions for RGB 2D diffusal simulation

        growth_rate <float>: independant growth rate of a species
        predation_rate <float>: rate at which a species will be
            eliminated by its predator
        predation_efficiency <float>: rate at which predation converts
            into population growth for the predator species.
        sigma <float>: sigma value to be passed to gaussian blur
            function representing 2D diffusal.
        """
        self._sigma = sigma
        super().__init__(
            growth_rate,
            predation_rate,
            predation_efficiency
        )

    def get_next_frame(self, frame):
        """
        Calculates next step in 2D diffusal simulation.
        First performs a gaussian blur using self._sigma to represent
        diffusal and interaction between cells (pixels), then calculates
        dv/dt on each cell of the diffused frame to represent interaction
        between species.

        next_frame = current_frame + df/dt

        frame <np.ndarray>: array with size (n, m, 3) representing a color image.
            The rgb values of each pixel will be treated as the populations of the
            three "species" for the RGB population simulation.
        return next_frame <np.ndarray>: array with same size as input representing
            the next frame in the simulation
        """
        diffused_frame = ndimage.gaussian_filter(
            frame, sigma=self._sigma, axes=(0, 1), mode='reflect'
        )
        new_frame = frame + self.diff(diffused_frame)
        # filter negative values to prevent divergent behavior
        return new_frame * (new_frame > 0)
