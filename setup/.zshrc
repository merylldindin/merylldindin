# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set the prompt theme
ZSH_THEME="robbyrussell"

# Enable syntax highlighting
source /opt/homebrew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# Enable auto-completion
autoload -Uz compinit
compinit

# Set the editor to nano
export EDITOR=vim

# Aliases
alias ll="ls -alF"
alias la="ls -A"

# Add custom paths to the PATH variable
export PATH=$HOME/bin:/usr/local/bin:$PATH

# Load GCloud CLI
if [ -f '/Users/merylldindin/google-cloud-sdk/path.zsh.inc' ];
then . '/Users/merylldindin/google-cloud-sdk/path.zsh.inc'; fi

if [ -f '/Users/merylldindin/google-cloud-sdk/completion.zsh.inc' ];
then . '/Users/merylldindin/google-cloud-sdk/completion.zsh.inc'; fi

# Load python
export PATH="/opt/homebrew/bin:$PATH"
alias python=python3.12

# Load poetry
export PATH="/Users/merylldindin/.local/bin:$PATH"

# Load nvm
export NVM_DIR=~/.nvm
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# Load node
export PATH="/Users/merylldindin/.nvm/versions/node/v20.12.2/bin:$PATH"

# Load pnpm
export PNPM_HOME="/Users/merylldindin/Library/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac

# Ensure autoloading of nvm
nvm_autoload() {
    local node_version
    local major_version
    major_version="$(cat .nvmrc 2>/dev/null | cut -d '.' -f 1)"
    if [ -n "$major_version" ]; then
        node_version="$(nvm ls-remote | grep -o "$major_version\.[0-9]*\.[0-9]*" | tail -1)"
        if [ -n "$node_version" ]; then
            nvm use "$node_version"
        fi
    fi
}

# Call `nvm_autoload` every time the directory changes
cd() { builtin cd "$@" && nvm_autoload; }

# Set some custom terminal colors
autoload -U colors
colors

# ZSH plugins
plugins=(git)

# Load oh-my-zsh
source $ZSH/oh-my-zsh.sh

# Customize prompt
prompt() {
    local last_dir=$(basename "$PWD")
    PROMPT="%F{blue}%n%f@%F{green}%m%f:%F{cyan}%1~%f (%F{yellow}$last_dir%f)%F{red}%(!.#.%%) %f"
}

