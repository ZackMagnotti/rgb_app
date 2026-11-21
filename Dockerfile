FROM python
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir upload
CMD [ \
	"flask", \
	"--app", \
	"rgb_app/app.py", \
	"run", \
	"--with-threads", \
	"--host=0.0.0.0" \
]
