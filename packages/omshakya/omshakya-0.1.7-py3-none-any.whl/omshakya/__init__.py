from ._bin_cc_or_sc import __version__ as v
__version__ = v.__VERSION__

def evaluate_package_requirements():
    """
    Evaluate the current project environment to check the required packages.

    As of now, the following packages are required to use this package 'omshakya':
    1. pandas
    2. sqlalchemy
    3. pymongo

    It will check and report the status on screen/console.
    """
    print('evaluating package requirements...')
    import pkg_resources
    packages = ['pandas', 'sqlalchemy', 'pymongo']
    print('===='*16)
    
    installed = ''
    notinstalled = ''
    toinstall = ''
    for package in packages:
        try:	
            dist = pkg_resources.get_distribution(package)
            installed = installed + f'"{dist}" is installed\n'
        except pkg_resources.DistributionNotFound:
            notinstalled = notinstalled + f'"{package}" is not installed\n'
            toinstall = toinstall + f'pip install {package}\n'
    
    if not(notinstalled == ''):
        print(f'sad!, this package "omshakya" depends on these packages')
        print(f'{notinstalled}')
        print(f'please install,')
        print(f'{toinstall}')
    else:
        print(f'congratulation!, all the required packages are installed,')
        print(f'{installed}')
    print('===='*16)