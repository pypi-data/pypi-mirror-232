This is a Python 3.10 implementation of RABASAR as described in [4].

RABASAR reduces the speckle in multi-temporal intensity, polarimetric or interferometric
Synthetic-Aperture-Radar (SAR, PolSAR, InSAR, resp.) images by first  computing a super
image with a high signal-to-noise ratio, and then processes the residuals between the
multi-temporal stack and the super-image.

# Description

RABASAR is a plug-and-play ADMM approach for speckle reduction in a stack of
(Pol/In)SAR images. It is based on MuLoG and the concepts of super image. It
uses an off-the-shelf Gaussian denoiser and matrix logarithm transform to stabilized
noise and simplify the optimization occuring for denoising the residual matrix fields
between  each image of the stack and the super image.

**REMARK**: Compared to the version of RABASAR described in [3], this one:
1. is not limited to monochanel intensity SAR image. It can be applied like-wise
   to mutli-channel SAR image such as PolSAR, InSAR, PolInSAR.
2. does not account for the statistics of the ratio-images (the z-Fisher distribution
   of the log of ratio of intensity image). Instead the noise of the log ratio is
   approximated by the Wishart-Fisher-Tippet distribution. For the approximation
   error to be negligeable, the stack of images must be large enough and ideally
   with enough pairs presenting low temporal coherence.

# Installation

Unless you have Python 3.10 installed and enabled as default, we recommend
installing RABASAR in a virtual environment as described in the following section.

## Set up a virtual environment (optional)

We recommend installing RABASAR in a virtual environment such as `venv`. You can
install `venv` for Python 3.10 on Debian/Ubuntu as follows:

	sudo apt install python3.10-venv

If your system does not have Python 3.10, please refer to the "Troubleshooting"
section below.

Create and activate your virtual environment by running the following either directly
in the directory in which you will execute or clone RABASAR or in a parent directory, as

	python3 -m venv venv
	source venv/bin/activate

Alternatively, you can use other environment systems such as `conda`.

## Latest stable version

We recommend installing the latest stable version of RABASAR by running

	pip3 install rabasar

in a system or environment with Python 3.10.

## Development version

Alternatively, you can install the development version from `git` as

	pip3 install -e git+https://bitbucket.org/charles_deledalle/rabasar2019-python.git#egg=rabasar

or, directly from the sources as

	git clone https://bitbucket.org/charles_deledalle/rabasar2019-python.git
	cd rabasar2019-python
	python3 setup.py sdist
	python3 setup.py install

# Run RABASAR

Examples on how to run RABASAR are provided in two scripts that you can execute as:
```shell
# Run RABASAR on a multlooked synthetic PolSAR image stack with 5 looks
python3 -m rabasar.rabasar_synthetic_example -l 5
```
For more precisions on how to execute these examples, see:

	python3 -m rabasar.rabasar_synthetic_example --help

To run RABASAR on your own data, you need to execute from Python the function
called `run_rabasar` that you can import as:

	from rabasar.rabasar_algorithm import run_rabasar

This function takes your data as input through the argument `sar_stack`
which has the format of a covariance matrix field (an image of non negative
definite complex Hermitian matrices). It's your responsibility to load and
format your data in Python to make it compatible with this input. SAR, InSAR,
PolSAR, DualPolSAR PolInSAR images can be formatted as such a matrix field. For
more details, please read [1-4].

# List of the files in this folder

- ```multilooking.py```

The code to compute the "super-image" of a temporal series of polarimetric images by
averaging them and applying optionally MuLoG on the result with an estimated number
of looks.

- ```rabasar_algorithm.py```

Implementation of RABASAR for polarimetric SAR images.

- ```rabasar_synthetic_example.py```

A cli tool to run RABASAR on a synthetic example.

- ```sar_image_stack_generation.py```

Tools to generate synthetic mono-channel and multichannel SAR image stacks.

- ```sar_image_stack_rendering.py```

Tools to render synthetic mono-channel and multichannel SAR image stacks.

# Developers

## Set up

Clone the git repository on your machine:

	git clone https://bitbucket.org/charles_deledalle/rabasar2019-python.git
	cd rabasar2019-python

Set up a Python 3.10 virtual environment as described in the Installation section above.
Once your virtual environment is set up and activated, install dependencies as

	pip3 install -r requirements.txt

## Contribution

Any contributions must be submitted through peer reviews.
Ask for an author account on the bitbucket repository,
create your own branch and raise a pull-request.
All additional code must be cover by a unit test.
Any pull request needs to pass the following commands before being approved:

	black .
	ruff --fix .
	pyright .
	python3 -m pytest --cov

If the last one does not have a 100% test coverage, run:

	python3 -m pytest --cov --cov-report=html

and inspect the report.

Make sure to update `requirements.txt` to include any extra dependencies.

## Distribution

To distribute the project make sure to uptick the version number in `setup.py`
and merge that upticked version on the `master` branch.
Once the `master` branch is ready, run the following

	git checkout master
	cd $(git rev-parse --show-toplevel)
	rm -rf dist/ build/ rabasar.egg-info/
	git status --porcelain

and make sure the last command did not print anything.
After that, generate the distribution files by running

	python3 setup.py sdist bdist_wheel
	python3 -m twine check dist/*
	python3 -m twine upload -r testpypi dist/*

Test in a different environment

	mkdir /tmp/test
	cd /tmp/test
	python3 -m venv venv
	source venv/bin/activate
	pip3 install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ rabasar
	python3 -m rabasar.rabasar_synthetic_example -l 5

Finally, publish the final version

	python3 -m twine upload dist/*

Once done, tag the `master` branch with the new version number on Git.

# License

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

# Contributors

- Charles Deledalle (original version in Matlab)
- Sébastien Mounier (translation in Python)
- Cristiano Ulondu Mendes (bug fixes and improvements)

# Scientific articles describing the method

Any published materials derived from MuLoG must cite [1-2].
Any published materials derived from RABASAR must cite [3-4].

[1] Deledalle, C. A., Denis, L., Tabti, S., & Tupin, F. (2017). MuLoG,
    or how to apply Gaussian denoisers to multi-channel SAR speckle
    reduction?. IEEE Transactions on Image Processing, 26(9), 4389-4403.

[2] Deledalle, C. A., Denis, L., & Tupin, F. (2022). Speckle reduction
    in matrix-log domain for synthetic aperture radar imaging. Journal
    of Mathematical Imaging and Vision, 64(3), 298-320.

[3] Zhao, W., Deledalle, C. A., Denis, L., Maître, H., Nicolas, J. M.,
    & Tupin, F. (2019). Ratio-based multitemporal SAR images denoising:
    RABASAR. IEEE Transactions on Geoscience and Remote Sensing, 57(6),
    3552-3565.

[4] Deledalle, C. A., Denis, L., Ferro-Famil, L., Nicolas, J. M., &
    Tupin, F. (2019, July). Multi-temporal speckle reduction of
    polarimetric SAR images: A ratio-based approach. In IGARSS 2019-2019
    IEEE International Geoscience and Remote Sensing Symposium (pp. 899-
    902). IEEE.
