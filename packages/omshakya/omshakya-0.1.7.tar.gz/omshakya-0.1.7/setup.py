
# ############ use/uncomment to pulich to pypi
import setuptools 
if __name__ == "__main__": 
   setuptools.setup()


# ############ use/uncomment for local installation
# import omshakya._bin_cc_or_sc.__version__ as v
# __VERSION__ = v.__VERSION__
# print(__VERSION__)

# from setuptools import setup, find_packages
# setup(name = 'omshakya',
#       version = '0.1.5',
#       packages = find_packages(),
#       description = '''A package created by om shakya, this provides several interfaces to sql
#       , mongodb, azure service bus, and other utility functions.
#       The author of the package call it "half done" and most of the re-usable code is modularize and
#       the developer can focus on the main business logics.''',
#       url = 'https://www.linkedin.com/in/om-shakya-49759120',
#       author = 'om shakya',
#       author_email = 'ommshakya@gmail.com',
#       license = 'MIT',
#       zip_safe = False
#       )


# ############# not working at all
# from setuptools import setup, find_packages
# setup(
#     name = 'omshakya',
#     version = '0.1',
#     packages = find_packages(),
#     install_requires = [
#         # list any dependencies your package has
#     ],
# )