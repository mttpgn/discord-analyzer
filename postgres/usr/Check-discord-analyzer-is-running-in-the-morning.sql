-- Check discord-analyzer is running in the morning                                                                   
select * from messages where "timestamp" >  (now() - interval '1' hour)                                               

