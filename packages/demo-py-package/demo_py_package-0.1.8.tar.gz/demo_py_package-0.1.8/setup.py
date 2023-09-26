from setuptools import setup

setup(
  name = 'demo_py_package',         # How you named your package folder (MyLib)
  packages = ['demo_py_package'],   # Chose the same as "name"
  version = '0.1.8',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Simple package to learn the process of publishing a python package to PyPI',   # Give a short description about your library
  long_description="""# Markdown supported!\n\n* Cheer\n* Celebrate\n""",
  long_description_content_type='text/markdown',
  author = 'Adrian Salgado Lopez',                   # Type in your name
  author_email = 'adrianlopezdev@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/AdrianSLopez/demo_py_package',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/AdrianSLopez/demo_py_package/archive/refs/tags/0.1.8.tar.gz',    # I explain this later on
  keywords = [],   # Keywords that define your package best
  install_requires=[], # package dependencies
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)