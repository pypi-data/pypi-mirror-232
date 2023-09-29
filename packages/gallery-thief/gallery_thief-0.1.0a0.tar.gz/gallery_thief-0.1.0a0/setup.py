from setuptools import setup, find_packages

setup(
    name='gallery_thief',
    version='0.1.0-alpha',
    license='MIT',
    author="Kirill Voloshin",
    author_email='kirill.voloshin.98@ya.ru',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/viktor-akusoff/GalleryThief',
    keywords=['images', 'scraping', 'parsing', 'search engines'],
    install_requires=[
          'requests',
          'bs4',
          'fake-useragent',
          'numpy'
      ],
)
