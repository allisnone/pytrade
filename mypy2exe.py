from distutils.core import setup
import py2exe
#setup(console=["pyautotrade.pyw"])

setup(
    windows=[{'script': 'pyautotrade.pyw'}],
    options={
        'py2exe': 
        {
            'includes': ['lxml.etree', 'lxml._elementpath', 'gzip'],
        }
    }
)