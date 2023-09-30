from setuptools import find_packages, setup

PACKAGE_NAME = "skpf"


setup(
    name="skpf",
    version="0.0.1",
    description="This package contains promptflow tools for working with Smenatic Kernel.",
    packages=find_packages(),
    install_requires=[
        'semantic_kernel'
    ],
    entry_points={
        "package_tools": ["query = skpf.tools.utils:list_package_tools"],
    },
    include_package_data=True,   # This line tells setuptools to include files from MANIFEST.in
)