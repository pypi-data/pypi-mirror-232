import setuptools

setuptools.setup(
    name="acid_box",
    version="0.0.0",
    author="Vincent Dary",
    author_email="",
    description="acid-box",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    zip_safe=False,
)
