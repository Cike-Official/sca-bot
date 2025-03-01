# Description: How to access the value of an environment variable within a Python script
# Without using the dotenv library.

"""
import os

myvar = os.environ['FREE']
# Note: set the value of the environment variable 'FREE' in terminal before running this script
# i.e.: export FREE="Env Var Value"     this is a temporary setting
# or:   echo 'export FREE="Env Var Value"' >> ~/.zshrc     this is a permanent setting

print(myvar)
"""