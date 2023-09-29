from setuptools import setup, find_packages

setup(
    name="vqa_package",
    version="0.1.0",
    description="Visual Question Answering (VQA) package",
    author="Your Name",
    author_email="andreialexbunea@yahoo.com",
    packages=find_packages(),
    install_requires=[
        "torch>=1.8.0",
        "torchvision>=0.9.0",
        "transformers>=4.0.0",
        "Pillow>=8.0.0",
        "scikit-learn>=0.24.0",
        "matplotlib>=3.4.0", 
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="visual-question-answering vqa deep-learning",
)
