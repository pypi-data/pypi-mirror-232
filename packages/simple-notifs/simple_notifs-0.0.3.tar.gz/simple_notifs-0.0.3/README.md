# Introduction

This library was built for making simple, shortened human readable versions of time deltas. 
This was specifically made for notifications on applications where a user wants to see how long it has been
since the notification was made. For example, instead of a time delta such as "1 hour ago" or "20 minutes ago", the resulting time delta would be
"1h" and "20mi", respectively

## Access
From simple_notifs.simple_notifs import utc_to_human

## Arguments

- Mandatory, a datetime object must be passed as input to the function. 
- By default, is_utc is set to True. If false, the built in method converts the datetime object to utc, then performs its operation.
- By default, days_and_above is set to False. If True, the built in method will only display time deltas starting at "1d". This means any deltas
in seconds, minutes, or hours that are less than a full day, will be truncated to "1d".