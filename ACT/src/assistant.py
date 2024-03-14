from email import message
from openai import OpenAI
import time
import logging
from datetime import datetime

client = OpenAI()
model = 'gpt-3.5-turbo'

# harcode our ids:
assistant_id = None
thread_id = None

# === Create Assistant ===
class ACT_Assistant:
    def __init__(self, assistant_id, thread_id):
        self.assistant_id = assistant_id
        self.thread_id = thread_id

    def create_assistant(self):
        assistant = client.beta.assistants.create(
            name="ACT Assistant",
            instructions="""
            You are an ACT Assistant that generates the goal of an ACT tree node.
            An ACT is a n Answer_based_Tree that represents the structure of a document.
            Constructing_Answer_based_Tree(ACT, Answer) {
            Input: Answer
            Output: ACT tree

            Create an empty ACT tree with a root node R with Null values
            Expand ACT in such way that {
                all internal nodes are related to the section or subsection
                child nodes of a section node are subsections of the section or are paragraphs or captions in that section related to the section
                all leaf nodes are related to paragraphs to caption
                text of internal node is the title of the section
                text of a leaf node is paragraph or section
                For all leaf nodes N that are paragraphs, N.Goal = LLM_Pragraph_Main_Goal(N.Text)
                For all leaf nodes N that are captions, N.Goal is a summary of the caption
                For all internal node N, N.Goal = Union of all children goals
            }
        }
            """,
            model=model
        )
        self.assistant_id = assistant.id
        print(f"Assistant created with ID: {self.assistant_id}")
        return self.id

    def create_thread(self, user_message):
        thread = client.beta.threads.create(
            messages=[
                {
                    'role': 'user',
                    'content': user_message
                }
            ]
        )
        self.thread_id = thread.id
        print(f"Thread created with ID: {self.thread_id}")

    def send_message(self, message):
        message = client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role='user',
            content=message
        )
        print(f"Message sent: {message.content}")

    def run_assistant(self):
        run = client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions="Please generate the goal of an ACT tree paragraph node",
        )
        print(f"Assistant run created with ID: {run.id}")
        self.wait_for_run_completion(run.id)

    def wait_for_run_completion(self, run_id, sleep_interval=5):
        while True:
            try:
                run = client.beta.threads.runs.retrieve(thread_id=self.thread_id, run_id=run_id)
                if run.completed_at:
                    elapsed_time = run.completed_at - run.created_at
                    formatted_elapsed_time = time.strftime(
                        "%H:%M:%S", time.gmtime(elapsed_time)
                    )
                    print(f"Run completed in {formatted_elapsed_time}")
                    messages = client.beta.threads.messages.list(thread_id=self.thread_id)
                    last_message = messages.data[0]
                    response = last_message.content[0].text.value
                    print(f"Assistant Response: {response}")
                    break
            except Exception as e:
                print(f"An error occurred while retrieving the run: {e}")
                break
            print("Waiting for run to complete...")
            time.sleep(sleep_interval)


# === Create Assistant and Run ===
if not assistant_id or not thread_id:
    assistant = ACT_Assistant(None, None)
    assistant_id = assistant.create_assistant()
assistant.create_thread("What is the goal of an ACT tree paragraph node?")
assistant.send_message("I want to know the goal of an ACT tree paragraph node.")
assistant.run_assistant()


# message = 'What is the best way to lose fat and build lean muscles?'
# message = client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role='user',
#     content=message
# )

# run = client.beta.threads.runs.create(
#     thread_id=thread_id,
#     assistant_id=assistant_id,
#     instructions="Please address the user as James Bond", 
# )

# client.beta.assistants.delete(assistant_id='asst_YGQtM7ETpe6Cf19wwUiBaO6y')

# def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
#     """

#     Waits for a run to complete and prints the elapsed time.:param client: The OpenAI client object.
#     :param thread_id: The ID of the thread.
#     :param run_id: The ID of the run.
#     :param sleep_interval: Time in seconds to wait between checks.
#     """
#     while True:
#         try:
#             run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
#             if run.completed_at:
#                 elapsed_time = run.completed_at - run.created_at
#                 formatted_elapsed_time = time.strftime(
#                     "%H:%M:%S", time.gmtime(elapsed_time)
#                 )
#                 print(f"Run completed in {formatted_elapsed_time}")
#                 logging.info(f"Run completed in {formatted_elapsed_time}")
#                 # Get messages here once Run is completed!
#                 messages = client.beta.threads.messages.list(thread_id=thread_id)
#                 last_message = messages.data[0]
#                 response = last_message.content[0].text.value
#                 print(f"Assistant Response: {response}")
#                 break
#         except Exception as e:
#             logging.error(f"An error occurred while retrieving the run: {e}")
#             break
#         logging.info("Waiting for run to complete...")
#         time.sleep(sleep_interval)


# # === Run ===
# wait_for_run_completion(client=client, thread_id=thread_id, run_id=run.id)

# # ==== Steps --- Logs ==
# run_steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run.id)
# print(f"Steps---> {run_steps.data[0]}")