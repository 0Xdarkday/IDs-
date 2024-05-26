import os
import json
import base64
import requests
import logging

class Reporter:
    def __init__(self, ip: str, port: int, base_url: str = '/cgi-bin/api', report_endpoint: str = 'report.py', use_https: bool = False, log_file: str = 'logs/reporter.log'):
        self.ip = ip
        self.port = port
        self.protocol = 'https' if use_https else 'http'
        self.base_url = base_url
        self.report_endpoint = report_endpoint
        self.reports = []  # Store reports
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, filename=log_file, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def report(self, message: dict):
        """
        Send a report to the configured server.

        Args:
            message (dict): The message to report.
        """
        try:
            json_payload = base64.b64encode(json.dumps(message).encode('ascii')).decode('utf8')
            self.logger.info(f"Reporting packet: {json_payload}")

            url = f'{self.protocol}://{self.ip}:{self.port}{self.base_url}{self.report_endpoint}'
            response = requests.get(url, params={'data': json_payload})
            response.raise_for_status()
            self.logger.info(f"Report sent successfully: {response.text}")
        except (requests.ConnectionError, requests.HTTPError, requests.RequestException) as e:
            self.logger.exception(f"Error while sending report: {e}")

    def report_attack(self, attack_type: str, src_ip: str, details: dict):
        """
        Report an attack to the configured server.

        Args:
            attack_type (str): The type of attack detected.
            src_ip (str): The source IP address of the attack.
            details (dict): Additional details about the attack.
        """
        report_data = {
            'attack_type': attack_type,
            'src_ip': src_ip,
            'details': details
        }
        self.logger.info(f"Reporting attack: {attack_type} from {src_ip}")
        self.report(report_data)
        
    def generate_html_report(self, output_file: str):
        """
        Generate an HTML report.
        """
        with open('template.html', 'r') as template_file:
            html_template = template_file.read()

        report_content = ""
        for report in self.reports:
            report_content += f"""
            <tr>
                <td>{report['attack_type']}</td>
                <td>{report['src_ip']}</td>
                <td>{json.dumps(report['details'])}</td>
            </tr>
            """

        html_content = html_template.replace('<!-- REPORT_CONTENT -->', report_content)

        with open(output_file, 'w') as file:
            file.write(html_content)
