# -* sh *-

# Install the tovid suite of tools

# First, the scripts
echo "Making and installing the executables..."
if make install; then :
else
  echo "Could not make and intall the executables!"
  echo "Try \"su -c 'make install'\""
  exit 1
fi

# Then, the python libraries
# Make the install script
rm -f "setuplib"
echo "#! `which env` python"  > setuplib
cat setuplib.py >> setuplib
chmod ugo+x setuplib

# Install the libraries
echo "Installing the python libararies..."
if ./setuplib install; then :
else
  echo "Could not install the python libraries!"
  echo "Try \"su -c './setup'\""
  exit 1
fi

exit 0