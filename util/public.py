# 时间转字符串
def date2str(date):
    if date:
        if isinstance(date, str):
            return date
        else:
            return date.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return "0000-00-00 00:00:00"