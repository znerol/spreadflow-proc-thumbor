from setuptools import setup

setup(
    name='SpreadFlowProcThumbor',
    version='0.0.1',
    description='Thumbor support for SpreadFlow metadata extraction and processing engine',
    author='Lorenz Schori',
    author_email='lo@znerol.ch',
    url='https://github.com/znerol/spreadflow-proc-thumbor',
    packages=[
        'spreadflow_proc_thumbor',
        'spreadflow_proc_thumbor.test'
    ],
    install_requires=[
        'SpreadFlowCore'
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia'
    ]
)
