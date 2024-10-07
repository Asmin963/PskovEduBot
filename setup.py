from setuptools import setup, find_packages

setup(
    name='PskovEduBot',
    url='https://github.com/Asmin963/PskovEduBot',
    packages=find_packages(),
    install_requires=[
        'pyTelegramBotAPI',
    ],
    python_requires='>=3.11',
)
