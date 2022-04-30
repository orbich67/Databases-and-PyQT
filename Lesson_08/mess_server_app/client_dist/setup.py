from setuptools import setup, find_packages

setup(name="mess_project67_client",
      version="0.1.0",
      description="Application (client part) for instant messaging. Allows you to exchange text "
                  "messages between users.",
      author="S.Orbidan",
      author_email="orbidan@bk.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
