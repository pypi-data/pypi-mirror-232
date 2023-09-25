"""
MIT License

Permission is hereby granted, free of charge, to Alexandre Meline
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

Copyright (c) 2023 Alexandre Meline

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from setuptools import setup, find_packages
from version import *
import subprocess
import os

print(get_latest_version("CanLabs"))

def delete_package_components():
    # Supprimez les composants du package s'ils existent
    if os.path.exists("build/CanLabs"):
        subprocess.run(["rm", "-rf", "build/CanLabs"])
    if os.path.exists("dist/CanLabs"):
        subprocess.run(["rm", "-rf", "dist/CanLabs"])
    if os.path.exists("CanLabs.egg-info"):
        subprocess.run(["rm", "-rf", "CanLabs.egg-info"])
    return True

def update_readme_file_for_pypi():
    # Mettez à jour le fichier README.rst à partir du fichier README.md
    if subprocess.run(["pandoc", "README.md", "-o", "README.rst"], check=True).returncode == 0:
        print("Le fichier README.rst a été mis à jour avec succès.")
        return True
    
def get_long_description():
    # Lisez le fichier README.md
    long_description = open('README.rst').read()
    return long_description

def get_requirements():
    # Mettez à jour le fichier requirements.txt
    if subprocess.run(["pip", "freeze", ">", "requirements.txt"], check=True).returncode == 0:
        print("Le fichier requirements.txt a été mis à jour avec succès.")
        # Lisez le fichier requirements.txt
        requirements = open('requirements.txt').read()
        return requirements
    
def update_repository_github():
        # Envoyez le repository sur GitHub
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"Update version: {get_latest_version('CanLabs')}"])
        # Si la commande réussit, poussez le repository sur GitHub
        if subprocess.run(["git", "push"], check=True).returncode == 0:
            print("Le repository a été envoyé sur GitHub avec succès.")

delete_package_components()

setup(
    name="CanLabs",
    version="0.1.0.3",  
    description="Gestion de l'interface CAN avec Python",
    long_description=get_long_description(),
    author="Alexandre Meline",
    author_email="alexandre.meline.dev@gmail.com",
    url="https://github.com/alexandre-meline/CanLabs",
    packages=find_packages(),
    install_requires=[get_requirements()],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)

update_repository_github()


"""class PackageManager:
    def __init__(self):
        self.latest_version = ""
    
    def update_version(self, component="PATCH"):
        # Obtenez la dernière version depuis PyPI en utilisant une fonction
        # Mettez en œuvre votre propre logique pour obtenir la dernière version
        # Ici, nous utilisons une valeur factice pour l'exemple
        self.latest_version = get_latest_version(component)

    def update_readme_file_for_pypi(self):
        # Mettez à jour le fichier README.rst à partir du fichier README.md
        if subprocess.run(["pandoc", "README.md", "-o", "README.rst"], check=True).returncode == 0:
            print("Le fichier README.rst a été mis à jour avec succès.")
            return True
    
    def get_long_description(self):
        # Lisez le fichier README.md
        long_description = open('README.rst').read()
        return long_description

    def get_requirements(self):
        # Mettez à jour le fichier requirements.txt
        if subprocess.run(["pip", "freeze", ">", "requirements.txt"], check=True).returncode == 0:
            print("Le fichier requirements.txt a été mis à jour avec succès.")
            # Lisez le fichier requirements.txt
            requirements = open('requirements.txt').read()
            return requirements

    def delete_package_components(self):
        # Supprimez les composants du package s'ils existent
        if os.path.exists("build/CanLabs"):
            subprocess.run(["rm", "-rf", "build/CanLabs"])
        if os.path.exists("dist/CanLabs"):
            subprocess.run(["rm", "-rf", "dist/CanLabs"])
        if os.path.exists("CanLabs.egg-info"):
            subprocess.run(["rm", "-rf", "CanLabs.egg-info"])
        return True

    def setup_package(self):
        # Créez le package
        setup(
            name="CanLabs",
            version=self.latest_version,  
            description="Gestion de l'interface CAN avec Python",
            long_description=self.get_long_description(),
            author="Alexandre Meline",
            author_email="alexandre.meline.dev@gmail.com",
            url="https://github.com/alexandre-meline/CanLabs",
            packages=find_packages(),
            install_requires=[self.get_requirements()],
            classifiers=[
                "Development Status :: 4 - Beta",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
            ],
        )

    def build_and_send_package(self):
        # Si la commande réussit, envoyez le package sur PyPI
        if subprocess.run(["python", "setup.py", "sdist", "bdist_wheel"], check=True).returncode == 0:
            print("Le package a été créé avec succès.")
            if subprocess.run(["python", "-m", "twine", "upload", "--repository", "pypi", "dist/*"], check=True).returncode == 0:
                print("Le package a été envoyé sur PyPI avec succès.")

    def send_repository_to_github(self):
        # Envoyez le repository sur GitHub
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"Update version: {self.latest_version}"])
        # Si la commande réussit, poussez le repository sur GitHub
        if subprocess.run(["git", "push"], check=True).returncode == 0:
            print("Le repository a été envoyé sur GitHub avec succès.")

if __name__ == "__main__":

    # Créez une instance de CanLabsPackageManager
    package_manager = PackageManager()

    # Obtenez la dernière version depuis PyPI (ou utilisez votre propre logique)
    latest_version = package_manager.update_version()

    print(f"La dernière version de CanLabs est {latest_version}.")

    # Mettez à jour le fichier README.rst pour PyPI
    if package_manager.update_readme_file_for_pypi():
        print("README.rst mis à jour pour PyPI.")

    # Obtenez la description longue à partir de README.md
    long_description = package_manager.get_long_description()

    # Obtenez les dépendances à partir de requirements.txt
    requirements = package_manager.get_requirements()

    # Supprimez les composants du package s'ils existent
    package_manager.delete_package_components()

    # Configuration du package
    setup(
            name="CanLabs",
            version=latest_version,  
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
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python :: 3.8",
                "Programming Language :: Python :: 3.9",
                "Programming Language :: Python :: 3.10",
            ],
        )

    # Build et envoi du package sur PyPI
    #package_manager.build_and_send_package()

    # Envoyez le repository sur GitHub
    package_manager.send_repository_to_github()

    print("Le package CanLabs a été créé, envoyé sur PyPI et le repository a été poussé sur GitHub avec succès.")"""

