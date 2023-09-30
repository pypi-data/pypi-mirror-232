from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name="mkwhatkit",
  version='0.0.1',
  description = 'This is a library that can do several things.',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='https://upload.pypi.org/legacy/',  
  author='Maullick Kathuria',
  author_email='maullickkathuria23@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='play,prompt,error,info,password,calculate,mouse_position,move_mouse,click,recognize_speech,speak,speak_voices,set_voice,create_tk_calculator', 
  packages=find_packages(),
  install_requires=['speech_recognition','pyttsx3','pyautogui','pywhatkit'] 
)
