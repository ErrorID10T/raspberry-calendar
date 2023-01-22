from datetime import datetime
import calendar

def create_current_calendar():
    today = datetime.today()
    first_day_of_current_month, last_date_of_current_month = calendar.monthrange(today.year, today.month)

    #monthrange uses monday as first day, convert to Sunday as first day
    first_day_of_current_month = (first_day_of_current_month + 1) % 7

    if today.month == 1:
        _, last_date_of_previous_month = calendar.monthrange(today.year-1, 12)
    else:
        _, last_date_of_previous_month = calendar.monthrange(today.year, today.month-1)

    #create calendar array, length 35 for 5 rows of 7 days
    cal = [None] * 35
    for i in range(first_day_of_current_month):
        cal[i] = last_date_of_previous_month - first_day_of_current_month + i + 1
    for i in range(last_date_of_current_month):
        cal[i + first_day_of_current_month] = i + 1
    for i in range(last_date_of_current_month + first_day_of_current_month, 35):
        cal[i] = i - last_date_of_current_month - first_day_of_current_month + 1

    cal_weeks = []
    for week in range(5):
        cal_weeks.append(cal[week * 7:week * 7 + 7])

    return cal_weeks

if __name__ == "__main__":
    cal = create_current_calendar()
    print(*cal, sep='\n')