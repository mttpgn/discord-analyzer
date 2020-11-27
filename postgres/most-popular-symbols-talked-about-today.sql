-- See most popular symbols talked about today                                                                        
select
ticker_symbol,count(ticker_symbol) as mentions
from messages
where "timestamp" > (now() - interval '15' hour)
group by ticker_symbol
having count(ticker_symbol) > 1
order by mentions desc;

