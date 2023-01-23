import tkinter
import calendar
import time
import os
import json

from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk

def create_current_calendar():
    #returns a list (rows) of lists (columns) resembling a monthly calendar
    #values are tuples, first value is day of month, second value:
        #0 - outside current month
        #1 - current month
        #2 - current day
    today = datetime.today()
    first_day_of_current_month, last_date_of_current_month = calendar.monthrange(today.year, today.month)

    #monthrange uses monday as first day, convert to Sunday as first day
    first_day_of_current_month = (first_day_of_current_month + 1) % 7

    #find last date of previous month
    if today.month == 1:
        _, last_date_of_previous_month = calendar.monthrange(today.year-1, 12)
    else:
        _, last_date_of_previous_month = calendar.monthrange(today.year, today.month-1)

    #create calendar array, length 35 for 5 rows of 7 days
    cal = [None] * 35
    for i in range(first_day_of_current_month):
        cal[i] = (last_date_of_previous_month - first_day_of_current_month + i + 1, 0)
    for i in range(last_date_of_current_month):
        cal[i + first_day_of_current_month] = (i + 1, 2 if i +1 == today.day else 1)
    for i in range(last_date_of_current_month + first_day_of_current_month, 35):
        cal[i] = (i - last_date_of_current_month - first_day_of_current_month + 1, 0)

    #convert calendar array to a list of 5 lists of 7 days
    cal_weeks = []
    for week in range(5):
        cal_weeks.append(cal[week * 7:week * 7 + 7])

    return cal_weeks

def load_image(file: str) -> object:
    global picture_frame

    window.update()
    frame_width = picture_frame.winfo_width()
    frame_height = picture_frame.winfo_height()
    
    picture = Image.open(file)

    # determine best way to resize and maintain aspect ratio
    height_ratio = picture.height / frame_height
    width_ratio = picture.width / frame_width
    
    if height_ratio > width_ratio:
        new_height = frame_height
        new_width = int(picture.width / height_ratio)
    else:
        new_width = frame_width
        new_height = int(picture.height / width_ratio)

    # the lazy way to deal with rounding errors
    if new_height > frame_height:
        new_height = frame_height
    if new_width > frame_width:
        new_width = frame_width

    resized_picture = picture.resize((new_width, new_height), Image.LANCZOS)
    new_picture = ImageTk.PhotoImage(resized_picture)
    
    return new_width, new_height, new_picture

def picture_rotator() -> str:
    global picture_interval_count

    new_picture_count = int( (time.time()-time.timezone) / settings['picture_change_interval'])
    
    supported_picture_types = ('jpg', 'jpeg', 'png')

    if picture_interval_count != new_picture_count:
        picture_interval_count = new_picture_count

        files = os.listdir(settings['picture_directory'])

        pictures = []

        #remove unsupported files
        for file in files:
            for extension in supported_picture_types:
                if file.endswith(extension):
                    pictures.append(file)
                    break

        pictures.sort()

        number_of_pictures = len(pictures)

        picture = int(picture_interval_count % number_of_pictures)
        return pictures[picture]

    else:
        return picture_name

def update_calendar() -> None:
    global calendar_frame

    calendar = create_current_calendar()

    for row in range(7):
        calendar_frame.rowconfigure(row, weight=10)
    for column in range(9):
        calendar_frame.columnconfigure(column, weight=10)

    for week in range(5):
        for day in range(7):
            date = calendar[week][day][0]
            date_type = calendar[week][day][1]

            #outside current month
            if date_type == 0:
                background_color = settings['calendar_other_month_background_color']
                text_color = settings['calendar_other_month_text_color']
                text_size = settings['calendar_other_month_text_size']
                text_font = settings['calendar_other_month_text_font']

            #current month
            elif date_type == 1:
                background_color = settings['calendar_current_month_background_color']
                text_color = settings['calendar_current_month_text_color']
                text_size = settings['calendar_current_month_text_size']
                text_font = settings['calendar_current_month_text_font']

            #current day
            elif date_type == 2:
                background_color = settings['calendar_current_day_background_color']
                text_color = settings['calendar_current_day_text_color']
                text_size = settings['calendar_current_day_text_size']
                text_font = settings['calendar_current_day_text_font']

            tkinter.Label(calendar_frame,
                          text=date,
                          background=background_color,
                          foreground=text_color,
                          font=(text_font, text_size)
                          ).grid(row=week+1, column=day+1, sticky='NSEW')

def update_clock() -> None:
        global day_name_label
        global time_label
        global month_label

        day = datetime.now().day
        day_name = datetime.now().strftime('%A')
        month = datetime.now().strftime('%B')
        year = datetime.now().year
        second = datetime.now().second
        hour = datetime.now().hour
        minute = datetime.now().minute
        ampm = datetime.now().strftime('%p')

        day_name_label.config(text=day_name)
        time_label.config(text=f'{hour:02}:{minute:02}:{second:02} {ampm}')
        month_label.config(text=f'{month} {day}, {year}')

def update_picture() -> None:
    global picture_frame
    global picture

    picture_width, picture_height, picture = load_image(f'{settings["picture_directory"]}/{picture_name}')

    try:
        picture_frame.configure(image=picture)
    except Exception as e:
        print(e)

def update():
    global window
    global day_of_month
    global calendar_frame
    global picture_name
    global settings_modified_time
    global settings

    if int(time.time()) % 10 == 0:
        new_settings_modified_time = os.path.getmtime(config_file_path)
        if settings_modified_time != new_settings_modified_time:
            settings_modified_time = new_settings_modified_time
            with open(config_file_path,'r',encoding='utf-8') as settings_file:
                settings = json.load(settings_file)

    update_clock()

    if day_of_month != datetime.now().day:
        day_of_month = datetime.now().day
        for widget in calendar_frame.winfo_children():
            widget.destroy()
        update_calendar()
    
    new_picture_name = picture_rotator()
    if picture_name != new_picture_name:
        picture_name = new_picture_name
        update_picture()

    delay = 1000 - int(datetime.now().microsecond/1000)
    #print(f'delay: {delay} ms')
    window.after(delay, update)

if __name__ == "__main__":

    day_of_month = None
    picture_interval_count = None
    picture_name = None
    picture = None
    config_file_path = 'config.json'

    settings_modified_time = os.path.getmtime(config_file_path)

    with open('config.json','r',encoding='utf-8') as settings_file:
        settings = json.load(settings_file)

    window = tkinter.Tk()
    window.title("Clock")
    window.attributes('-fullscreen',True)

    #create window with two rows, two columns, all equal size
    window.columnconfigure(0, weight=1, uniform=True)
    window.columnconfigure(1, weight=1, uniform=True)
    window.rowconfigure(0, weight=1, uniform=True)
    window.rowconfigure(1, weight=1, uniform=True)

    #create grid
    picture_frame = tkinter.Label(window)
    picture_frame.configure(width=int(window.winfo_width()/2),
                            background=settings['picture_background_color'],
                            border=False,
                            image=None)
    picture_frame.grid(row=0, column=0, sticky='nsew', rowspan=2)
        
    datetime_frame = tkinter.Frame(window)
    datetime_frame.configure(background=settings['clock_background_color'], border=False)
    datetime_frame.grid(row=0, column=1, sticky='nsew')

    calendar_frame = tkinter.Frame(window)
    calendar_frame.configure(background=settings['calendar_background_color'], border=False)
    calendar_frame.grid(row=1, column=1, sticky='nsew')

    #initialize clock
    datetime_frame.rowconfigure(0, weight=10)
    datetime_frame.rowconfigure(1, weight=10)
    datetime_frame.rowconfigure(2, weight=10)
    datetime_frame.columnconfigure(0, weight=10)
    
    day_name_label = tkinter.Label(datetime_frame,
                                   text='loading',
                                   background=settings['clock_background_color'],
                                   foreground=settings['clock_weekday_text_color'],
                                   font=(settings['clock_weekday_text_font'], settings['clock_weekday_text_size']))
    day_name_label.grid(row=0)
    time_label = tkinter.Label(datetime_frame,
                               text='loading',
                               background=settings['clock_background_color'],
                               foreground=settings['clock_time_text_color'],
                               font=(settings['clock_time_text_font'], settings['clock_time_text_size']))
    time_label.grid(row=1)
    month_label = tkinter.Label(datetime_frame,
                                text='loading',
                                background=settings['clock_background_color'],
                                foreground=settings['clock_date_text_color'],
                                font=(settings['clock_date_text_font'], settings['clock_date_text_size']))
    month_label.grid(row=2)
        
    window.after(1000, update)

    #launch window
    window.mainloop()

    try:
        window.destroy()
    except:
        ...
