"""
License

This software is governed by the CeCILL license under French law and
abiding by the rules of distribution of free software. You can use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty and the software's author, the holder of the
economic rights, and the successive licensors have only limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading, using, modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean that it is complicated to manipulate, and that also
therefore means that it is reserved for developers and experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and, more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

Copyright Charles Deledalle (charles-alban.deledalle@math.u-bordeaux.fr)

List of Contributors:
  - Charles Deledalle (original version in Matlab)
  - Sébastien Mounier (translation in Python)
  - Cristiano Ulondu Mendes (bug fixes and improvements)

Scientific articles describing the method:

[1] Zhao, W., Deledalle, C. A., Denis, L., Maître, H., Nicolas, J. M.,
    & Tupin, F. (2019). Ratio-based multitemporal SAR images denoising:
    RABASAR. IEEE Transactions on Geoscience and Remote Sensing, 57(6),
    3552-3565.

[2] Deledalle, C. A., Denis, L., Ferro-Famil, L., Nicolas, J. M., &
    Tupin, F. (2019, July). Multi-temporal speckle reduction of
    polarimetric SAR images: A ratio-based approach. In IGARSS 2019-2019
    IEEE International Geoscience and Remote Sensing Symposium (pp. 899-
    902). IEEE.
"""

from typing import TypeAlias, TypeVar, Union

from mulog import (
    GaussianDenoiser,
    SARImage,
    ScalarImageStack,
    compute_fisher_tippet_noise_std,
    estimate_gaussian_noise_std_with_mad,
    run_mulog,
    stabmatrices,
)
import nptyping as npt
import numpy as np
import scipy

T = TypeVar("T", bound=int)
M = TypeVar("M", bound=int)
N = TypeVar("N", bound=int)
D = TypeVar("D", bound=int)

MatrixFieldStack: TypeAlias = npt.NDArray[npt.Shape["T,M,N,D,D"], npt.Floating]
SARImageStack: TypeAlias = Union[ScalarImageStack, MatrixFieldStack]
TSARImageStack = TypeVar("TSARImageStack", bound=SARImageStack)


def inverse_compute_fisher_tippet_noise_std(std: float) -> float:
    """
    Compute the inverse of the function `compute_fisher_tippet_noise_std`
    """
    # Optimization below is bounded because the trigamma function satisifies:
    #
    #   (x + .5) / x**2 <= psi1(x) <= (x + 1) / x**2
    #
    return np.exp(
        scipy.optimize.fminbound(
            lambda log_number_looks: (
                compute_fisher_tippet_noise_std(np.exp(log_number_looks)) - std
            )
            ** 2,
            np.log((1 + np.sqrt(1 + 2 * std**2)) / (2 * std**2)),
            np.log((1 + np.sqrt(1 + 4 * std**2)) / (2 * std**2)),
        )
    )


def estimate_number_looks(sar_image: SARImage) -> float:
    d = 1 if sar_image.ndim == 2 else sar_image.shape[2]
    measured_std = float(
        np.mean(
            [
                estimate_gaussian_noise_std_with_mad(
                    np.log(sar_image[:, :, k, k])
                    if sar_image.ndim == 4
                    else np.log(sar_image)
                )
                for k in range(d)
            ]
        )
    )
    return inverse_compute_fisher_tippet_noise_std(measured_std)


def compute_sar_super_image(
    sar_stack: SARImageStack,
    denoiser: GaussianDenoiser | None,
) -> SARImage:
    """
    Compute the "super-image" of a temporal series of polarimetric images
    :param sar_stack: a stack of T polarimetric SAR images.
    :param denoiser: a Gaussian denoiser to use within MuLoG if provided.
        If None, super image isn't denoised.
    :return: average of the T polarimetric SAR images optionally post-processed
        by the provided spatial filtering with MuLoG.
    """

    if sar_stack.ndim == 5:
        reshaped = False
    elif sar_stack.ndim == 3:
        reshaped = True
        sar_stack = sar_stack[:, :, :, np.newaxis, np.newaxis]
    else:
        raise ValueError(
            "The first input of this function should be of size "
            "T x M x N ot T x M x N x D x D with T>1 "
        )
    temporal_average = stabmatrices(np.mean(sar_stack, axis=0))

    if denoiser is None:
        result = temporal_average
    else:
        estimated_number_looks = estimate_number_looks(sar_image=temporal_average)

        # spatial filtering
        result = run_mulog(
            sar_image=temporal_average,
            number_looks=estimated_number_looks,
            denoiser=denoiser,
        )

    if reshaped:
        return result[:, :, 0, 0]
    else:
        return result
