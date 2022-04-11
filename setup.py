from distutils import extension
from distutils.command.clean import clean
from sys import flags
import setuptools
import distutils.core
import Cython.Build
import Cython.Distutils
#build everything into the Optimized folder, including .pyd files
build_directory = "Optimized/build"
pyd_directory = "Optimized/pyd"
ext_modules = Cython.Build.cythonize(
    ["Patterns.py", "lightingControl.py", "NetworkTableManager.py"], language_level=3, build_dir=build_directory, include_path=["."], force=True)
#build_ext -i clean
distutils.core.setup(cmdclass={"build_ext": Cython.Distutils.build_ext, "clean": clean}, ext_modules=ext_modules, name="lightingControl", options={"build_ext": {"build_lib": pyd_directory}})

