# coding: utf-8

from __future__ import unicode_literals

import os

from fabric.api import local
from fabric.context_managers import hide
from fabric.utils import indent


__all__ = [
	'django_env_init',
]


def get_scripts_path():
	self_path = os.path.realpath(__file__)
	self_folder = os.path.dirname(self_path)

	return os.path.join(self_folder, 'scripts')


def django_env_init():
	completions_mark = 'dw work-env completions'

	with hide('running'):
		home = local('echo $HOME', capture=True)
	bash_completions_folder = os.path.join(home, '.bash_completions')

	if not os.path.exists(bash_completions_folder):
		local('mkdir {}'.format(bash_completions_folder))

	completions_folder = os.path.join(get_scripts_path(), 'completions')
	local('cp {}/* {}'.format(completions_folder, bash_completions_folder))

	bashrc_path = os.path.join(home, '.bashrc')
	with open(bashrc_path, 'r+') as f:
		if f.read().find(completions_mark) == -1:
			text = indent(
				text='''
					# dw work-env completions
					if [ -f "${HOME}/.bash_completions" ]; then
						source "${HOME}/.bash_completions"
					fi

					if [ -d "${HOME}/.bash_completions" ]; then
						for f in `ls ${HOME}/.bash_completions/`; do
							source "${HOME}/.bash_completions/$f"
						done
					fi
					# dw work-env
				''',
				spaces=0,
				strip=True,
			)
			f.write(text + '\n')


django_env_init()
