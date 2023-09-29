from setuptools import setup, find_packages
 
setup(name='PrintableTree',
      packages=['PrintableTree'],
      version='0.5',
      url='https://github.com/klingerkrieg/PrintableTree',
      download_url='https://github.com/klingerkrieg/PrintableTree/archive/refs/tags/0.5.tar.gz',
      license='MIT',
      author='Alan Klinger',
      author_email='klingerkrieg@gmail.com',
      description='It has an implementation of a tree in python and methods that print the tree to an image through OpenCV / É uma implementação de uma árvore em python com métodos que permitem imprimir a árvore através do OpenCV',
      long_description='Visit the <a href="https://github.com/klingerkrieg/PrintableTree">homepage</a> for more details.',
      zip_safe=False,
      install_requires=[            # I get to this in a second
          'opencv-python',
          'numpy',
          'matplotlib',
      ])
