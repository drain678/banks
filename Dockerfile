FROM python:3.11 

WORKDIR /app 

COPY banks/ ./banks
COPY banks_app/ ./banks_app

COPY requirements.txt . 

COPY manage.py . 

RUN pip install -r requirements.txt   

# runs the production server
CMD python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000