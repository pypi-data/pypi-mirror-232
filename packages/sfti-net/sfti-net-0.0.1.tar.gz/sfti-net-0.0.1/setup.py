from setuptools import setup, find_packages

setup(
   name='sfti-net',
   description='Package to send data in the SFTI Biotechnology Spearhead project',
   author='Ben Hong',
   packages=find_packages(),
   entry_points={
      'console_scripts': [
         'sfti-send=sfti_net.send:main',
         'sfti-watch=sfti_net.watch:main',
      ],
   },
   install_requires=[
       "watchfiles"
   ],
)