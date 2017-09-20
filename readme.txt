#
每天需要做的事情：
1.下载银河最新数据
2 export银河沪深A股数据
3 export 银河基金数据
4 export 银河精选指数数据
5 获取持仓信息，并运行仓位更新到数据库
5 运行历史数据更新：
	更新持仓股票的历史数据到'C:/hist/day/data/'--from web
	更新基金和指数数据到  'C:/hist/day/data/'  -from YH
7 复盘指数分析数据
8 复盘持仓股票分析数据
9 复盘所有股票分析数据，精选各种策略股票


http://notemi.cn/how-to-make-the-ui-automation-program-still-interactive-after-the-remote-desktop-is-turned-off.html
cmd close remote desktop:
query session

C:\Users\Administrator\pytrade>query session
 会话名            用户名                   ID  状态    类型        设备
 services                                    0  断开
 console                                     1  已连接
>rdp-tcp#0         Administrator             2  运行中  rdpwd
 rdp-tcp                                 65536  侦听

C:\Users\Administrator\pytrade>tscon rdp-tcp#0 /dest:console


tscon rdp-tcp#0 /dest:console

tscon console /dest:rdp-tcp#0

recover:
rundll32.exe user32.dll,LockWorkStation