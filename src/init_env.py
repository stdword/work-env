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
	pass


def scripts_starter(env_type, home, bash_folder):
	pass


def configs_starter(env_type, home, bash_folder):
	for config_name in os.listdir(bash_folder):
		config_path = os.path.join(bash_folder, config_name)
		old_config_path = os.path.join(home, config_name)

		if os.path.exists(old_config_path):
			with open(old_config_path) as f1:
				with open(config_path) as f2:
					if f1.read().strip() != f2.read().strip():
						save = prompt(
							'Save a backup for "{}"? (yes/no)'.format(old_config_path),
							default='yes',
							validate=r'^yes|no$',
						) == 'yes'
						if save:
							local('mv {0} {0}-old'.format(old_config_path))
						else:
							local('rm -r {}'.format(old_config_path))

		local('cp {} {}'.format(config_path, old_config_path))


def init_env(env_type, starter):
	with hide('running'):
		home = local('echo $HOME', capture=True)
	bash_folder = os.path.join(home, '.bash_{}'.format(env_type))

	if os.path.exists(bash_folder):
		save = prompt(
			'Save a backup for "{}"? (yes/no)'.format(bash_folder),
			default='yes',
			validate=r'^yes|no$',
		) == 'yes'
		if save:
			local('mv {0} {0}-old'.format(bash_folder))
		else:
			local('rm -r {}'.format(bash_folder))

	env = get_env_path()
	env_folder = os.path.join(env, env_type)
	local('cp -r {} {}'.format(env_folder, bash_folder))

	starter(env_type, home, bash_folder)


def main():
	init_env(env_type='completions', starter=source_starter)
	init_env(env_type='scripts', starter=scripts_starter)
	init_env(env_type='configs', starter=configs_starter)
	init_env(env_type='functions', starter=source_starter)
	init_env(env_type='aliases', starter=source_starter)


###############################################################################


if __name__ == '__main__':
	main()
