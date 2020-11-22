-- What are people saying about a particular ticker
select text,ticker_symbol, timestamp, positive from messages where
ticker_symbol in ('CAL', 'ALE')
and
"timestamp" > (now() - interval '1' day)
and discord_name <> 'fake'
order by ticker_symbol;

