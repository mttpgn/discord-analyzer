-- Delete all messages from tickers on the blacklist
DELETE FROM messages where ticker_symbol in (
'A','AGO','AL','ALE','ALL','AM','AN','ARE','AT','ATH','AU','B','BE','BEN','BIG','BRO','C','CAL','CAN','CAT','CE','CL','CM','CS','CUB','CUBE','CUZ','D','DD','DE','DOW','E','EAT','EL','EOD','ER','ES','ET','EXP','F','FE','FOR','FUN','G','GE','GEL','GM','GO','GOLD','GOOD','H','HALL','HAS','HE','HES','HOME','ICE','ING','IO','IT','J','K','KEY','L','LOVE','LOW','M','MA','MAN','MAX','MMM','MO','MS','MT','MU','NEE','NEXT','NEW','NOW','O','OI','ON','OR','OUT','PLAN','PM','PPL','R','RM','RY','SAVE','SE','SEE','SNN','SO','SON','SRE','STAR','SUM','T','THO','TT','TU','USA','U','V','W','WAT','WELL','WM','WORK','WWW','WY','X'
);

