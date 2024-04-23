from .assistant import ACTAssistant
from log.log import Log

logger = Log("act_jobs", "act_jobs.log")


def process_paragraph_job(text):
    try:
        act_assistant = ACTAssistant()
        act_assistant.add_message_to_thread("Paragraph:\n" + text)
        return act_assistant.run_assistant_single_paragraph()
    except Exception as e:
        logger.error(f"Error in processing paragraph job: {e}")
        raise e
