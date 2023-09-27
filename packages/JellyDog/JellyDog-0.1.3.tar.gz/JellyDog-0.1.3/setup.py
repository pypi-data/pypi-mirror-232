from setuptools import setup

setup(name='JellyDog',
      version='0.1.3',
      description='A JellyCat online store stock tracker',
      url='https://github.com/Akuna23Matata/JellyDog',
      author='Akuna23Matata',
      author_email='zhiboh23@gmail.com',
      license='MIT',
      long_description=open('README.md', 'r').read(),
      long_description_content_type='text/markdown',
      packages=['JellyDog'],
      install_requires=[
          'bs4'
      ],
      zip_safe=False)