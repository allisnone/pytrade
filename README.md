# PyAutoTrading
股票交易软件辅助工具

## 简介
用于华泰证券通达信版（须有`双向委托`功能）。软件可以一次监控5只股票，根据条件下单。每次下单耗时小于1s，目前软件只能知道委托是否成功。如果有疑问，或是建议，可以发邮件联系。QQ群：486224275。

## 注意事项
* 开发环境是win10 64bit, python3 64bit、pywin32、tushare。 以前是用python 32bit开发的，现在好像python 64bit的也能用。
* 软件共有4个文件，pyautotrading.ini配置文件，PyAutoTrading.pyw主程序，stockInfo.dat存盘文件，winguiauto.py是封装的winapi函数。
* 交易软件启动后，按F6，进入双向委托界面，启动本程序后，不要再切换到其它界面。切换到其他界面后即使再切换回来，有些情况会导致不能正常获取句柄。
* 程序启动有点慢，初始化工作比较多，python的多线程问题。
* 不写时间条件单，默认时间为凌晨1点。如果只想要时间条件单而忽略价格条件单，可以写个始终满足条件的价格。其它地方不写，这行将不做处理。
* 股票数量最好为100的倍数，小于100股的不会交易，大于100、非整数倍的将取整, 比如150股将作为100股。
* 时间为24小时制，形式为 “时：分：秒”， 每项都必须写， 后面的写法是错误的： “13：30” 。

## 版本
* v 0.01 修正了股票价格实时显示问题。
* v 0.02 重构了交易软件接口，目前在最小化状态下也可以下单，下单速度加快，增加委托日志。
* v 0.03 重新布局了控件，修改委托日志控件。修复了少许Bug。
* v 0.04 重新布局了控件，重构了monitor函数。现在一次可以下4个条件单。
* v 0.05 加入时间条件单。
* v 0.06 交易软件接口函数单独放winguiauto文件。
* v 0.07 时间条件单和价格条件单相结合，添加保存和载入功能,存档和主文件在同一目录下，名为stockInfo.dat，是个二进制文件。
* v 0.08 代码清理，添加了注释。现在可以同时监控5只股票。
* v 0.09 增加配置文件pyautotrading.ini。加入自动刷新功能，每隔5分钟刷新一次，防止软件进入待机状态。
* v0.10 修改了几个bug，买卖价格改由python计算，加快了下单速度（1.5s），稳定性增加了不少。需更改交易软件设置，请看图。
* v0.11 重构交易接口。现在可以获取持仓，成交，资金状况。注意：打开交易软件后，需要依次点击菜单条上的按钮，从左向右，然后再打开本程序，否则无法正确获取句柄。见图八中的工具条。


-----------------------------------
![image](https://github.com/drongh/pyautotrade_tdx/raw/master/Logo/setting1.png)
![image](https://github.com/drongh/pyautotrade_tdx/raw/master/Logo/setting2.png)
![image](https://github.com/drongh/pyautotrade_tdx/raw/master/Logo/setting3.png)
![image](https://github.com/drongh/pyautotrade_tdx/raw/master/Logo/setting4.png)
![image](https://github.com/drongh/pyautotrade_tdx/raw/master/Logo/setting5.png)
![image](https://github.com/drongh/pyautotrade_tdx/raw/master/Logo/setting6.png)
![image](https://github.com/drongh/pyautotrade_tdx/raw/master/Logo/setting7.png)
![image](https://github.com/drongh/pyautotrade_tdx/raw/master/Logo/setting8.png)
![image](https://github.com/drongh/pyautotrade_tdx/raw/master/Logo/trading.png)