from celery import shared_task
import time

@shared_task
def generate_report(report_id):
    time.sleep(5)
    return f"Report {report_id} generated."

@shared_task
def process_image(image_path):
    time.sleep(3)
    return f"Image at {image_path} processed."


