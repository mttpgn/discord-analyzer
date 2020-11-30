-- See most popular tickers in a given timeframe                                                                      
select                                                                                                                
ticker_symbol,count(ticker_symbol)                                                                                    
from messages                                                                                                         
where "timestamp" BETWEEN  '2020-11-16 9:00 AM' AND '2020-11-16 4:00 PM'                                              
and discord_name <> 'fake'
group by ticker_symbol                                                                                                
order by count desc;                                                                                                  

