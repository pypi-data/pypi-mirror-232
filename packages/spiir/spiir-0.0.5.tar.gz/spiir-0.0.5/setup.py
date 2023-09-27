from setuptools import find_packages, setup

# specify optional dependencies
igwn_alert_requires = ["igwn-alert", "toml"]
p_astro_requires = [
    "scikit-learn>=1.0",
    "pycbc",
    "spiir-p-astro",
]
sealgw_requires = ["sealgw"]

extras_require = {
    "p-astro": p_astro_requires,
    "igwn-alert": igwn_alert_requires,
    "sealgw": sealgw_requires,
}

extras_require["all"] = [pkg for pkgs in extras_require.values() for pkg in pkgs]

setup(
    name="spiir",
    version="0.0.5",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "wheel",
        "setuptools",
        "lalsuite",
        "astropy",
        "python-ligo-lw>=1.8.1",
        "ligo.skymap",
        "ligo-gracedb",
        "numpy>=1.23",
        "scipy",
        "pandas<2.0.0",
        "matplotlib",
        "click",
    ],
    extras_require=extras_require,
    description="A Python library for the SPIIR gravitational wave science pipeline.",
    author="Tim Davies, Luke Davis, Manoj Kovalam, Daniel Tang",
    author_email="tim.davies@uwa.edu.au, luke.davis@uwa.edu.au, manoj.kovalam@uwa.edu.au, daniel.tang@uwa.edu.au",
)
