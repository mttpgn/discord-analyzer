-- See most popular symbols talked about today                                                                        
select                                                                                                                
ticker_symbol,count(ticker_symbol)                                                                                    
from messages                                                                                                         
where "timestamp" > (now() - interval '15' hour)                                                                      
group by ticker_symbol                                                                                                
order by count desc;                                                                                                  

