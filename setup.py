from setuptools import setup

setup(name='CMAnalytics',
      version='0.9',
      packages=[ 'CMAnalytics', 'CMAnalytics.video', 'CMAnalytics.uievents' ],
      scripts = [ 'bin/makePlayTemplates.py', 'bin/analyze_video.py' ],
      install_requires = [ 'pillow', 'pytesseract', 'shapely' ]
      )
