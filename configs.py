# import logging

dbname = 'sentiment.sqlite'
projroot = '/Users/mttpgn/src/wsbdiscordsentiment'
ss_location = '{}/screenshots'.format(projroot)
db_location = '{}/{}'.format(projroot, dbname)
exten = '.png'
ss_top = 220
ss_left = 820
ss_width = 1985
ss_height = 1645
# logging.basicConfig('/var/log/wsbdiscordsentiment/python.log')
negative_wordlist = [
  'drill', 
  'Drill', 
  'DRILL', 
  'puts', 
  'Puts', 
  'PUTS',
  'PUT',
  'Put',
  'put'
  '0p', 
  '1p', 
  '2p', 
  '3p', 
  '4p', 
  '5p', 
  '6p', 
  '7p', 
  '8p', 
  '9p', 
  'fuck', 
  'FUCK', 
  'Fuck', 
  'ROPE', 
  'imagine', 
  'Imagine', 
  'drop', 
  'Drop', 
  'DROP', 
  'shit',
  'Shit',
  'SHIT',
  'Garbage',
  'garbage', 
  'GARBAGE',
  'trash',
  'Trash',
  'TRASH',
  'TANK',
  'tank',
  'Tank',
  'Dump',
  'dump',
  'DUMP',
  'Sad',
  'sad',
  'SAD'
]                                                                        

dictionary_location = '/usr/share/dict/words'

pg_db_name = 'sentiment-db'
pg_db_host = 'sentiment-db.cogzqkcq8zkt.us-east-2.rds.amazonaws.com'
pg_db_port = 5432
pg_db_username = 'postgres'
pg_db_password = 'q6juzlW4GBoKPpyilvPh'
