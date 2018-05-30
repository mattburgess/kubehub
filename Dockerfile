FROM python:3.6-alpine
ADD . /kubehub
WORKDIR /kubehub
RUN pip install -r requirements.txt
CMD ["python", "kubehub/kubehub.py"]
