-- See most popular symbols talked about this week                                                                    
select                                                                                                                
ticker_symbol,count(ticker_symbol)                                                                                    
from messages                                                                                                         
where "timestamp" > (now() - interval '1' week)                                                                       
and discord_name <> 'fake'
group by ticker_symbol                                                                                                
order by count desc;                                                                                                  

