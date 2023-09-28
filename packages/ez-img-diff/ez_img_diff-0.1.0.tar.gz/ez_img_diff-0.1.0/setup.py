"""Contains all the configuration for the package on pip"""
import setuptools
from ez_img_diff import __version__

def get_content(*filename:str) -> str:
    """ Gets the content of a file or files and returns
    it/them as a string
    Parameters
    ----------
    filename : (str)
        Name of file or set of files to pull content from 
        (comma delimited)
    
    Returns
    -------
    str:
        Content from the file or files
    """
    content = ""
    for file in filename:
        with open(file, "r") as full_description:
            content += full_description.read()
    return content

setuptools.setup(
    name = "ez_img_diff",
    version = __version__,
    author = "Kieran Wood",
    author_email = "kieran@canadiancoding.ca",
    description = "A tool for doing quick perceptual image difference analysis",
    long_description = get_content("README.md"),
    long_description_content_type = "text/markdown",
    project_urls = {
        "API Docs"  :      "https://kieranwood.ca/ez_img_diff",
        "Source" :         "https://github.com/Descent098/ez-img-diff",
        "Bug Report":      "https://github.com/Descent098/ez-img-diff/issues/new?assignees=Descent098&labels=bug&template=bug_report.md&title=%5BBUG%5D",
        "Feature Request": "https://github.com/Descent098/ez-img-diff/issues/new?labels=enhancement&template=feature_request.md&title=%5BFeature%5D",
        "Roadmap":         "https://github.com/Descent098/ez-img-diff/projects"
    },
    include_package_data = True,
    packages = setuptools.find_packages(),
    
    entry_points = { 
           'console_scripts': ['img_diff = ez_img_diff.cli:main']
       },

    install_requires = [
    "docopt", # Used for argument parsing if you are writing a CLI
    "scikit-image",
    "imutils",
    "opencv-python",
        ],
    extras_require = {
        "dev" : ["nox",    # Used to run automated processes
                "pytest",  # Used to run the test code in the tests directory
                "mkdocs"], # Used to create HTML versions of the markdown docs in the docs directory

    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning"
    ],
)