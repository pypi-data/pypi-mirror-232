
from setuptools import setup
from setuptools.command.install import install

# Define una función que se ejecutará durante la instalación
class custom_install_code(install):
    def run(self):
        print("Here is where I would be running my code...")
        install.run(self)

    def _post_install():
        print("Here is where I would be running my code post install...")

setup(
    name='paraty_commit_jlvillada',
    version='0.1.35',
    description='Una biblioteca personalizada',
    author='José Luis Villada',
    author_email='jlvillada@paratytech.com',
    cmdclass={
        'install': custom_install_code
      },
    packages=['paraty_commit_jlvillada'],
    install_requires=['colorama'],
    # package_data={'paraty_commit_jlvillada': ['*', '.pre-commit-config.yaml']}
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'my_executable = paraty_commit_jlvillada.precommit:main',
        ],
    },
)