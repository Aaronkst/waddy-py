from openai import OpenAI

class Waddy():
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
        )

    def basic_run(self, messages, assistant_id):
        try:
            stream = self.client.beta.threads.create_and_run(
                assistant_id=assistant_id, thread={"messages": messages}, stream=True
            )
            for event in stream:
                if (
                    event.event == "thread.created"
                    and event.data.id
                ):
                    print('created thread:', event.data.id)
                elif event.event == "thread.message.delta" and event.data.delta.content:
                    if event.data.delta.content[0].type == "text":
                        current_content = event.data.delta.content[0].text.value or ""
                        yield f"data: {current_content}\n\n"
                    else:
                        print(event.data.delta.content[0])
                elif event.event == "thread.run.completed":
                    print("\n----")
                    print(event.data.usage) # Total tokens
                    # NOTE: Save to DB rather than yeilding
                    # yield f"data: {str(event.data.usage)}\n\n"
        except Exception as e:
            print("Error in creating thread and run from openAI:", str(e))
            raise e


    def _get_thread_messages(self, thread_id: str, after="", messages=[]):
        try:
            message_list = self.client.beta.threads.messages.list(thread_id, after=after)
            for message in message_list.data:
                messages.append(message)
            if message_list.has_more is True and message_list.last_id:
                self._get_thread_messages(thread_id, after=message_list.last_id, messages=messages)
            else:
                return messages
        except Exception as e:
            print("Error in getting thread details:", str(e))
            raise e

    def get_thread_details(self, thread_id):
        try:
            print('getting thread details')
            thread_details = self.client.beta.threads.retrieve(thread_id)
            messages = []
            self._get_thread_messages(thread_id, messages=messages)
            return {
                **thread_details.__dict__,  # Convert the Thread object to a dictionary
                "messages": messages   # Add messages to the details
            }
        except Exception as e:
            print('Error in getting message list:', str(e))
            raise e
