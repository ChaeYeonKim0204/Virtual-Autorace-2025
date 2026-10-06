from distutils.core import setup
from catkin_pkg.pyhton_setup import generate_disutils_setup

setup_args = generate_disutils_setup(
    packages=['lane_following'],
    package_dir={":'src'"}
)
setup(**setup_args)