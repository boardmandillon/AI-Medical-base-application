CURRENT_DIR=$(pwd)

if [ "$1" = "-f" ] || [ "$1" = "--force" ]
then
  if [ -e "$CURRENT_DIR/venv" ]
  then
      echo -e "\nVenv already exists, deleting and creating a new one...\n"

      rm -r "$CURRENT_DIR/venv"

      if [ -e "$CURRENT_DIR/venv" ]
      then
          echo "Failed to delete venv, please do it manually"
          exit 1
      fi

      echo "Venv deleted successfully"
  fi
elif [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  echo "Create the Python virtual environment under the venv directory"
  echo -e "\t-f, \t--force \tRemove the current virtual environment under the venv directory"
  exit 0
fi

echo "Setting up the Vulture virtual environment"

echo -e "\nCreating a Python3 virtual environment named venv in $CURRENT_DIR\n"

python3 --version
python3 -m venv "$CURRENT_DIR/venv"

echo -e "\nActivating virtual environment..."

source "$CURRENT_DIR/venv/bin/activate"

echo -e "\nVirtual environment information:"

which python3
python3 --version

echo -e "\n=============================="
echo "Installing pip requirements..."
echo -e "==============================\n"

pip install -r build/requirements.txt

echo -e "\n=========================="
echo "Python packages installed:"
echo -e "==========================\n"

pip freeze

echo -e "\n=============="
echo -e "Setup complete\n"