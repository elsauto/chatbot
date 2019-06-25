FROM python:3.6-slim

RUN pip3 install --upgrade pip && pip3 install termcolor && pip3 install nltk

RUN ["python3", "-c", "import nltk; nltk.download('stopwords'); nltk.download('punkt')" ]

ADD food_ordering.py /

CMD ["python3", "/food_ordering.py"]