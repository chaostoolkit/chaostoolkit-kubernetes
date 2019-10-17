from setuptools import setup, find_packages

if __name__ == "__main__":
    with open("requirements.txt") as f:
        requirements = list(filter(lambda x: not x.startswith("pytest"), f.read().splitlines()))

    setup(
        name="chaostoolkit-nimble",
        packages=find_packages(),
        description="Guavus Chaos Test automation framework",
        version="0.0.2",
        install_requires=requirements,
        url="https://github.com/kritika-saxena-guavus/chaos_eng_automation",
        author="Core Automation Squad",
        author_email="automation-squad@guavus.com",
        include_package_data=True
    )
