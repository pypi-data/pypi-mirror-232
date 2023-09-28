from setuptools import setup, find_packages

setup(
    name='ecoindex_journey_scraper',
    version='1.0.2',
    packages=find_packages(where='src'),
    description='Calcul du lecoindex du un parcours',
    author='Orange Innovation',
    install_requires=[
        "ecoindex>=5.4.2",
        "undetected-chromedriver==3.4.7",
        "Pillow>=9.2.0",
        "selenium==4.9",
        "jinja2>=3.1.0",
        "ecoindex_scraper"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',  # Add this to specify OS compatibility
    ],
    python_requires=">=3.8",
    py_modules=["ecoindex_journey_scraper"],  # Correct the module name
    package_dir={'': 'src'},
)