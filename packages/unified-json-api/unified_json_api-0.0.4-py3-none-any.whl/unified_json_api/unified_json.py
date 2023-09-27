import json
from typing import Dict
from dotenv import load_dotenv


from unified_json_api.constants_unified_json import ConstantsUnifiedJson

load_dotenv()
from logger_local.Logger import Logger  # noqa: E402

logger = Logger.create_logger(object=ConstantsUnifiedJson.OBJECT_FOR_LOGGER_CODE)


# Our Unified JSON structure
UNIFIED_JSON = {
    "modelId": "your_model_id",
    "contentType": "application/json",
    "accept": "*/*",
    "body": {
        # Another option for stability ai is to use "inputText": [{"text": "your_input_text1"}, {"text": "your_input_text2"}, {"text": "your_input_text3}]
        "inputText": "your_input_text",
        "textGenerationConfig": {
            "maxTokenCount": 50,
            "stopSequences": [],
            "temperature": 0,
            "topP": 1,
            "topK": 1,
            "countPenalty": {
                "scale": 0
            },
            "presencePenalty": {
                "scale": 0
            },
            "frequencyPenalty": {
                "scale": 0
            },
            "cfg_scale": 50,
            "seed": 0,
            "steps": 1
        }
    }
}

# Unified json is identical to TEST_REQUEST_TITAN_TEXT_LARGE json


class UnifiedJson:
    def __init__(self, unified_json: Dict[str, any]):
        self.unified_json = unified_json

    def get_bedrock_titan_json(self) -> Dict[str, any]:
        return self.unified_json

    def get_bedrock_jurassic_json(self) -> Dict[str, any]:
        jurassic_json = {}
        jurassic_json["modelId"] = self.unified_json["modelId"]
        jurassic_json["contentType"] = self.unified_json["contentType"]
        jurassic_json["accept"] = self.unified_json["accept"]
        text = self.unified_json.get("body", {}).get("inputText", "")
        maxTokens = self.unified_json.get(
            "body", {}).get(
            "textGenerationConfig", {}).get(
            "maxTokenCount", 50)
        temperature = self.unified_json.get(
            "body", {}).get(
            "textGenerationConfig", {}).get(
            "temperature", 0)
        topP = self.unified_json.get("body", {}).get("textGenerationConfig", {}).get("topP", 1)
        stop_sequences = self.unified_json.get(
            "body", {}).get(
            "textGenerationConfig", {}).get(
            "stopSequences", [])
        count_penalty_scale = self.unified_json.get(
            "body", {}).get(
            "textGenerationConfig", {}).get(
            "countPenalty", {}).get(
            "scale", 0)
        presence_penalty_scale = self.unified_json.get(
            "body", {}).get(
            "textGenerationConfig", {}).get(
            "presencePenalty", {}).get(
            "scale", 0)
        frequency_penalty_scale = self.unified_json.get(
            "body", {}).get(
            "textGenerationConfig", {}).get(
            "frequencyPenalty", {}).get(
            "scale", 0)
        body = f"\"prompt\": \"{text}\", \"maxTokens\": {maxTokens}, \"temperature\": {temperature}, \"topP\": {topP}, \"stop_sequences\": {stop_sequences}, \"countPenalty\": {{\"scale\": {count_penalty_scale}}}, \"presencePenalty\": {{\"scale\": {presence_penalty_scale}}}, \"frequencyPenalty\": {{\"scale\": {frequency_penalty_scale}}}"
        jurassic_json["body"] = "{" + body + "}"
        return jurassic_json

    def get_bedrock_claude_json(self) -> Dict[str, any]:
        claude_json = {}
        claude_json["modelId"] = self.unified_json["modelId"]
        claude_json["contentType"] = self.unified_json["contentType"]
        claude_json["accept"] = self.unified_json["accept"]
        text = self.unified_json.get("body", {}).get("inputText", "")
        max_tokens_to_sample = self.unified_json.get(
            "body", {}).get(
            "textGenerationConfig", {}).get(
            "maxTokenCount", None)
        top_k = self.unified_json.get("body", {}).get("textGenerationConfig", {}).get("topK", 1)
        top_p = self.unified_json.get("body", {}).get("textGenerationConfig", {}).get("topP", 1)
        stop_sequences = self.unified_json.get(
            "body", {}).get(
            "textGenerationConfig", {}).get(
            "stopSequences", [])
        temperature = self.unified_json.get("body", {}).get("textGenerationConfig", {}).get("temperature", 0)
        body = None
        if max_tokens_to_sample:
            body = f"\"prompt\": \"{text}\", \"max_tokens_to_sample\": {max_tokens_to_sample}, \"temperature\": {temperature}, \"top_k\": {top_k}, \"top_p\": {top_p}, \"stop_sequences\": {stop_sequences}"
        else:
            body = f"\"prompt\": \"{text}\", \"temperature\": {temperature}, \"top_k\": {top_k}, \"top_p\": {top_p}, \"stop_sequences\": {stop_sequences}"
        claude_json["body"] = "{" + body + "}"
        return claude_json

    def get_bedrock_stability_ai_json(self) -> Dict[str, any]:
        stability_ai_json = {}
        stability_ai_json["modelId"] = self.unified_json["modelId"]
        stability_ai_json["contentType"] = self.unified_json["contentType"]
        stability_ai_json["accept"] = self.unified_json["accept"]
        body = {}
        body["text_prompts"] = self.unified_json.get("body", {}).get("inputText", [])
        body["cfg_scale"] = self.unified_json.get("body", {}).get("textGenerationConfig", {}).get("cfg_scale", 50)
        body["seed"] = self.unified_json.get("body", {}).get("textGenerationConfig", {}).get("seed", 0)
        body["steps"] = self.unified_json.get("body", {}).get("textGenerationConfig", {}).get("steps", 1)
        stability_ai_json["body"] = json.dumps(body)
        return stability_ai_json
