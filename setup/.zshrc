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

# Set colima for docker
export DOCKER_BUILDKIT=1
export DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock"

# Load python - must be at the end to override any conflicts
export PATH="/opt/homebrew/bin:$PATH"
alias python=/opt/homebrew/bin/python3.13
alias python3=/opt/homebrew/bin/python3.13

# Load poetry
export PATH="/Users/merylldindin/.local/bin:$PATH"

# Added by dbt Fusion extension
alias dbtf=/Users/merylldindin/.local/bin/dbt

# Load nvm
export NVM_DIR=~/.nvm
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
alias nvmuse='nvm use && corepack enable'

# Enable corepack for yarn/pnpm (managed by Node.js)
command -v corepack &> /dev/null && corepack enable

# Load GCloud CLI
if [ -f '/Users/merylldindin/google-cloud-sdk/path.zsh.inc' ];
then . '/Users/merylldindin/google-cloud-sdk/path.zsh.inc'; fi

if [ -f '/Users/merylldindin/google-cloud-sdk/completion.zsh.inc' ];
then . '/Users/merylldindin/google-cloud-sdk/completion.zsh.inc'; fi

# Ensure autoloading of nvm
nvm_autoload() {
    if [ -f .nvmrc ]; then
        local nvmrc_version="$(cat .nvmrc)"
        local current_version="$(nvm current)"

        # Only switch if the version is different
        if [ "$nvmrc_version" != "$current_version" ]; then
            nvm use "$nvmrc_version"
            # Re-enable corepack after switching Node versions
            command -v corepack &> /dev/null && corepack enable
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

# Alias for screencast compression
vidcomp() {
    if [ $# -lt 1 ]; then
        echo "Usage: vidcomp <input_file> [output_file]"
        return 1
    fi

    local input="$1"
    local output="${2:-${input%.*}_compressed.mp4}"

    ffmpeg -i "$input" -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 96k "$output"
}

# Alias for video to GIF conversion
vid2gif() {
    if [ $# -lt 1 ]; then
        echo "Usage: vid2gif <input_file> [output_file] [width] [fps]"
        echo "  input_file: video file to convert"
        echo "  output_file: optional, defaults to input name with .gif extension"
        echo "  width: optional, defaults to 640px (height auto-scaled)"
        echo "  fps: optional, defaults to 15fps"
        return 1
    fi

    local input="$1"
    local output="${2:-${input%.*}.gif}"
    local width="${3:-640}"
    local fps="${4:-15}"

    # Two-pass conversion for better quality and smaller file size
    # Pass 1: Generate palette
    ffmpeg -i "$input" -vf "fps=$fps,scale=$width:-1:flags=lanczos,palettegen" -y /tmp/palette.png

    # Pass 2: Create GIF using the palette
    ffmpeg -i "$input" -i /tmp/palette.png -filter_complex "fps=$fps,scale=$width:-1:flags=lanczos[x];[x][1:v]paletteuse" "$output"

    # Clean up temporary palette
    rm -f /tmp/palette.png

    echo "GIF created: $output"
}
