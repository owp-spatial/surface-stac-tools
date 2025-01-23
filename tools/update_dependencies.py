# Script for reading the requirements.txt and 
# updating the pyproject.toml dependencies block based on the requirements.txt file

import toml

# requirements.txt
with open("requirements.txt", "r") as req_file:
    requirements = req_file.readlines()

# get the dependencies from requirements.txt
dependencies = {}
for req in requirements:
    package = req.strip()
    print(f"req: {req}\npackage: {package}")
    if "==" in package:
        name, version = package.split("==")
        dependencies[name] = ["==", version]
    elif ">=" in package:
        name, version = package.split(">=")
        dependencies[name] = [">=", version]
    elif "<=" in package:
        name, version = package.split("<=")
        dependencies[name] = ["<=", version]
    elif ">" in package:
        name, version = package.split(">")
        dependencies[name] = [">", version]
    elif "<" in package:
        name, version = package.split("<")
        dependencies[name] = ["<", version]
    else:
        dependencies[package] = ["*"]

dependencies_list = []
for key, value in dependencies.items():
    dependencies_list.append(f"{key}{value[0]}{value[1]}")

# print("\n".join([f'"{dep}",' for dep in dependencies_list]))

# load the current pyproject.toml
pyproject_file = "pyproject.toml"
with open(pyproject_file, "r") as toml_file:
    pyproject = toml.load(toml_file)

pyproject['project']['dependencies'] = dependencies_list

# write the updated pyproject.toml
with open(pyproject_file, "w") as toml_file:
    toml.dump(pyproject, toml_file)

print("Dependencies from requirements.txt have been added to pyproject.toml!")