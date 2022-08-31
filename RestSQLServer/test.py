from peewee import *
from playhouse.reflection import generate_models
import pandas as pd

pg_db = PostgresqlDatabase('testdjango', user='postgres', password='*',
                           host='127.0.0.1', port=5432)

print(pg_db)


class Base(Model):
    usse = 1

    class Meta:
        database = pg_db


class Schedule(Model):
    delay = IntegerField()  # I would prefer if we had a TimeDeltaField


print(Base.__dict__)
# Meta = type(str('Meta'), (Base,), {'database': pg_db})
print("内部类")

# print(Meta)


fields = {'username': CharField(), 'password': CharField(), 'datetime': DateTimeField(),'id': IntegerField()}
table = type(str('Model1_testuser'), (Base,), fields)  # 动态类型
print(table)
print(table.__dict__)
dir(table)
print("再次查看内部类")
# 第一个 dbname

print(pg_db)
query = table.select()
df = pd.DataFrame(query.dicts())
print(df)
# df = df.set_index(pd.DatetimeIndex(pd.to_datetime(df.index)))
# group1=df.groupby('datetime')
# for i in group1:
#     print(i)
print("aaa")
df['datetime']=pd.to_datetime(df['datetime'])
print(df)
# df.set_('datetime')

# print(df.resample(rule='1T').mean())
print(df.resample('6S',on='datetime').agg({'id':'sum','username':'count'}))


# Calculate the timestamp of the next occurrence. This is done
# by taking the last occurrence and adding the number of seconds
# indicated by the schedule.
# one_second = SQL("INTERVAL '1 second'")
# next_occurrence = table.datetime + (one_second * Schedule.delay)

# Get all recurring rows where the current timestamp on the
# postgres server is greater than the calculated next occurrence.
# query = (table
#          .select(table, Schedule)
#          .join(Schedule)
#          .where(SQL('current_timestamp') >= next_occurrence))
#
# for recur in query:
#     print(recur.occurred_at, recur.schedule.delay)
