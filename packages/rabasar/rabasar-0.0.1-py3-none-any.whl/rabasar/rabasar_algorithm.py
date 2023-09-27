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

from mulog import GaussianDenoiser, SARImage, run_mulog
from mulog.hermitian_matrix_field import (
    MatrixField,
    mulmatrices,
    spfunmatrices,
)
import numpy as np

from .multilooking import MatrixFieldStack, TSARImageStack, compute_sar_super_image


def _compute_sar_residue_stack(
    matrix_field_stack: MatrixFieldStack, super_matrix_field: MatrixField
) -> MatrixFieldStack:
    """
    Compute the residual images as the maxtrix ratio between the images of the stack
    and the super image.
    :param matrix_field_stack: a stack of T polarimetric SAR images (T>=1)
    :param super_matrix_field: a super-image
    :return: a stack of T ratio images, calculated with the formula:

        matrix_field_super^-1/2 x matrix_field_stack x matrix_field_super^-1/2)
    """
    inv_sqrt_super_matrix_field = spfunmatrices(
        super_matrix_field, lambda x: 1 / np.sqrt(x)
    )
    return mulmatrices(
        mulmatrices(inv_sqrt_super_matrix_field, matrix_field_stack),
        inv_sqrt_super_matrix_field,
    )


def run_rabasar_residue_filtering(
    sar_stack: TSARImageStack,
    super_sar_image: SARImage,
    number_looks: float,
    denoiser: GaussianDenoiser,
) -> TSARImageStack:
    if sar_stack.ndim == 3:
        assert super_sar_image.ndim == 2
        is_scalar_stack = True
        sar_stack = sar_stack[:, :, :, np.newaxis, np.newaxis]  # type: ignore
        super_sar_image = super_sar_image[:, :, np.newaxis, np.newaxis]
    elif sar_stack.ndim == 5:
        assert super_sar_image.ndim == 4
        is_scalar_stack = False
    else:
        raise ValueError(f"Unexpected ndim {sar_stack.ndim} for `sar_stack`")

    # Compute residual images
    matrix_field_stack_residue = _compute_sar_residue_stack(sar_stack, super_sar_image)

    # Perform spatial filtering of residual images
    denoised_matrix_field_stack_residue = np.stack(
        [
            run_mulog(
                sar_image=matrix_field_stack_residue[t],
                number_looks=number_looks,
                denoiser=denoiser,
            )
            for t in range(matrix_field_stack_residue.shape[0])
        ]
    )

    # final estimation
    sqrt_super_matrix_field = spfunmatrices(super_sar_image, lambda x: np.sqrt(x))
    result = mulmatrices(
        mulmatrices(sqrt_super_matrix_field, denoised_matrix_field_stack_residue),
        sqrt_super_matrix_field,
    )

    if is_scalar_stack:
        return result[:, :, :, 0, 0]  # type: ignore
    else:
        return result  # type: ignore


def run_rabasar(
    sar_stack: TSARImageStack,
    number_looks: float,
    denoiser: GaussianDenoiser,
) -> tuple[TSARImageStack, SARImage]:
    """
    Reduce speckle in images of the stack using Rabasar.
    :param sar_stack: a stack of T SAR/InSAR/PolSAR images (T>=1)
    :param number_looks: the number of looks
    :return: a stack of T denoised images
    """

    # Compute super-image
    super_sar_image = compute_sar_super_image(sar_stack, denoiser=denoiser)

    # Denoise residual
    rabasar_stack = run_rabasar_residue_filtering(
        sar_stack=sar_stack,
        super_sar_image=super_sar_image,
        number_looks=number_looks,
        denoiser=denoiser,
    )

    return rabasar_stack, super_sar_image
