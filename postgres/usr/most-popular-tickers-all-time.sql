-- See most popular symbols talked about all time 
select
  ticker_symbol, count(ticker_symbol)
from (
    select id, ticker_symbol, "timestamp" from messages
      UNION
    select id,ticker_symbol,"timestamp" from atlastradingtraderchat
      UNION
    select id,ticker_symbol,"timestamp" from ogwsbso
      UNION select id,ticker_symbol,"timestamp" from wsb_stocks_and_options
    ) as all_tbls
where ticker_symbol not in (
  'A','AGO','AH','AI','AL','ALE','ALEX','ALL','AM','AN','ANY','APR','ARE','AT','ATH','AU','AUG','AX','B','BE','BEAT','BEN','BEST','BIG','BIT','BLUE','BRO','BUD','BY','C','CAL','CAN','CASH','CAT','CE','CEO','CL','CM','CS','CUB','CUBE','CUZ','D','DAN','DD','DE','DEC','DOW','E','EAT','EDD','EL','ELSE','EOD','ER','ES','ET','EV','EVER','EXP','F','FAST','FE','FEB','FOR','FREE','FUN','G','GAIN','GE','GEL','GM','GO','GOLD','GOOD','GUT','H','HALL','HAS','HE','HEAR','HERD','HES','HOME','HOPE','HUGE','ICE','ING','IO','IT','J','JACK','JAN','JUL','JUN','K','KEY','KIRK','L','LIFE','LL','LOVE','LOW','M','MA','MAN','MAR','MARK','MAX','MAY','MEN','MMM','MO','MODN','MP','MS','MU','NEE','NEXT','NEW','NICE','NICK','NM','NOV','NOW','O','OCT','OI','OLD','OM','ON','ONE','OR','OUT','PIE','PLAN','PLAY','PM','POST','PPL','PUMP','R','RE','REAL','RH','RIDE','RM','RUN','RY','SAM','SAN','SAVE','SE','SEE','SEP','SNN','SO','SOLO','SON','SRE','STAR','STAY','SU','SUM','SUNS','T','TA','TECH','TH','THO','TM','TT','TU','USA','U','V','VERY','VET','W','WAT','WELL','WLL','WM','WOOD','WOW','WWW','WY','X','Y','Z'
  )
group by ticker_symbol
order by count desc
having count > 9;

