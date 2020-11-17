-- Check discord-analyzer is running in the morning
select * from messages where "timestamp" >  (now() - interval '1' hour)

-- See most popular tickers in a given timeframe
select 
ticker_symbol,count(ticker_symbol) 
from messages 
where "timestamp" BETWEEN  '2020-11-16 9:00 AM' AND '2020-11-16 4:00 PM'
group by ticker_symbol 
order by count desc;

-- See most popular symbols talked about today
select 
ticker_symbol,count(ticker_symbol) 
from messages 
where "timestamp" > (now() - interval '15' hour)
group by ticker_symbol 
order by count desc;

-- See most popular symbols talked about this week
select 
ticker_symbol,count(ticker_symbol) 
from messages 
where "timestamp" > (now() - interval '1' week)
group by ticker_symbol 
order by count desc;

-- What are people saying about a particular ticker
select text,ticker_symbol, timestamp, positive from messages where
ticker_symbol in ('CAL', 'ALE')
and
"timestamp" > (now() - interval '1' day)
order by ticker_symbol;


