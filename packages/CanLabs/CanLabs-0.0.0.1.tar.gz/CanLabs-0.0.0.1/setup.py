from setuptools import setup, find_packages
from version import bump_version
import subprocess

# Appelez la fonction pour augmenter la version
bump_version()

# Mettez à jour le fichier README.rst à partir du fichier README.md
subprocess.run(["pandoc", "README.md", "-o", "README.rst"])

# Read the README.md file
long_description = open('README.rst').read()

# Mettez à jour le fichier requirements.txt freeze
subprocess.run(["pip", "freeze", ">", "requirements.txt"])

# Read the requirements.txt file
requirements = open('requirements.txt').read()

# Avant de créer le package, assurez-vous que le répertoire de build est propre
subprocess.run(["rm", "-rf", "build"])
subprocess.run(["rm", "-rf", "dist"])
subprocess.run(["rm", "-rf", "CanLabs.egg-info"])

# Créez le package
setup(
    name="CanLabs",
    version="0.0.0.1",  # Mettez à jour la version selon votre projet
    # Download pip install CanLabs

    description="Gestion de l'interface CAN avec Python",
    long_description=long_description,
    author="Alexandre Meline",
    author_email="alexandre.meline.dev@gmail.com",
    url="https://github.com/alexandre-meline/CanLabs",
    packages=find_packages(),
    install_requires=[requirements],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        f"License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],

)
