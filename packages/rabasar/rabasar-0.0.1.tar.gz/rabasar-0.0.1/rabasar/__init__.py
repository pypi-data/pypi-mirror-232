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
from .multilooking import (
    compute_sar_super_image as compute_sar_super_image,
    estimate_number_looks as estimate_number_looks,
    inverse_compute_fisher_tippet_noise_std as inverse_compute_fisher_tippet_noise_std,
)
from .rabasar_algorithm import (
    run_rabasar as run_rabasar,
    run_rabasar_residue_filtering as run_rabasar_residue_filtering,
)
from .sar_image_stack_generation import (
    RGBImageStack as RGBImageStack,
    generate_mondrian_image_stack as generate_mondrian_image_stack,
    generate_speckle_stack as generate_speckle_stack,
    simulate_polsar_stack_from_rgb_stack as simulate_polsar_stack_from_rgb_stack,
)
from .sar_image_stack_rendering import (
    AnimatedImageStackShower as AnimatedImageStackShower,
    RGBImageStackRenderer as RGBImageStackRenderer,
    SARImageStack as SARImageStack,
    SARImageStackRenderer as SARImageStackRenderer,
)
