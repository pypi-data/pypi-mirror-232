from setuptools import setup, find_packages

setup(
    name="smb3-video-autosplitter",
    version="1.2.1",
    description=("Ingest video data to render smb3 eh manip stimuli"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="smb3-video-autosplitter",
    author="narfman0",
    author_email="narfman0@blastedstudios.com",
    license="LICENSE",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "dataclass_wizard",
        "opencv-python",
        "pygrabber",
        "pywin32",
        "pyyaml",
    ],
    test_suite="tests",
)
