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
from typing import Optional, TypeAlias, TypeVar

import cv2
from mulog import generate_mondrian_image, generate_speckle, simulate_polsar_from_rgb
import nptyping as npt
from nptyping import Shape
import numpy as np

from .multilooking import MatrixFieldStack

T = TypeVar("T", bound=int)
M = TypeVar("M", bound=int)
N = TypeVar("N", bound=int)

RGBImageStack: TypeAlias = (
    npt.NDArray[Shape["T,M,N,3"], npt.Floating]
    | npt.NDArray[Shape["T,M,N,3"], npt.Integer]
)


def generate_mondrian_image_stack(resize_factor: float = 0.5) -> RGBImageStack:
    max_t: int = 10
    result = np.array(
        [
            generate_mondrian_image(),
        ]
        * max_t
    )
    for t in range(max_t):
        result[t, :24, :74, :] = np.array([200 + 55 * np.cos(t / 10 * 2 * np.pi), 1, 0])
    result[3:6, 27:, :49] = np.array([255, 1, 255])
    result[6, 27:, :49] = np.array([255, 255, 255])
    result[9:10, :24, 77:] = np.array([255, 255, 1])
    result[1:3, 27:, :] = np.array([1, 1, 255])
    result = np.stack(
        [
            cv2.resize(
                result[t],
                dsize=None,
                fx=resize_factor,
                fy=resize_factor,
                interpolation=cv2.INTER_CUBIC,
            )
            for t in range(max_t)
        ],
        axis=0,
    )
    return result


def simulate_polsar_stack_from_rgb_stack(
    image_stack: RGBImageStack,
) -> MatrixFieldStack:
    return np.stack([simulate_polsar_from_rgb(image) for image in image_stack])


def generate_speckle_stack(
    number_looks: int,
    sar_stack: Optional[MatrixFieldStack] = None,
    shape: Optional[tuple[int, int, int, int, int] | tuple[int, int, int]] = None,
    random_state: Optional[np.random.RandomState] = None,
) -> MatrixFieldStack:
    """
    Simulate speckle according to Goodman's fully developed model.
    :param number_looks: the parameter of the Wishart distribution.
    :param sar_stack: the underlying matrix field stack if any, identity otherwise.
    :param shape: the shape of the matrix field if `matrix_field` is not provided.
    :param random_state: the state of the random generator.
    :return: a field of Hermitian non-negative matrices. If `number_looks` is
        is larger that the matrix dimension, the field is positive definite.
    """
    if random_state is None:
        random_state = np.random.RandomState(1630)

    if sar_stack is None and shape is None:
        raise ValueError("Arguments `matrix_field_stack` or `shape` must be given")
    if shape is None:
        assert sar_stack is not None
        shape = sar_stack.shape  # type: ignore

    assert shape is not None

    if sar_stack is not None and sar_stack.shape != shape:
        raise ValueError(
            f"Got incompatible dimensions ({sar_stack.shape}) vs ({shape})"
        )

    if len(shape) == 5:
        is_scalar_stack = False
    elif len(shape) == 3:
        is_scalar_stack = True
        shape = (shape[0], shape[1], shape[2], 1, 1)
        if sar_stack is not None:
            sar_stack = sar_stack[:, :, :, np.newaxis, np.newaxis]  # type: ignore
    else:
        raise ValueError(f"Unexpected shape {shape}")

    result = np.array(
        [
            generate_speckle(
                number_looks=number_looks,
                sar_image=sar_stack[k] if sar_stack is not None else None,
                shape=shape[1:],
                random_state=random_state,
            )
            for k in range(shape[0])
        ]
    )

    if is_scalar_stack:
        return result[:, :, :, 0, 0]
    else:
        return result
