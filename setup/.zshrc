# ==============================================================================
# OH-MY-ZSH
# ==============================================================================
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"

# Plugin settings
zstyle ':omz:plugins:nvm' lazy yes
zstyle ':omz:plugins:nvm' autoload yes

# Plugins
# poetry: mkdir -p $ZSH_CUSTOM/plugins/poetry && poetry completions zsh > $ZSH_CUSTOM/plugins/poetry/_poetry
plugins=(git z poetry nvm npm yarn)

source $ZSH/oh-my-zsh.sh

# ==============================================================================
# SHELL
# ==============================================================================
export EDITOR=vim

autoload -Uz compinit && compinit
autoload -Uz bashcompinit && bashcompinit
autoload -U colors && colors

source /opt/homebrew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# ==============================================================================
# PATH
# ==============================================================================
export PATH="$HOME/bin:/usr/local/bin:$PATH"
export PATH="/opt/homebrew/bin:$PATH"
export PATH="$HOME/.local/bin:$PATH"

# ==============================================================================
# DOCKER (Colima)
# ==============================================================================
export DOCKER_BUILDKIT=1
export DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock"

# Auto-start colima if not running
if command -v colima &>/dev/null && ! colima status &>/dev/null 2>&1; then
    colima start --cpu 2 --memory 4 --mount-type virtiofs &>/dev/null &
fi

# ==============================================================================
# PYTHON (pipx, poetry, uv)
# ==============================================================================
export PIPX_HOME=~/.local/pipx
export PIPX_BIN_DIR=~/.local/bin

alias python=/opt/homebrew/bin/python3.13
alias python3=/opt/homebrew/bin/python3.13

eval "$(uv generate-shell-completion zsh)"
eval "$(uvx --generate-shell-completion zsh)"

# ==============================================================================
# NODE (nvm, corepack)
# ==============================================================================
export NVM_DIR=~/.nvm

# ==============================================================================
# CLOUD (gcloud, aws)
# ==============================================================================
[ -f "$HOME/google-cloud-sdk/path.zsh.inc" ] && source "$HOME/google-cloud-sdk/path.zsh.inc"
[ -f "$HOME/google-cloud-sdk/completion.zsh.inc" ] && source "$HOME/google-cloud-sdk/completion.zsh.inc"

complete -C '/opt/homebrew/bin/aws_completer' aws

# ==============================================================================
# DATA (dbt)
# ==============================================================================
alias dbtf="$HOME/.local/bin/dbt"
[ -f ~/.dbt-completion.bash ] && source ~/.dbt-completion.bash

# ==============================================================================
# ALIASES
# ==============================================================================
alias ll="ls -alF"
alias la="ls -A"

# ==============================================================================
# FUNCTIONS
# ==============================================================================

# Image compression to WebP (lossless)
imgcomp() {
    [ $# -lt 1 ] && echo "Usage: imgcomp <input> [output]" && return 1
    local input="$1"
    local output="${2:-${input%.*}.webp}"
    cwebp -lossless -q 100 -m 6 "$input" -o "$output"
}

# Video compression (H.264/AAC)
vidcomp() {
    [ $# -lt 1 ] && echo "Usage: vidcomp <input> [output]" && return 1
    local input="$1"
    local output="${2:-${input%.*}_compressed.mp4}"
    ffmpeg -i "$input" -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 96k "$output"
}
