#! /usr/bin/env sh
# -* sh *-

# Install the tovid suite of tools

# Become root if needed
if test $UID -ne 0; then
    echo "Please enter the root password to install tovid system-wide"
    su -c './setup.sh'
    exit
fi

# First, the scripts
echo "Making and installing the executables..."
if make install; then :
else
  echo "Could not make and intall the executables!"
  echo "Did you run ./configure first?"
  echo "If so, try \"su -c 'make install'\""
  exit 1
fi

# Then, the python libraries
# Make the install script
sed -i "s:^#!.*:#! `command -v python`:" setuplib
chmod ugo+x setuplib

# Install the libraries
echo "Installing the python libararies..."
if ./setuplib install; then :
else
  echo "Could not install the python libraries!"
  echo "Try \"su -c './setup'\""
  exit 1
fi

echo "---------------------"
echo "Done installing tovid. See the tovid homepage (http://tovid.org/)"
echo "or read the manual page ('man tovid') for help."
exit 0
