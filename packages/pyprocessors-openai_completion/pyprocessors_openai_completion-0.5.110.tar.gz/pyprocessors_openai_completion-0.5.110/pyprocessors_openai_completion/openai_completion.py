import inspect
import json
import os
from collections import defaultdict
from enum import Enum
from functools import lru_cache
from logging import Logger
from string import Template
from typing import List, cast, Type, Dict, Tuple, Any

import jinja2
import openai
from log_with_context import add_logging_context
from pydantic import Field, BaseModel
from pymultirole_plugins.v1.processor import ProcessorParameters, ProcessorBase
from pymultirole_plugins.v1.schema import Document, AltText, Annotation, Category

from .retry_limit import api_retry

logger = Logger("pymultirole")


class OpenAIFunction(str, Enum):
    add_annotations = "add_annotations"
    add_categories = "add_categories"


class OpenAIModel(str, Enum):
    gpt_4 = "gpt-4"
    gpt_4_32k = "gpt-4-32k"
    gpt_4_0613 = "gpt-4-0613"
    gpt_3_5_turbo = "gpt-3.5-turbo"
    gpt_3_5_turbo_16k = "gpt-3.5-turbo-16k"
    gpt_3_5_turbo_16k_0613 = "gpt-3.5-turbo-16k-0613"


class TemplateLanguage(str, Enum):
    none = "none"
    string = "string"
    jinja2 = "jinja2"


class OpenAICompletionBaseParameters(ProcessorParameters):
    model_str: str = Field(
        None, extra="internal"
    )
    max_tokens: int = Field(
        256,
        description="""The maximum number of tokens to generate in the completion.
    The token count of your prompt plus max_tokens cannot exceed the model's context length.
    Most models have a context length of 2048 tokens (except for the newest models, which support 4096).""",
    )
    temperature: float = Field(
        1.0,
        description="""What sampling temperature to use, between 0 and 2.
    Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
    We generally recommend altering this or `top_p` but not both.""",
        extra="advanced",
    )
    top_p: int = Field(
        1,
        description="""An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass.
    So 0.1 means only the tokens comprising the top 10% probability mass are considered.
    We generally recommend altering this or `temperature` but not both.""",
        extra="advanced",
    )
    n: int = Field(
        1,
        description="""How many completions to generate for each prompt.
    Note: Because this parameter generates many completions, it can quickly consume your token quota.
    Use carefully and ensure that you have reasonable settings for `max_tokens`.""",
        extra="advanced",
    )
    best_of: int = Field(
        1,
        description="""Generates best_of completions server-side and returns the "best" (the one with the highest log probability per token).
    Results cannot be streamed.
    When used with `n`, `best_of` controls the number of candidate completions and `n` specifies how many to return – `best_of` must be greater than `n`.
    Use carefully and ensure that you have reasonable settings for `max_tokens`.""",
        extra="advanced",
    )
    presence_penalty: float = Field(
        0.0,
        description="""Number between -2.0 and 2.0.
    Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.""",
        extra="advanced",
    )
    frequency_penalty: float = Field(
        0.0,
        description="""Number between -2.0 and 2.0.
    Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.""",
        extra="advanced",
    )
    prompt: str = Field(
        "$text",
        description="""Contains the prompt as a template string, templates can be:
         <li>a simple (python template string)[https://docs.python.org/3/library/string.html#template-strings]<br/>
         where the document elements can be substituted using `$based`-syntax<br/>
         `$text` to be substituted by the document text<br/>
         `$title` to be substituted by the document title
         <li>a more complex (jinja2 template)[https://jinja.palletsprojects.com/en/3.1.x/]
         where the document is injected as `doc` and can be used in jinja2 variables like<br/>
         `{{ doc.text }}` to be substituted by the document text etc...""",
        extra="multiline",
    )
    completion_altText: str = Field(
        None,
        description="""<li>If defined: generates the completion as an alternative text of the input document,
    <li>if not: replace the text of the input document.""",
    )
    function: OpenAIFunction = Field(
        None,
        description="""The function to call. Options currently available:</br>
                        <li>`add_categories` - .
                        <li>`add_annotations` - .
                        """,
        extra="internal,advanced",
    )
    candidate_labels: Dict[str, str] = Field(
        None,
        description="""The list of possible labels to extract.""",
        extra="internal,advanced,key:label,inject",
    )


class OpenAICompletionParameters(OpenAICompletionBaseParameters):
    model: OpenAIModel = Field(
        OpenAIModel.gpt_3_5_turbo,
        description="""The [OpenAI model](https://platform.openai.com/docs/models) used for completion. Options currently available:</br>
                        <li>`gpt_4` - More capable than any GPT-3.5 model, able to do more complex tasks, and optimized for chat. Will be updated with our latest model iteration.
                        <li>`gpt-3.5-turbo` - Most capable GPT-3.5 model and optimized for chat at 1/10th the cost of text-davinci-003. Will be updated with our latest model iteration.
                        <li>`text-davinci-003` - Most capable GPT-3 model. Can do any task the other models can do, often with higher quality, longer output and better instruction-following.
                        <li>`text-curie-001` - Very capable, but faster and lower cost than Davinci.
                        <li>`text-babbage-001` - Capable of straightforward tasks, very fast, and lower cost.
                        <li>`text-ada-001` - Capable of very simple tasks, usually the fastest model in the GPT-3 series, and lowest cost.
                        <li>`davinci-instruct-beta` - older Instruct GPT-3 model.
                        """,
    )


# SUPPORTED_LANGUAGES = "de,en,es,fr,it,nl,pt"
def add_annotations(annotations: List[Dict]):
    """Add name entities with a label and a start and end offset in the original text"""
    return [(a['segment'], Annotation(label=a['label'], text=a.get('text', None), start=a['start'], end=a['end'])) for a
            in annotations]


def add_categories(categories: List[str]):
    """Add name entities with a label and a start and end offset in the original text"""
    return [Category(label=c) for c in categories]


FUNCTIONS = {
    "add_annotations": (add_annotations, {
        "name": "add_annotations",
        "description": "Add name entities with a segment index, a label and a start and end offset in the original text segment",
        "parameters": {
            "type": "object",
            "properties": {
                "annotations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "segment": {
                                "type": "number",
                                "description": 'The text segment index where the named entity is located"',
                            },
                            "label": {
                                "type": "string",
                                "description": 'The label of the named entity, e.g. "Person" or "Location"',
                            },
                            "text": {
                                "type": "string",
                                "description": 'The covering text of the named entity in the original text, e.g. "Joe Biden"',
                            },
                            "start": {"type": "number",
                                      "description": "The start offset of the named entity in the original text, e.g. 0"},
                            "end": {"type": "number",
                                    "description": "The end offset of the named entity in the original text, e.g. 10"},
                        },
                        "required": ["segment", "label", "start", "end"],
                    }
                }
            }
        },
    }),
    "add_categories": (add_categories, {
        "name": "add_categories",
        "description": "Add categories with a label",
        "parameters": {
            "type": "object",
            "properties": {
                "categories": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
    })
}


# noqa: E501
def fix_offsets(doc: Document, indexed_annotations: List[Tuple[int, Annotation]]):
    annotations = []
    seg_annotations = defaultdict(list)
    for i, a in indexed_annotations:
        seg_annotations[i].append(a)
    for i, ann_list in seg_annotations.items():
        ann_list.sort(key=lambda x: x.start, reverse=False)
        seg = doc.sentences[i]
        stext = doc.text[seg.start:seg.end]
        for a in ann_list:
            idx = stext.find(a.text, a.start)
            if idx >= 0:
                a.start = idx + seg.start
                a.end = idx + len(a.text)
                annotations.append(a)
            else:
                logger.warning(f"Can't locate entity {a.text} ({a.start},{a.end}) in text segment: {stext}")
    return annotations


class OpenAICompletionProcessorBase(ProcessorBase):
    __doc__ = """Generate text using [OpenAI Text Completion](https://platform.openai.com/docs/guides/completion) API
    You input some text as a prompt, and the model will generate a text completion that attempts to match whatever context or pattern you gave it."""
    PREFIX: str = ""

    def compute_args(self, params: OpenAICompletionBaseParameters, prompt: str
                     ) -> Dict[str, Any]:
        kwargs = {
            'model': params.model_str,
            'messages': [{"role": "user", "content": prompt}],
            'max_tokens': params.max_tokens,
            'temperature': params.temperature,
            'top_p': params.top_p,
            'n': params.n,
            'frequency_penalty': params.frequency_penalty,
            'presence_penalty': params.presence_penalty,
        }
        OPENAI_DEPLOYMENT_ID = os.getenv(self.PREFIX + "OPENAI_DEPLOYMENT_ID", None)
        if OPENAI_DEPLOYMENT_ID:
            kwargs['deployment_id'] = OPENAI_DEPLOYMENT_ID
        return kwargs

    def compute_result(self, **kwargs):
        response = openai_chat_completion(self.PREFIX, **kwargs)
        contents = []
        for r in response["choices"]:
            if 'content' in r.message and r.message['content']:
                contents.append(r.message['content'])
            elif 'function_call' in r.message and r.message['function_call']:
                function_name = r.message['function_call']["name"]
                function = FUNCTIONS.get(function_name, None)
                if function:
                    fuction_to_call = function[0]
                    function_args = json.loads(r.message['function_call']["arguments"])
                    function_response = fuction_to_call(**function_args)
                    result = (function_name, function_response)
        if contents:
            result = "\n".join(contents)
        return result

    def process(
            self, documents: List[Document], parameters: ProcessorParameters
    ) -> List[Document]:
        # supported_languages = comma_separated_to_list(SUPPORTED_LANGUAGES)

        params: OpenAICompletionBaseParameters = cast(
            OpenAICompletionBaseParameters, parameters
        )
        OPENAI_MODEL = os.getenv(self.PREFIX + "OPENAI_MODEL", None)
        if OPENAI_MODEL:
            params.model_str = OPENAI_MODEL
        try:
            candidate_names = {v: k for k, v in params.candidate_labels.items()} if (params.candidate_labels and len(
                params.candidate_labels) > 0) else {}

            templ, prompt_templ = get_template(params)

            for document in documents:
                with add_logging_context(docid=document.identifier):
                    altTexts = document.altTexts or []
                    if templ == TemplateLanguage.string:
                        flatten_doc = flatten_document(document)
                        prompt = prompt_templ.safe_substitute(flatten_doc)
                    elif templ == TemplateLanguage.jinja2:
                        prompt = prompt_templ.render(doc=document, parameters=params)
                    else:
                        prompt = prompt_templ

                    kwargs = self.compute_args(params, prompt)
                    result = self.compute_result(**kwargs)

                    if result:
                        if isinstance(result, str):
                            if params.completion_altText is not None and len(
                                    params.completion_altText
                            ):
                                altTexts.append(
                                    AltText(name=params.completion_altText, text=result)
                                )
                                document.altTexts = altTexts
                            else:
                                document.text = result
                                document.sentences = []
                                document.annotations = []
                                document.categories = []
                        elif isinstance(result, Tuple):
                            function_name, function_response = result
                            for _, item in function_response:
                                item.labelName = candidate_names.get(item.label)
                            if function_name == "add_annotations":
                                document.annotations = fix_offsets(document, function_response)
                            elif function_name == "add_categories":
                                document.categories = function_response
        except BaseException as err:
            raise err
        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return OpenAICompletionBaseParameters


class OpenAICompletionProcessor(OpenAICompletionProcessorBase):
    __doc__ = """Generate text using [OpenAI Text Completion](https://platform.openai.com/docs/guides/completion) API
    You input some text as a prompt, and the model will generate a text completion that attempts to match whatever context or pattern you gave it."""

    def process(
            self, documents: List[Document], parameters: ProcessorParameters
    ) -> List[Document]:
        params: OpenAICompletionParameters = cast(
            OpenAICompletionParameters, parameters
        )
        params.model_str = params.model.value
        return super().process(documents, params)

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return OpenAICompletionParameters


class AzureOpenAICompletionProcessor(OpenAICompletionProcessorBase):
    __doc__ = """Generate text using [Azure OpenAI Text Completion](https://platform.openai.com/docs/guides/completion) API
    You input some text as a prompt, and the model will generate a text completion that attempts to match whatever context or pattern you gave it."""
    PREFIX = "AZURE_"


class DeepInfraOpenAICompletionProcessor(OpenAICompletionProcessorBase):
    __doc__ = """Generate text using [DeepInfra Text Completion](https://deepinfra.com/docs/advanced/openai_api) API
    You input some text as a prompt, and the model will generate a text completion that attempts to match whatever context or pattern you gave it."""
    PREFIX = "DEEPINFRA_"


def flatten_document(doc: Document):
    y = doc.dict()
    out = {}

    def flatten(x, name=""):

        # If the Nested key-value
        # pair is of dict type
        if type(x) is dict:

            for a in x:
                flatten(x[a], name + a + "_")

        # If the Nested key-value
        # pair is of list type
        elif type(x) is list:

            i = 0

            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def document_language(doc: Document, default: str = None):
    if doc.metadata is not None and "language" in doc.metadata:
        return doc.metadata["language"]
    return default


def get_template(params: OpenAICompletionParameters, default: str = None):
    if "$" in params.prompt:
        prompt_templ = Template(params.prompt)
        return TemplateLanguage.string, prompt_templ
    elif "{{" in params.prompt:
        environment = get_jinja2_env()
        prompt_dedented = inspect.cleandoc(params.prompt)
        prompt_templ = environment.from_string(prompt_dedented)
        return TemplateLanguage.jinja2, prompt_templ
    return TemplateLanguage.none, params.prompt


@api_retry(max_call_number=3500, max_call_number_interval=60)
def openai_chat_completion(prefix, **kwargs):
    set_openai(prefix)
    response = openai.ChatCompletion.create(**kwargs)
    return response


def set_openai(prefix):
    openai.api_key = os.getenv(prefix + "OPENAI_API_KEY")
    OPENAI_API_TYPE = os.getenv(prefix + "OPENAI_API_TYPE", None)
    if OPENAI_API_TYPE is not None:
        openai.type = OPENAI_API_TYPE
    elif prefix == "":
        openai.type = "open_ai"
    OPENAI_API_BASE = os.getenv(prefix + "OPENAI_API_BASE", None)
    if OPENAI_API_BASE is not None:
        openai.api_base = OPENAI_API_BASE
    elif prefix == "":
        openai.api_base = "https://api.openai.com/v1"
    OPENAI_API_VERSION = os.getenv(prefix + "OPENAI_API_VERSION", None)
    if OPENAI_API_VERSION is not None:
        openai.api_version = OPENAI_API_VERSION
    elif prefix == "":
        openai.api_version = None


@lru_cache(maxsize=None)
def get_jinja2_env():
    return jinja2.Environment(extensions=["jinja2.ext.do"])
