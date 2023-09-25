from setuptools import setup, find_packages

setup(
    name="gptq_Quantizer",
    version="1.0",
    author="Kirouane Ayoub",
    author_email="ayoubkirouane3@email.com",
    description="A Python package for GPTQ quantization",
    packages=find_packages(),
    install_requires=[
        'transformers' ,'torch' , 'optimum==1.13.2', 'auto-gptq==0.4.2'],
)
