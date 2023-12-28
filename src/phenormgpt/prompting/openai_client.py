import openai
import time
from typing import List

from prompting.openai_dataset_analysis import num_tokens_from_messages

TOKEN_LIMIT = 8_000
DURATION_LIMIT = 60 # seconds

# Class for API use. Not only for requests...
class Request:
    def __init__(self, token_count, request_time):
        self.token_count = token_count
        self.request_time = request_time
    
    def has_expired(self) -> bool:
        time_passed = time.time() - self.request_time
        return time_passed > DURATION_LIMIT

class ApiKeyTracker:
    def __init__(self):
        self.requests = []

    def add_request(self, request: Request):
        self.requests.append(request)
    
    def remove_request(self, request: Request):
        self.requests.remove(request)
    
    # Removes request older than a minute, since Rate Limits are bound to last 60 seconds.
    def purge_requests(self):
        current_time = time.time()
        for request in self.requests:
            if request.has_expired():
                self.remove_request(request)
    
    def get_tokens_used(self) -> int:
        total_tokens = 0
        for request in self.requests:
            total_tokens += request.token_count
        return total_tokens
           
    # Waits until we are clear to submit a new request with specified number of tokens
    def prepare_for_tokens(self, num_tokens: int):
        while (self.get_tokens_used() + num_tokens) > TOKEN_LIMIT:
            time.sleep(.1)
            self.purge_requests()
                
class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo-0613", debug: bool = True):
        self.api_key = api_key
        openai.api_key = api_key
        self.api_key_tracker = ApiKeyTracker()
        self.model = model
        self.debug = debug
         
    def get_response(self, messages: List[dict]) -> str:
        
        num_tokens = num_tokens_from_messages(messages)
        if self.debug:
            print('Request tokens: %d.' % int(num_tokens))
            
        self.api_key_tracker.prepare_for_tokens(num_tokens)
        
        if self.debug:
            print('TPM: %d.' % self.api_key_tracker.get_tokens_used())
        
        awaiting_response = True
        while awaiting_response:
            try:
                #print('Sending request to OpenAI API...')
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=0,
                    max_tokens=1550,
                    top_p=0.01,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                #print('Response received.')
                awaiting_response = False
            except openai.error.RateLimitError as e:
                print('Encountered RateLimitError, retrying...')
                print(e)
                time.sleep(10)
            except openai.error.InvalidRequestError as e:
                print('Encountered InvalidRequestError, stopping...')
                print(messages)
                print(e)
                exit()
            except Exception as e:
                print('Encountered exception, retrying...')
                print(e)
                time.sleep(5)
        
        total_tokens = response['usage']['total_tokens']
        if self.debug:
            print('Total tokens: %d.' % int(total_tokens))
        
        '''
        response_tokens = response['usage']['completion_tokens'] 
        response_request = Request(response_tokens, time.time())
        '''
        response_request = Request(total_tokens, time.time())
        self.api_key_tracker.add_request(response_request)
        
        answer = response['choices'][0]['message']['content']
        return answer
    
class FinetuningOpenAIClient(OpenAIClient):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo-0613", debug: bool = True):
        super().__init__(api_key, model, debug)
        self.train_file_id = None
        self.val_file_id = None
        self.finetune_job_id = None
        self.finetuned_model = None

    def upload_file(self, filepath: str, purpose: str = "fine-tune") -> str:
        response = openai.File.create(file=open(filepath, "rb"), purpose="fine-tune")
        file_id = response["id"]
        return file_id
    
    def upload_train_file(self, filepath: str = '../output/finetune_datasets/train.json') -> str:
        self.train_file_id = self.upload_file(filepath)
        if self.debug:
            print('Uploaded training file: %s.' % self.train_file_id)
        return self.train_file_id
    
    def upload_val_file(self, filepath: str = '../output/finetune_datasets/val.json') -> str:
        self.val_file_id = self.upload_file(filepath)
        if self.debug:
            print('Uploaded validation file: %s.' % self.val_file_id)
        return self.val_file_id
    
    def finetune(self, name: str = 'bc-f') -> str:
        response = openai.FineTuningJob.create(
            training_file=self.train_file_id,
            validation_file=self.val_file_id,
            model=self.model,
            suffix=name,
        )
        self.finetune_job_id = response["id"]
        if self.debug:
            print('Began fine-tuning job: %s.' % self.finetune_job_id)
        return self.finetune_job_id

    def retrieve_finetune_job(self) -> dict:
        return openai.FineTuningJob.retrieve(self.finetune_job_id)
    
    def get_finetuned_model(self) -> str:
        job = self.retrieve_finetune_job()
        status = job['status']
        if status == 'running':
            if self.debug:
                print('Fine-tuning in progress, please try again later.')
            return 'TBD'
        elif status == 'succeeded':
            self.finetuned_model = job['fine_tuned_model']
            if self.debug:
                print('Finished tuning model: %s.' % self.finetuned_model)
            return self.finetuned_model
        else:
            if self.debug:
                print('Unknown status: %s.' % status)
            pass #TODO

    def use_finetuned_model(self):
        if self.debug and self.model.startswith('ft'):
            print('Warning: Switching away from fine-tuned model %s.' % self.model)
        self.model = self.finetuned_model
        if self.debug:
            print('Switched to %s.' % self.model)