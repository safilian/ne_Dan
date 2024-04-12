from email import message
from venv import create
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

client = OpenAI()
model = 'gpt-4-0125-preview'


def save_to_env_file(key, value):
    with open(".env", "a") as f:  # Append mode
        f.write(f"{key}={value}\n")

# === Create Assistant ===


class ACT_Assistant:
    def __init__(self, assistant_id=None, thread_id=None):
        ASSISTANT_ID = os.getenv("ASSISTANT_ID")

        if not ASSISTANT_ID:
            ASSISTANT_ID = self.create_assistant()
            save_to_env_file("ASSISTANT_ID", ASSISTANT_ID)

        if not thread_id:
            thread_id = self.create_thread(
                "Hello, I have a paragraph that I would like to summarize.")

        self.assistant_id = ASSISTANT_ID
        self.thread_id = thread_id

    def create_assistant(self):
        assistant = client.beta.assistants.create(
            name="Paragraph Summary Assistant",
            instructions="""
            You are an assistant speacialised in summarizing paragraphs.
            }
            """,
            model=model
        )
        ASSISTANT_ID = assistant.id
        print(f"Assistant created with ID: {ASSISTANT_ID}")

        self.assistant_id = ASSISTANT_ID
        return self.assistant_id

    def create_thread(self, user_message):
        thread = client.beta.threads.create(
            messages=[
                {
                    'role': 'user',
                    'content': user_message
                }
            ]
        )
        print(f"Thread created with ID: {thread.id}")

        self.thread_id = thread.id
        return self.thread_id

    def send_message(self, message):
        message = client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role='user',
            content=message
        )
        print(f"Message sent: {message.content}")

    def run_assistant_single_paragraph(self):
        run = client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions="""Please extract the main goal or abstractive summary of a text for a paragraph node, 
            main goal need to cover all concept mention in the text. Please provide the goal in less than 3 bullet points.""",
        )
        print(f"Assistant run created with ID: {run.id}")
        return self.wait_for_run_completion(run.id)

    def wait_for_run_completion(self, run_id, sleep_interval=5, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                run = client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id, run_id=run_id)
                if run.completed_at:
                    elapsed_time = run.completed_at - run.created_at
                    formatted_elapsed_time = time.strftime(
                        "%H:%M:%S", time.gmtime(elapsed_time)
                    )
                    print(f"Run completed in {formatted_elapsed_time}")
                    messages = client.beta.threads.messages.list(
                        thread_id=self.thread_id)
                    last_message = messages.data[0]
                    response = last_message.content[0].text.value
                    print(f"Assistant Response: {response}")
                    return response
            except Exception as e:
                print(f"An error occurred while retrieving the run: {e}")
                retries += 1
                if retries < max_retries:
                    print(f"Retrying in {sleep_interval} seconds...")
                    time.sleep(sleep_interval)
                else:
                    print("Maximum retries exceeded. Terminating the run.")
                    # self.delete_thread_by_id(self.thread_id)
                    return None
        else:
            print("Maximum retries exceeded. Terminating the run.")
            self.delete_thread_by_id(self.thread_id)

        def delete_thread_by_id(self, thread_id):
            client.beta.threads.delete(thread_id=thread_id)
            print(f"Thread {thread_id} deleted")

        def list_all_threads(self):
            threads = client.beta.threads.list()
            print(f"Threads: {threads}")

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
# assistant.send_message("Paragraph:\n" + SAMPLE_PARAGRAPH)
# assistant.run_assistant_single_paragraph()
