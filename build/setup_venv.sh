echo "Setting up the Vulture virutal environment"

CURRENT_DIR=$(pwd)

if [ "$1" = "-f" ] || [ "$1" = "--force" ]
then
  if [ -e "$CURRENT_DIR/venv" ]
  then
      echo "Venv already exists, deleting and creating a new one..."

      rm -r "$CURRENT_DIR/venv"
  fi
fi

echo "Creating a Python3 virtual environment named venv in $CURRENT_DIR"

python3 -m venv "$CURRENT_DIR/venv"

echo "Activating virtual environment"

source "$CURRENT_DIR/venv/bin/activate"

echo "Installing pip requirements"

pip install -r build/requirements.txt
