from setuptools import setup, find_packages

setup(
    name='ecoindex-journey-scrapper',
    version='1.0.1',
    packages=find_packages(),
    description='Calcul du lecoindex du un parcours',
    author='Orange Inovation',
    install_requires=[
        "ecoindex>=5.4.2",
        "undetected-chromedriver==3.4.6",
        "Pillow>=9.2.0",
        "selenium==4.9",
        "jinja2>=3.1.0"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # Again, pick a license
        'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
