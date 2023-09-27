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
import argparse

import matplotlib.pyplot as plt
from mulog import (
    PREDEFINED_GAUSSIAN_DENOISER_NAMES_TO_DENOISER,
    PredefinedGaussianDenoiserNames,
)

from .rabasar_algorithm import run_rabasar
from .sar_image_stack_generation import (
    generate_mondrian_image_stack,
    generate_speckle_stack,
    simulate_polsar_stack_from_rgb_stack,
)
from .sar_image_stack_rendering import AnimatedImageStackShower, SARImageStackRenderer


def run_rabasar_synthetic_example(
    number_looks: int,
    gaussian_denoiser_name: PredefinedGaussianDenoiserNames,
    show: bool = True,
):
    ideal_polsar_stack = simulate_polsar_stack_from_rgb_stack(
        image_stack=generate_mondrian_image_stack()
    )
    speckled_polsar_stack = generate_speckle_stack(
        sar_stack=ideal_polsar_stack,
        number_looks=number_looks,
    )
    rabasar_polsar_stack, rabasar_polsar_super_image = run_rabasar(
        sar_stack=speckled_polsar_stack,
        number_looks=number_looks,
        denoiser=PREDEFINED_GAUSSIAN_DENOISER_NAMES_TO_DENOISER[gaussian_denoiser_name],
    )

    sar_stack_render = SARImageStackRenderer.from_guide(
        sar_stack_guide=ideal_polsar_stack
    )

    _, axes = plt.subplots(ncols=2, nrows=2, figsize=(16, 10), sharex=True, sharey=True)
    image_stack_shower = AnimatedImageStackShower()
    image_stack_shower.stackshow(
        axis=axes[0][0],
        image_stack=sar_stack_render.render(ideal_polsar_stack),
        title="Synthetic speckle-free PolSAR stack",
    )
    image_stack_shower.stackshow(
        axis=axes[1][0],
        image_stack=sar_stack_render.render(speckled_polsar_stack),
        title="Synthetic PolSAR stack with speckle",
    )
    image_stack_shower.stackshow(
        axis=axes[0][1],
        image_stack=sar_stack_render.render(rabasar_polsar_stack),
        title="Synthetic PolSAR stack processed by RABASAR",
    )
    axes[1][1].imshow(
        sar_stack_render.sar_image_renderer.render(rabasar_polsar_super_image),
    )
    axes[1][1].set_title("Synthetic PolSAR super image processed by MuLoG")
    image_stack_shower.show(skip=not show)


if __name__ == "__main__":
    """
    Examples:

       python mulog_synthetic_example.py --help
       python mulog_synthetic_example.py -l 1
       python mulog_synthetic_example.py --number_looks 3

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--number_looks",
        type=int,
        default=1,
        help="Number of looks or Equivalent Number of Looks (ENL)",
    )
    parser.add_argument(
        "-g",
        "--gaussian_denoiser_name",
        type=PredefinedGaussianDenoiserNames,
        default=PredefinedGaussianDenoiserNames.TV,
        help=(
            f"Gaussian denoiser name, one of "
            f"{[name.value for name in PredefinedGaussianDenoiserNames]}"
        ),
    )
    args = parser.parse_args()

    run_rabasar_synthetic_example(
        number_looks=args.number_looks,
        gaussian_denoiser_name=args.gaussian_denoiser_name,
    )
