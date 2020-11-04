import logging
import io
import pandas as pd

from datetime import datetime
from flask import make_response


def response_csv(response):
    """Returns the data as a CSV file"""

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    try:
        output = io.StringIO()

        df = pd.DataFrame(response)
        csv_response = df.to_csv(sep=";", index=False, decimal=",")

        output.write(csv_response)

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f"attachment; filename={timestamp}.csv"
        return response
    except Exception as e:
        logging.info(f"Generating CSV file failed: {str(e)}")
        return make_response('Something went wrong during the generation of a CSV file', 400)


def create_content_response(response, content_type):
    """Creates a response based on the request's content-type"""

    if content_type == 'text/csv':
        return response_csv(response.get('results', response))

    return response  # application/json
