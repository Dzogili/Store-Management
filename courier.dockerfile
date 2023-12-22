FROM python:3

RUN mkdir -p /opt/DomaciZadatak/applications/courier
WORKDIR /opt/DomaciZadatak/applications/courier

COPY ./applications/courier/application.py ./application.py
COPY ./applications/requirements.txt ../requirements.txt
COPY ./applications/configuration.py ../configuration.py
COPY ./applications/models.py ../models.py
COPY ./roleCheck.py ../../roleCheck.py

RUN pip install -r ../requirements.txt

ENV PYTHONPATH="/opt/DomaciZadatak"

ENTRYPOINT ["python", "./application.py"]
