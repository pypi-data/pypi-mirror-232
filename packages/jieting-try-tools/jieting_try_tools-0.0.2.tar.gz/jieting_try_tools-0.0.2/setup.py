from setuptools import find_packages, setup

PACKAGE_NAME = "jieting_try_tools"

setup(
    name=PACKAGE_NAME,
    version="0.0.2",
    description="This is my tools package",
    packages=find_packages(),
    entry_points={
        "package_tools": ["jieting_try_tool_1 = jieting_try_tools.tools.utils:list_package_tools", "jieting_try_tool_2 = jieting_try_tools.tools.utils:list_package_tools"],
    },
    include_package_data=True,   # This line tells setuptools to include files from MANIFEST.in
)