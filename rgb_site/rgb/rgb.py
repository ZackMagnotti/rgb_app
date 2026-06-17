import numpy as np
from scipy import ndimage

class RGB:
    def __init__(
        self,
        growth_rate,
        predation_rate,
        predation_efficiency,
        sigma
    ):
        _a = growth_rate
        _g = -growth_rate / 255
        _b = -predation_rate
        _d = predation_rate * predation_efficiency
        self._a = _a
        self._g = _g
        self._b = _b
        self._d = _d
        self._A = np.array([
            [_g, _d, _b],
            [_b, _g, _d],
            [_d, _b, _g]
        ])
        self._sigma = sigma

    def pp_diff(self, p, p_k):
        """
        Partial Pixel Diff

        p <np.ndarray>: pixel vector with shape (3),
            or array of such vectors
        p_k <np.ndarray>: pixel vector with identical shape to p
        return: Diff of p relative to p_k
        """
        return p_k * (self._a + np.matvec(self._A, p))

    def diff(self, p):
        """
        p <np.ndarray>: pixel vector with shape (3),
            or array of such vectors
        return: Diff of p
        """
        return self.pp_diff(p, p)

    def next_pixel(self, p):
        return p + self.diff(p)

    def next_frame(self, frame):
        pk_frame = ndimage.gaussian_filter(
            frame, sigma=self._sigma, axes=(0, 1)
        )
        new_frame = frame + self.pp_diff(frame, pk_frame)
        # filtering negative values prevents crashes
        return new_frame * (new_frame > 0)
