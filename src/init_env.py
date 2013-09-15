# coding: utf-8

from __future__ import unicode_literals

import os

from fabric.api import local
from fabric.context_managers import hide
from fabric.operations import prompt
from fabric.utils import indent


def get_env_path():
	self_path = os.path.realpath(__file__)
	self_folder = os.path.dirname(self_path)

	return os.path.join(self_folder, 'env')


def source_starter(env_type, home, bash_folder):
	mark = 'dw work-env {}'.format(env_type)

	bashrc_path = os.path.join(home, '.bashrc')
	with open(bashrc_path, 'r+') as f:
		if f.read().find(mark) == -1:
			text = indent(
				text='''
					## {mark} start
					if [ -d "{bash_folder}" ]; then
						for f in `ls {bash_folder}`; do
							source "{bash_folder}/$f"
						done
					fi
					## {mark} end
				'''.format(
					mark=mark,
					bash_folder=bash_folder
				),
				spaces=0,
				strip=True,
			)
			f.write('\n\n' + text + '\n\n')


def scripts_starter(env_type, home, bash_folder):
	pass


def configs_starter(env_type, home, bash_folder):
	pass


def init_env(env_type, starter):
	with hide('running'):
		home = local('echo $HOME', capture=True)
	bash_folder = os.path.join(home, '.bash_{}'.format(env_type))

	if os.path.exists(bash_folder):
		replace = prompt(
			'Replace a "{}" folder? (yes/no)'.format(bash_folder),
			default='no',
			validate=r'^yes|no$',
		) == 'yes'
		if replace:
			local('rm -r {}'.format(bash_folder))
		else:
			local('mv {0} {0}-old'.format(bash_folder))

	env = get_env_path()
	env_folder = os.path.join(env, env_type)
	local('cp -r {} {}'.format(env_folder, bash_folder))

	starter(env_type, home, bash_folder)


def main():
	init_env(env_type='functions', starter=source_starter)
	init_env(env_type='aliases', starter=source_starter)
	init_env(env_type='completions', starter=source_starter)
	init_env(env_type='scripts', starter=scripts_starter)
	init_env(env_type='configs', starter=configs_starter)


###############################################################################


if __name__ == '__main__':
	main()
