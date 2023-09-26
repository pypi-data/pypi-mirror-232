"""
DDI Transformations
"""

from setuptools import find_packages, setup

setup(
    version="0.0.1",
    name="ddi_transformations",
    description="DDI Transformations",
    package_dir = {"": "src"},
    packages = find_packages(where="src"),
    python_requires = ">=3.6",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Jinja2==3.1.2"
    ]
)
