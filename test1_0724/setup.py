from distutils.core import setup
from catkin_pkg.pyhton_setup import generate_disutils_setup

setup_args = generate_disutils_setup(
    packages=['test1_0724'],
    package_dir={":'src'"}
)
setup(**setup_args)