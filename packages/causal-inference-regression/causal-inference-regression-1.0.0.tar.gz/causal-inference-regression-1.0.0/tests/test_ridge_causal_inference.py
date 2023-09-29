from dbml.ridge_causal_inference import RidgeCausalInference
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
import numpy.typing as npt
from typing import Tuple
import numpy as np
import unittest


class TestRegression(unittest.TestCase):

    n_tests = 5
    places = 6
    atol = 1e-06
    rtol = 1e-06
    min_samples = 15
    max_samples = 10_000

    def create_data(self) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        n_samples = np.random.randint(self.min_samples, self.max_samples)
        max_features = 100 if n_samples // 2 > 100 else n_samples // 2
        n_features = np.random.randint(1, max_features)
        noise = np.random.randint(10, 100)

        x, y = make_regression(n_samples=n_samples, n_features=n_features, noise=noise)
        t = np.random.randint(0, 2, n_samples)
        y += (np.random.normal(10, 0, n_samples) * t)

        return x, t, y

    def test_fwl_theorem(self):
        """alpha=0 and out-of-fold residuals oof=False should yield the same result according to FWL as OLS"""
        print('testing FWL')
        for i in range(self.n_tests):
            print(f'    test {i + 1}')

            x, t, y = self.create_data()

            rci = RidgeCausalInference(x, t, y, alphas=[0], oof_residuals=False)
            rci.run_causal_pipeline()

            m = LinearRegression()
            m.fit(np.concatenate((x, t.reshape(-1, 1)), axis=1),
                  y
                  )
            self.assertAlmostEqual(rci.treatment_coef_, m.coef_[-1], places=self.places)
