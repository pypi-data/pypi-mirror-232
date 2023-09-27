import setuptools

setuptools.setup(
    name='threadinglogger',
    version='0.0.1',
    description='Logger by a thread.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='chorong',
    author_email='chorong8883@gmail.com',
    url='https://github.com/chorong8883/threadinglogger.git',
    # install_requires=['tqdm', 'pandas', 'scikit-learn',],
    packages=setuptools.find_packages(exclude=[]),
    keywords=['logger'],
    python_requires='>=3.10',
    package_data={},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)