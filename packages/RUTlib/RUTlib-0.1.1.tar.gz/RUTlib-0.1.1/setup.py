from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Operating System :: Microsoft :: Windows :: Windows 10",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

setup(
    name="RUTlib",
    version="0.1.1",
    description="A library to handle and validate Chilean RUT",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # Reemplaza 'tu_usuario' con tu usuario de GitHub
    url="https://github.com/RUTlib/rutlib-py",
    author="Felipe Vergara",  # Reemplaza 'Tu Nombre' con tu nombre
    author_email="rutlibteam@gmail.com",  # Reemplaza con tu correo
    license="MIT",
    classifiers=classifiers,
    keywords=["RUT", "Chile", "validation"],
    packages=find_packages(),
    install_requires=[],
)
