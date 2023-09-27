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
from typing import Generic, TypeAlias, TypeVar, Union

from attr import Factory, define
from matplotlib import animation as animation, pyplot as plt
from matplotlib.image import AxesImage
from mulog import (
    RGBImageRenderer,
    SARImageRenderer,
    ScalarImageStack,
)
import numpy as np
from typing_extensions import Self

from rabasar import RGBImageStack

from .multilooking import MatrixFieldStack

SARImageStack: TypeAlias = Union[ScalarImageStack, MatrixFieldStack]
TImageStack = TypeVar("TImageStack", bound=Union[ScalarImageStack, RGBImageStack])


@define
class RGBImageStackRenderer(Generic[TImageStack]):
    image_renderer: RGBImageRenderer

    def render(
        self,
        image_stack: TImageStack,
        normalize: bool = False,
    ) -> TImageStack:
        """
        Render an image for best display.
        :param image_stack: the image to render.
        :param normalize: whether ot not to normalize the output.
        :return: the adjusted image.
        """
        return np.array(
            [
                self.image_renderer.render(
                    image=image,
                    normalize=normalize,
                )
                for image in image_stack
            ]
        )  # type: ignore


@define
class SARImageStackRenderer:
    sar_image_renderer: SARImageRenderer

    @classmethod
    def from_guide(
        cls,
        sar_stack_guide: SARImageStack,
    ) -> Self:
        """
        Instantiate a SAR stack renderer to best capture the dynamic of
        the given image guide.
        """
        return cls(
            sar_image_renderer=SARImageRenderer.from_guide(
                sar_image_guide=sar_stack_guide[0]
            )
        )

    def render(self, sar_stack: SARImageStack) -> RGBImageStack:
        """
        Render a SAR or PolSAR image into a
        :param image: an image of gamma or Wishart distributed observations.
        :return: the image, its minimum value and maximum value.
        """
        return np.array(
            [
                self.sar_image_renderer.render(
                    sar_image=sar_image,
                )
                for sar_image in sar_stack
            ]
        )


@define
class AnimatedImageStackShower:
    @define
    class _Element:
        handle: AxesImage
        axis: plt.Axes  # type: ignore
        image_stack: RGBImageStack
        title: str

    _axis_handle_stack_list: list[_Element] = Factory(list)

    @classmethod
    def _set_title(
        cls, axis: plt.Axes, title: str, frame_number: int  # type: ignore
    ) -> None:
        axis.set_title(f"{title} [frame: {frame_number}]")

    def stackshow(
        self,
        axis: plt.Axes,  # type: ignore
        image_stack: RGBImageStack,
        title: str = "",
    ) -> None:
        self._axis_handle_stack_list.append(
            self._Element(
                axis=axis,
                handle=axis.imshow(image_stack[0]),
                image_stack=image_stack,
                title=title,
            )
        )
        self._set_title(axis=axis, title=title, frame_number=0)

    def show(self, skip: bool = False) -> None:
        figure = self._axis_handle_stack_list[0].handle.figure
        assert isinstance(figure, plt.Figure)  # type: ignore
        number_frames = max(
            [item.image_stack.shape[0] for item in self._axis_handle_stack_list]
        )

        def _animate(i: int):
            for element in self._axis_handle_stack_list:
                k = i % element.image_stack.shape[0]
                element.handle.set_data(element.image_stack[k])
                self._set_title(axis=element.axis, title=element.title, frame_number=k)

        _animation = animation.FuncAnimation(
            figure,
            _animate,  # type: ignore
            frames=number_frames,
            interval=500,
            blit=False,
            repeat=True,
        )
        if not skip:
            plt.show()
        else:
            _animate(0)
            figure.clf()
