# To run our project in a docker

# step1.

open the terminal and cwd to current folder openleader-python

# step2.

usr$ sudo docker build -t openleader-python .

# step3.(if test on a local host)

usr$ sudo docker run -it -p 5000:5000 openleader-python

# ====================================================================================================

## if you don't want to run it in a docker

# First install the virtualenv packages

usr$ pip3 install virtualenv

# Set the virtualenv version, notice that we can only set the python version number we have at the system level

# Besides, asyncio only supports python version which is lower than or equal to 3.8.0

usr$ virtualenv python_env --python=python3.8

# Then active our python_env

usr$ source python_env/bin/activate

# Install our packeages once in the requirements.txt

(python_env)usr$ pip3 install -r dev_requiremnets.txt

# Running the VEN server

(python_env)usr$ python main.py

# Command for exiting python_env

(python_env)usr$ deactivate
