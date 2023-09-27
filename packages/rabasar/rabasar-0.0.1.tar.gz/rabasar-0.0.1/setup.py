from setuptools import find_packages, setup

PACKAGE_NAME: str = "rabasar"
REQUIREMENTS_FILENAME: str = "requirements.txt"
README_FILENAME: str = "README.md"


def find_required_packages(
    requirements_filename: str = REQUIREMENTS_FILENAME,
) -> list[str]:
    with open(requirements_filename, "rt") as f:
        all_lines = f.read().splitlines()

    required_packages = []
    in_required_section = False
    for package in all_lines:
        if package == "":
            continue
        if package == "# required":
            in_required_section = True
            continue
        elif package[0] == "#":
            in_required_section = False
        if in_required_section:
            required_packages.append(package)
    return required_packages


if __name__ == "__main__":
    with open("README.md", "rt") as f:
        readme_text = f.read()

    setup(
        name=PACKAGE_NAME,
        version="0.0.1",
        author="Charles Deledalle, Sébastien Mounier, Cristiano Ulondu Mendes",
        author_email="charles.deledalle@gmail.com",
        url="https://www.charles-deledalle.fr/pages/rabasar",
        description=(
            "Ratio-Based Multitemporal SAR Images Denoising "
            "- A (Pol/In)SAR image stack speckle reduction algorithm."
        ),
        long_description_content_type="text/markdown",
        long_description=readme_text,
        keywords="SAR,PolSAR,InSAR,speckle,filtering,images,wishart,temporal,stack",
        license="cecill",
        packages=find_packages(exclude=["tests", "tests.*"]),
        install_requires=find_required_packages(),
        python_requires=">=3.10",
        project_urls={
            "Source": "https://bitbucket.org/charles_deledalle/rabasar2019-python/",
        },
    )
