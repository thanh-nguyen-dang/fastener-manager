#!/bin/bash

# Determine the operating system
OS="$(uname)"
PYENV_ROOT="$HOME/.pyenv"

# Function to install pyenv
install_pyenv() {
    echo "Installing pyenv..."

    # Install pyenv based on the operating system
    if [[ "$OS" == "Linux" ]]; then
        # Linux installation steps
        sudo apt update -y
        sudo apt install -y build-essential curl libssl-dev zlib1g-dev \
            libbz2-dev libreadline-dev libsqlite3-dev wget llvm \
            libncurses5-dev libncursesw5-dev xz-utils tk-dev \
            libffi-dev liblzma-dev python-openssl git

        curl https://pyenv.run | bash

    elif [[ "$OS" == "Darwin" ]]; then
        # macOS installation steps
        if ! command -v brew &> /dev/null; then
            echo "Homebrew is not installed. Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi

        brew install openssl readline sqlite3 xz zlib
        brew install pyenv

    else
        echo "Unsupported OS. Exiting."
        exit 1
    fi

    # Add pyenv to shell startup script
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

    echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

    # Restart shell to reload bashrc or zshrc
    exec "$SHELL"
}

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "pyenv is not installed. Installing pyenv..."
    install_pyenv
else
    echo "pyenv is already installed."
fi

# Ensure pyenv and its environment are loaded
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Install Python 3.10.7 using pyenv if it's not already installed
PYTHON_VERSION="3.10.7"
if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo "Installing Python $PYTHON_VERSION via pyenv..."
    pyenv install "$PYTHON_VERSION"
else
    echo "Python $PYTHON_VERSION is already installed."
fi

# Set Python version to 3.10.7 using pyenv shell
pyenv shell "$PYTHON_VERSION"

# Create a pyenv virtual environment named fastener_manager if it doesn't exist
VENV_NAME="fastener_manager"
if ! pyenv virtualenvs | grep -q "$VENV_NAME"; then
    echo "Creating pyenv virtualenv $VENV_NAME with Python $PYTHON_VERSION..."
    pyenv virtualenv "$PYTHON_VERSION" "$VENV_NAME"
else
    echo "Virtualenv $VENV_NAME already exists."
fi

# Activate the virtualenv
echo "Activating virtualenv $VENV_NAME..."
pyenv activate "$VENV_NAME"

# Path to root directory (two levels up from the script folder)
SCRIPT_DIR="$(python -c 'import os, sys; print(os.path.abspath(os.path.dirname("$0")))')"
ROOT_DIR="$(python -c 'import os, sys; print(os.path.abspath(os.path.join("$SCRIPT_DIR", "..")))')"

# Install required libraries from requirements.txt located in the root directory
REQUIREMENTS_FILE="$ROOT_DIR/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing required libraries from $REQUIREMENTS_FILE"
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "requirements.txt not found in $ROOT_DIR. Please ensure it is present in the project directory."
    exit 1
fi

echo "Setup completed successfully. Your virtualenv '$VENV_NAME' is ready."
echo "To activate the virtual environment, run: pyenv shell $VENV_NAME"
