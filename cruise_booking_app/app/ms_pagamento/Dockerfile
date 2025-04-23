FROM python:3.11-slim

WORKDIR /app

COPY app/ms_pagamento /app/app/ms_pagamento
COPY app/shared      /app/app/shared
COPY app/ms_pagamento/keys /app/app/ms_pagamento/keys
COPY app/ms_pagamento/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["python", "app/ms_pagamento/main.py"]
