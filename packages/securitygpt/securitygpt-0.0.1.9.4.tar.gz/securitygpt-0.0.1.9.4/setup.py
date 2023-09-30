import setuptools

DESCRIPTION = 'SecurityGPT, GPT for security practioners'
LONG_DESCRIPTION = """ 
# What is securitygpt ? 
securitygpt is a package that makes makes common tasks that a
security engineer does easy using generative LLMs.  

As a security engineer, you dont want to worry about writing correct prompts, we have taken care of that for you.
# Install
```
pip install securitygpt
export OPENAI_API_KEY="sk-xxx"
```
# Usage and Examples
Current usecases support
 - anonymization and deanonymization of text
 - CVE summaries
 - drawing threat knowledge graphs

[Usage and Examples] (https://github.com/rkreddyp/securitygpt)


send feedback and comments to rkreddy@gmail.com or open issues in GitHub (https://github.com/rkreddyp/securitygpt)

"""

setuptools.setup(
    name="securitygpt",                     # This is the name of the package
    version="0.0.1.9.4",                        # The initial release version
    author="rkreddyp",                     # Full name of the author
    description="SecurityGPT, GPT for security practioners",
    long_description=LONG_DESCRIPTION,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["securitygpt"],             # Name of the python package
    install_requires=[]                     # Install other dependencies if any
)
