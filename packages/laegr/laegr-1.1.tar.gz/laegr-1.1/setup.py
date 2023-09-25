import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="laegr",                            
    version="1.1",                            
    author="Yi Yao, Lin Li",
    author_email="yyao26@crimson.ua.edu",                        
    description="Python package to extract graph structure of local atomic environment and build GNN to predict atomic properties (Potential Energy)",
    long_description=long_description,          
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),        
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                         
    python_requires='>=3.8',                  
    py_modules=["laegr"],                   
    # package_dir={'':'LAEGR/src'},            
    install_requires=[]                       
)