import os
from dotenv import load_dotenv

from GPT_assistant.base_assistant import BaseAssistant
from log.log import Log
from utilities.utils import save_to_env_file

load_dotenv()  # Load environment variables

ACT_MODEL = "gpt-4-0125-preview"
ACT_MODEL_NAME = "ACT_ASSISTANT"
ACT_MODEL_ID = f"{ACT_MODEL_NAME}_ID"
ACT_THREAD_ID = f"{ACT_MODEL_NAME}_THREAD_ID"
# === Create Assistant ===


class ACTAssistant(BaseAssistant):
    ASSISTANT_INSTRUCTIONS = "Please extract the main goal or abstractive summary of a text for a paragraph node"
    CREATE_THREAD_MESSAGE = "Hello, I have a paragraph that I would like to summarize."
    SINGLE_PARAGRAPH_GOAL = """Please extract the main goal or abstractive summary of a text for a paragraph node,
            main goal need to cover all concept mention in the text. Please provide the goal in less than 3 bullet points."""

    def __init__(self, assistant_id=None, thread_id=None):
        logger = Log("ACT_Assistant", "act_assistant.log")
        super().__init__(ACT_MODEL_NAME, assistant_id, thread_id, logger)

        ASSISTANT_ID = os.getenv(ACT_MODEL_ID)
        THREAD_ID = os.getenv(ACT_THREAD_ID)

        if not ASSISTANT_ID and not assistant_id:
            ASSISTANT_ID = self.create_assistant(
                ACT_MODEL_NAME, self.ASSISTANT_INSTRUCTIONS, ACT_MODEL
            )
            save_to_env_file(ACT_MODEL_ID, ASSISTANT_ID)

        if not THREAD_ID and not thread_id:
            THREAD_ID = self.create_thread(self.CREATE_THREAD_MESSAGE)
            save_to_env_file(ACT_THREAD_ID, THREAD_ID)

        self.assistant_id = ASSISTANT_ID or assistant_id
        self.thread_id = THREAD_ID or thread_id

    def run_assistant_single_paragraph(self, instructions=None):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions=instructions or self.SINGLE_PARAGRAPH_GOAL,
        )
        self.logger.info(f"Assistant run created with ID: {run.id}")
        return self.wait_for_run_completion(run.id)


# assistant = ACT_Assistant()

# SAMPLE_PARAGRAPH = """
# ITIC global as many big names partner under their belt and the deliverable products they are
# working with has vast concept in upcoming times like cloud services, networking, cyber
# security, The ITIC is providing great opportunities to the new students of background of data
# science, cyber security and network engineers as well as it also providing the research
# centre for artificial intelligence which is remarkable and giving hands on experience of
# working on Telstra product and services for the students its big opportunity to grab in this
# crucial times where pandemic has given us big hit in all regards to have the opportunity to
# explore all these learning from the university was quite a challenge due to past
# circumstances while ITIC has taken the lead in that learning department and providing the
# chance to learn in professional environment will open new gates of opportunities for the
# students. The career consulting you get while getting their training program it should be
# highlighted here as it’s not an easy thing to get in real world. ITIC is doing an great job of
# creating opportunities in all big tech fields which is going to change the world and having
# experience to learn on cisco technologies for networking students is a great way of
# experiencing their theoretical concepts.
# """
# assistant.add_message_to_thread("Paragraph:\n" + SAMPLE_PARAGRAPH)
# assistant.run_assistant_single_paragraph()
