from setuptools import setup, find_packages

setup(
    name='wbparser',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'scrapy',
        # ...
    ],
    url='https://github.com/maxim-lixakov/WildBerriesParser',
    author='Maxim Liksakov',
    author_email='lixakov.maksim@yandex.ru',
    description='WB parser (async)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
