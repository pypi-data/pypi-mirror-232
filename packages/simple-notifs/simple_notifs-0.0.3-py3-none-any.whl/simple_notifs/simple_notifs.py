import arrow as ar
from datetime import datetime, timezone

def utc_to_human(datetime_object: datetime, days_and_above: bool = False) -> str:
    now = ar.utcnow()

    # check if the object is an arrow object, if not, convert it to arrow. 
    if not isinstance(datetime_object, ar.Arrow):
        datetime_object = ar.get(datetime_object)

    datetime_object = datetime_object.to('UTC')
    time_delta = now - datetime_object

    seconds = time_delta.total_seconds()
    days = time_delta.days

    if days >= 365:
        return f"{int(days / 365)}y"
    
    elif days >= 30:
        return f"{int(days / 30)}m" 
    
    elif days >= 7:
        return f"{int(days / 7)}w"

    elif days >= 1: 
        return f"{int(days)}d"

    elif seconds >= 3600:
         return "1d" if (days_and_above == True) else f"{int(seconds / 3600)}h"
    
    if seconds >= 60:
        return "1d" if (days_and_above == True) else f"{int(seconds / 60)}mi"
       
    else:
         return "1d" if (days_and_above == True) else f"{int(seconds)}s"
    


