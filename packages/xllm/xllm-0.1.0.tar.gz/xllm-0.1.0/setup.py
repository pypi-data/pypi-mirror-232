from setuptools import find_packages, setup

# Extras
extras = dict()

extras["quality"] = [
    "black",
    "mypy",
    "mypy-extensions",
    "pre-commit",
    "ruff",
]

extras["tests"] = [
    "pytest",
    "coverage",
    "pytest-html",
    "pytest-cov",
]

extras["dev"] = extras["quality"] + extras["tests"]

extras["deepspeed"] = ["deepspeed"]

extras["flash-attn"] = ["flash-attn>=2.2.1"]

extras["train"] = extras["deepspeed"] + extras["flash-attn"]

extras["all"] = extras["train"] + extras["dev"]

# Install deps
install_requires = [
    "numpy>=1.17",
    "packaging>=20.0",
    "psutil",
    "torch>=2.0.0",
    "loguru",
    "peft>=0.5.0",
    "wandb",
    "python-dotenv",
    "requests",
    "optimum>=1.12.0",
    "bitsandbytes>=0.41.1",
    "scipy",
    "transformers",
    # "transformers>=4.33.1",
    # "https://github.com/huggingface/transformers",  # temporarily for mistral
    "tqdm",
    "safetensors",
]

# Setup
setup(
    name="xllm",
    version="0.1.0",
    description="Simple & Cutting Edge LLM Finetuning",
    license_files=["LICENSE"],
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="deep learning",
    license="Apache",
    author="BobaZooba",
    author_email="bobazooba@gmail.com",
    url="https://github.com/kompleteai/xllm",
    package_dir={"": "src"},
    packages=find_packages("src"),
    package_data={"xllm": ["py.typed"]},
    entry_points={},
    python_requires=">=3.8.0",
    install_requires=install_requires,
    extras_require=extras,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    dependency_links=["git+https://github.com/huggingface/transformers@main"],
)
