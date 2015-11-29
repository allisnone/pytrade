This is tested in windows server 2008, x64 system. For x86/32bit OS, just for reference


http://www.lfd.uci.edu/~gohlke/pythonlibs/#pywin32

c:\Python34\Scripts>pip install F:\2015\tools\pandas17-py34\tables-3.2.2-cp34-no
ne-win32.whl


python.exe Scripts\pywin32_postinstall.py -install

c:\Python34\Scripts>pip install F:\2015\tools\pandas17-py34\pywin32-219-cp34-non
e-win32.whl


https://www.python.org/ftp/python/


step by step:
 
pip3.4 install lxml-3.4.4-cp34-none-win_amd64.whl
pip3.4 install python_dateutil-2.4.2-py2.py3-none-any.whl
pip3.4 install pytz-2015.7-py2.py3-none-any.whl

pip3.4 install numpy-1.9.3+mkl-cp34-none-win_amd64.whl
pip3.4 install llvmlite-0.8.0-cp34-none-win_amd64.whl
pip3.4 install pandas-0.17.1-cp34-none-win_amd64.whl
pip3.4 install matplotlib-1.5.0-cp34-none-win_amd64.whl
pip3.4 install numba-0.22.1-cp34-none-win_amd64.whl
pip3.4 install numexpr-2.4.6-cp34-none-win_amd64.whl
pip3.4 install py2exe-0.9.2.2-cp34-none-win_amd64.whl
pip3.4 install scipy-0.16.1-cp34-none-win_amd64.whl
pip3.4 install SQLAlchemy-1.0.9-cp34-none-win_amd64.whl

pywin32-219-cp34-none-win_amd64.whl
pip3.4 install tushare
pip3.4 install pymysql
pip3.4 install backtrader


Then for pywin32, need to copy:
C:\Python34\Lib\site-packages\pywin32_system32/* to C:\Windows\System32