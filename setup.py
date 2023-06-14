from setuptools import setup, find_namespace_packages

setup(name='svrimg',
      version='0.1a4',
      description='SVRIMG Dataset Interface and Analyses',
      author='Alex Haberlie',
      author_email='svr.image@gmail.com',
      package_dir={'':'src'},
      packages=find_namespace_packages(where="src"),
      url='http://nimbus.niu.edu/svrimg'
     )