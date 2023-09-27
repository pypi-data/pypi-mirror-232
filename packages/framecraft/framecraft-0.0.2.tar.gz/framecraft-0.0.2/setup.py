from setuptools import setup, find_packages

setup(
    name='framecraft',
    version='0.0.2',
    description='by hyeonwoo jeong',
    author='hyeonu',
    author_email='hyeonu4945@gmail.com',
    url='https://github.com/HyeonuJeong/frame_craft',
    install_requires=['tqdm', 'pandas', 'scikit-learn',],
    packages=find_packages(exclude=['opencv-python','concurrent','multiprocessing']),
    keywords=['frame','video','capture'],
    python_requires='>=3.8',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)