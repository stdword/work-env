
# If not running interactively, don't do anything
[[ "$-" != *i* ]] && return


# Shell Options
#
# See man bash for more options...
#
# Don't wait for job termination notification
# set -o notify
#
# Don't use ^D to exit
# set -o ignoreeof
#
# Use case-insensitive filename globbing
# shopt -s nocaseglob
#
# Make bash append rather than overwrite the history on disk
# shopt -s histappend
#
# When changing directory small typos can be ignored by bash
# for example, cd /vr/lgo/apaache would find /var/log/apache
# shopt -s cdspell


# Completion options
#
# These completion tuning parameters change the default behavior of bash_completion:
#
# Define to access remotely checked-out files over passwordless ssh for CVS
# COMP_CVS_REMOTE=1
#
# Define to avoid stripping description in --option=description of './configure --help'
# COMP_CONFIGURE_HINTS=1
#
# Define to avoid flattening internal contents of tar files
# COMP_TAR_INTERNAL_PATHS=1


# History Options
#
# Don't put duplicate lines in the history.
 export HISTCONTROL=$HISTCONTROL${HISTCONTROL+,}ignoredups
#
# Ignore some controlling instructions
# HISTIGNORE is a colon-delimited list of patterns which should be excluded.
# The '&' is a special pattern which suppresses duplicate entries.
# export HISTIGNORE=$'[ \t]*:&:[fb]g:exit'
# export HISTIGNORE=$'[ \t]*:&:[fb]g:exit:ls' # Ignore the ls command as well
#
# Whenever displaying the prompt, write the previous line to disk
# export PROMPT_COMMAND="history -a"


# Umask
#
# /etc/profile sets 022, removing write perms to group + others.
# Set a more restrictive umask: i.e. no exec perms for others:
# umask 027
# Paranoid: neither group nor others have any perms:
# umask 077


# User

if [ -d "/home/DWord/.bash_completions" ]; then
	for f in `ls /home/DWord/.bash_completions`; do
		source "/home/DWord/.bash_completions/$f"
	done
fi

if [ -d "/home/DWord/.bash_functions" ]; then
	for f in `ls /home/DWord/.bash_functions`; do
		source "/home/DWord/.bash_functions/$f"
	done
fi

if [ -d "/home/DWord/.bash_aliases" ]; then
	for f in `ls /home/DWord/.bash_aliases`; do
		source "/home/DWord/.bash_aliases/$f"
	done
fi

if [ -f /etc/bash_completion ]; then
        . /etc/bash_completion
fi
