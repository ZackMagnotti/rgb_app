FROM flask
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /root
CMD [ \
	"flask", \
	"--app", \
	"rgb_site/app.py", \
	"run", \
	"--with-threads", \
	"--host=0.0.0.0" \
]
