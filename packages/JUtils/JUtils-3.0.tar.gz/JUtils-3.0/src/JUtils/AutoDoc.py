"""This File serves no purpose other then creating documentation for this package. Please do not import it in your scripts!"""

if __name__ == "__main__":
    import os
    from inspect import getmembers, isfunction
    from json import dumps

    #######################################################

    originalwd = os.getcwd()
    os.chdir(originalwd + os.sep + "src" + os.sep + "Jutils")

    #######################################################

    foldername = __file__.split(os.sep)[-2]

    dataStruct = {foldername : {}}

    for file in os.listdir():
        if file.endswith(".py"):
            if file not in ["__init__.py", __file__.split("\\")[-1]]:
                dataStruct[foldername][file.replace(".py", "")] = {}

    for package in dataStruct[foldername].keys():
        exec(f"import {package}")
        exec(f"dataStruct[foldername][package]['doc'] = {package}.__doc__")

        dataStruct[foldername][package]["funcs"] = {}
        funclist = []
        exec(f"funclist = getmembers({package}, isfunction)")
        for name, func in funclist:
            dataStruct[foldername][package]["funcs"][name] = func.__doc__

    #print(os.getcwd())
    #print(dumps(dataStruct, indent=4))
    #######################################################

    readme = f"# {foldername}\n"
    modulestart = r"""
JUtils is a package containing various utility functions i needed now and then, summarized into a single package
and released, in case someone finds the need to use something.
""".strip()
    readme += modulestart + "\n\n"

    readme += "# Table of Contents\n"
    for package in dataStruct[foldername].keys():
        readme += f"* [{package}](#{package.lower()})\n"
    readme += "\n"

    for package, info in dataStruct[foldername].items():
        readme += f"# {package}\n{info['doc']}.\n```py\nfrom {foldername}.{package} import *\n```\n\n"
        for func, funcINFO in info["funcs"].items():
            readme += f"- **{func}**\n```{funcINFO}.\n```\n"

    moduleend = r"""
\
\
\
This Package is not under active development, i will update it every now and then if i find a new function to add.
Please consider emailing me at: [jan@seifert-online.de](mailto:jan@seifert-online.de) if you got any suggestions for improvement.
""".strip()
    readme += moduleend

    #print(readme)
    #######################################################

    os.chdir(originalwd)

    #######################################################

    if os.path.exists("README.md"):
        os.remove("README.md")
    with open("README.md", "x") as f:
        f.write(readme)
