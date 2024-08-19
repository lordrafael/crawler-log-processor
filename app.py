from flask import Flask, request, Response
import io
import csv

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'The Flask app is running!'

def filter_googlebot_logs(log_data: str) -> str:
    """Filters log records containing 'Googlebot' or 'Googlebot-Image'."""
    return "\n".join(line for line in log_data.splitlines() if "Googlebot" in line or "Googlebot-Image" in line)

def convert_logs_to_csv(filtered_logs: str) -> io.StringIO:
    """Converts filtered log lines into CSV format."""
    csv_file = io.StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(["URL", "ResponseCode", "Date_Time", "Crawler"])

    for line in filtered_logs.splitlines():
        parts = line.split(' ')
        url = parts[1] + parts[6]
        responseCode = parts[8]
        date = parts[3]
        crawler = ' '.join(parts[11:])
        writer.writerow([url, responseCode, date, crawler])

    csv_file.seek(0)
    return csv_file

@app.route('/process-log', methods=['POST'])
def process_log():
    if 'file' not in request.files:
        return ('No file part', 400)

    file = request.files['file']
    
    if not file.filename.endswith(".log"):
        return ('Invalid file format. Please upload a .log file.', 400)

    log_data = file.read().decode('utf-8')
    filtered_logs = filter_googlebot_logs(log_data)

    if not filtered_logs:
        return ('No Googlebot records found in the log file.', 404)

    csv_file = convert_logs_to_csv(filtered_logs)

    return Response(
        csv_file.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=filtered_googlebot_logs.csv'
        }
    )

if __name__ == '__main__':
    app.run(debug=True)
