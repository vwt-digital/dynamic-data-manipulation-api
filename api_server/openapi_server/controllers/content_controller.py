import logging
import io
import pandas as pd

from datetime import datetime
from flask import g, make_response


def response_csv(response):
    """Returns the data as a CSV file"""

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    try:
        output = io.StringIO()

        df = pd.DataFrame(response)
        for col in df.select_dtypes(include=['datetimetz']):
            df[col] = df[col].apply(lambda a: a.tz_convert('Europe/Amsterdam').tz_localize(None))

        csv_response = df.to_csv(sep=";", index=False, decimal=",")

        output.write(csv_response)

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f"attachment; filename={timestamp}.csv"
        return response
    except Exception as e:
        logging.info(f"Generating CSV file failed: {str(e)}")
        return make_response('Something went wrong during the generation of a CSV file', 400)


def response_xlsx(response):
    """Returns the data as a XLSX file"""

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    try:
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        df = pd.DataFrame(response)
        for col in df.select_dtypes(include=['datetimetz']):
            df[col] = df[col].apply(lambda a: a.tz_convert('Europe/Amsterdam').tz_localize(None))

        df.to_excel(writer, sheet_name=g.db_table_name, index=False)
        writer.save()

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f"attachment; filename={g.db_table_name}_{timestamp}.xlsx"
        return response
    except Exception as e:
        logging.info(f"Generating XLSX file failed: {str(e)}")
        return make_response('Something went wrong during the generation of a XLSX file', 400)


def create_content_response(response, content_type):
    """Creates a response based on the request's content-type"""

    if content_type == 'text/csv':  # CSV
        return response_csv(response.get('results', response))
    elif content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':  # XLSX
        return response_xlsx(response.get('results', response))

    return response  # JSON
