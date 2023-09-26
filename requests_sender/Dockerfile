FROM python:3.10-buster
COPY requests_sender.py requests_sender.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt update && apt install -y curl unzip groff
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
	./aws/install
CMD [ "python",  "./requests_sender.py" ]