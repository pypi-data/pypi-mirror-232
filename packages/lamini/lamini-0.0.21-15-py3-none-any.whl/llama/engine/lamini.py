import requests
import time

from llama.program.util.run_ai import get_url_and_key
from llama.program.util.config import edit_config


class Lamini:
    def __init__(self, id, model_name, prompt_template=None, key=None):
        self.id = id
        self.model_name = model_name
        self.key = key
        self.prompt_template = prompt_template
        edit_config()
        key, url = get_url_and_key()
        if self.key is None:
            self.key = key
        self.api_prefix = url + "/v2/lamini/"

    """
    https://lamini-ai.github.io/API/completions/

    - arguments are maps
    - user can optionally specify type in output_type like "Answer#bool"
      valid types are:
        'string'/'str', 'integer'/'int', 'float'/'number', 'bool'/'boolean'
    - input type is runtime type of input value.
      if runtime type is not a valid type above, then default to string
    
    Ex 1:
      input_value = {"question": "What is the hottest day of the year?"}
      output_type = {"Answer": "An answer to the question"}
    Ex 2:
      input_value = {"question": "What is the hottest day of the year?",
                     "question2": "What is for lunch?"}
      output_type = {"Answer": "An answer to the question",
                     "Answer2": "An answer to the question2"}
    """

    def __call__(
        self,
        input_value,
        output_type,
        stop_tokens=None,
    ):
        req_data = self.make_llm_req_map(
            input_value,
            output_type,
            stop_tokens,
        )
        url = self.api_prefix + "completions"

        return self.make_web_request(url, "post", req_data)

    # https://lamini-ai.github.io/API/data/
    # data must be a single map or a list of maps
    # cannot be a list of input/output map pairs
    def save_data(self, data):
        req_data = self.make_save_data_req_map(data)
        url = self.api_prefix + "data"

        return self.make_web_request(url, "post", req_data)

    # https://lamini-ai.github.io/API/train/
    # just submit the job, no polling
    def train_async(self):
        req_data = {"id": self.id, "model_name": self.model_name}
        url = self.api_prefix + "train"

        return self.make_web_request(url, "post", req_data)

    # https://lamini-ai.github.io/API/train/
    # continuously poll until the job is completed
    def train(self, **kwargs):
        job = self.train_async()

        try:
            status = self.check_job_status(job["job_id"])
            if status["status"] == "FAILED":
                print(f"Job failed: {status}")
                return status

            while status["status"] not in ("COMPLETED", "FAILED", "CANCELLED"):
                if kwargs.get("verbose", False):
                    print(f"job not done. waiting... {status}")
                time.sleep(30)
                status = self.check_job_status(job["job_id"])
                if status["status"] == "FAILED":
                    print(f"Job failed: {status}")
                    return status
                elif status["status"] == "CANCELLED":
                    print(f"Job canceled: {status}")
                    return status
            print(
                f"Finetuning process completed, model name is: {status['model_name']}"
            )
        except KeyboardInterrupt as e:
            print("Cancelling job")
            return self.cancel_job(job["job_id"])

        return status

    # https://lamini-ai.github.io/API/data/
    # data can only be a list of input/output map pairs, like
    # [[input_map1, output_map1], [input_map2, output_map2], ...]
    def save_data_pairs(self, data):
        req_data = self.make_save_data_pairs_req_map(data)
        url = self.api_prefix + "data_pairs"
        print(req_data)
        return self.make_web_request(url, "post", req_data)

    # https://lamini-ai.github.io/API/train_job_cancel/
    def cancel_job(self, job_id):
        url = self.api_prefix + "train/jobs/" + str(job_id) + "/cancel"

        return self.make_web_request(url, "post", {})

    # https://lamini-ai.github.io/API/train_job_status/
    def check_job_status(self, job_id):
        url = self.api_prefix + "train/jobs/" + str(job_id)

        return self.make_web_request(url, "get", {})

    # https://lamini-ai.github.io/API/eval_results/#request
    def evaluate(self, job_id):
        url = self.api_prefix + "train/jobs/" + str(job_id) + "/eval"

        return self.make_web_request(url, "get", {})

    # https://lamini-ai.github.io/API/delete_data/
    def delete_data(self, id):
        url = self.api_prefix + "delete_data"

        return self.make_web_request(url, "post", {"id": id})

    def make_web_request(self, url, http_method, json):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.key,
        }
        if http_method == "post":
            resp = requests.post(url=url, headers=headers, json=json)
        elif http_method == "get":
            resp = requests.get(url=url, headers=headers)
        else:
            raise Exception("http_method must be 'post' or 'get'")

        resp.raise_for_status()

        return resp.json()

    # check if two maps have the same keys and value types
    def same_type(self, t1, t2):
        if t1.keys() != t2.keys():
            return False

        for k in t1.keys():
            if type(t1[k]) != type(t2[k]):
                return False

        return True

    def make_save_data_req_map(self, data):
        req_data = {}
        req_data["id"] = self.id
        req_data["data"] = []

        if type(data) != list:
            data = [data]

        for d in data:
            if type(d) != dict:
                raise TypeError("type must be a list of maps or a single map")

            if not self.same_type(data[0], d):
                raise TypeError("all maps must have the same keys and value types")

            req_data["data"].append(d)

        return req_data

    def make_save_data_pairs_req_map(self, data):
        req_data = {}
        req_data["id"] = self.id
        req_data["data"] = []
        type_err_msg = "data must be in the form [[input_map1, output_map1], [input_map2, output_map2], ...]"

        if type(data) != list:
            raise TypeError(type_err_msg)

        for d in data:
            if len(d) != 2:
                raise TypeError(type_err_msg)

            input_data = d[0]
            output_data = d[1]

            if (
                type(input_data) != dict
                or type(output_data) != dict
                or not self.same_type(input_data, data[0][0])
                or not self.same_type(output_data, data[0][1])
            ):
                raise TypeError(type_err_msg)

            req_data["data"].append(d)

        return req_data

    def make_llm_req_map(
        self,
        input_value,
        output_type,
        stop_tokens=None,
    ):
        req_data = {}
        req_data["id"] = self.id
        req_data["model_name"] = self.model_name
        req_data["in_value"] = input_value
        req_data["out_type"] = output_type
        if self.prompt_template:
            req_data["prompt_template"] = self.prompt_template
        if stop_tokens:
            req_data["stop_tokens"] = stop_tokens

        return req_data

    def make_llm_input_type(self, input_value):
        in_type = {}
        in_type["title"] = ""
        in_type["properties"] = {}

        for k, v in input_value.items():
            vt = type(v)
            if vt == int:
                v_type = "integer"
            elif vt == float:
                v_type = "number"
            elif vt == bool:
                v_type = "boolean"
            else:
                v_type = "string"

            in_type["properties"][k] = {"description": "", "type": v_type}

        return in_type
