from sqlbase import *

mysql_obj=SqlOperation(host='112.74.101.126', port=3306, user='emsadmin', passwd='Ems4you', db='stock')#, charset='utf8')

sql_q=form_sql(table_name='stock.account',oper_type='query',select_field='acc_name,initial',where_condition="acc_name='36005'")
print(time.time())

q_data=mysql_obj.query(sql_q)
print('q_data=',q_data)

print(time.time())

sql_q=form_sql(table_name='stock.account',oper_type='query',select_field='acc_name,initial,comm')

q_data=mysql_obj.query(sql_q)
print('q_data=',q_data)

sql_insert=form_sql(table_name='stock.account',oper_type='insert',insert_field='(acc_name,initial,comm)')
#sql_insert=form_sql(table_name='stock.acount',oper_type='insert',insert_field='(acount)')

data=[['223458',10000,0.0005],['223459',14200,0.01]]
#mysql_obj.insert_data(sql_insert,data)
q_data=mysql_obj.query(sql_q)
print('sql_insert_data=',q_data)

initial_value=19000
sql_update=form_sql(table_name='stock.account',oper_type='update',update_field='initial',where_condition='initial=29000',update_value='29000')

#sql_update=sql_update%initial_value
#print('sql_update=',sql_update)
update_data=mysql_obj.update_data(sql_update)
q_data=mysql_obj.query(sql_q)
print('update_data=',q_data)

sql_delete=form_sql(table_name='stock.account',oper_type='delete',where_condition="initial=14200.0")
update_data=mysql_obj.update_data(sql_delete)

q_data=mysql_obj.query(sql_q)
print('delete_data=',q_data)

