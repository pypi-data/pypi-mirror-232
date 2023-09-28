from setuptools import setup, find_packages

setup(
    name='PlantLidar',
    version='1.0.0',
    author='ThreeCats',
    author_email='s1729041183@gmail.com',
    description='PointCloud analysis focus on solving 3D phenotypes of plants and remote sensing problems',
    packages=find_packages(),
    install_requires=[
        'open3d',
        'numpy',
        'pandas',
        'CSF',
        'tqdm',
        'matplotlib',
        'scipy'
    ],
    keywords=['point cloud','lidar','plant','phenotypes','data analysis','remote sensing']
    
)
