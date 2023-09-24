from enum import Enum
import json
from typing import Annotated, Dict, List, Optional, Tuple, Union

import openai
from pydantic import BaseModel, Extra, Field, confloat, conint, constr
import rich
import typer


app = typer.Typer(add_completion=False)


@app.callback()
def callback():
    """
    shellm = shell + LLM
    """


class CompletionModelEnum(Enum):
    babbage_002 = "babbage-002"
    davinci_002 = "davinci-002"
    gpt_3_5_turbo_instruct = "gpt-3.5-turbo-instruct"
    gpt_3_5_turbo_instruct_0914 = "gpt-3.5-turbo-instruct-0914",
    text_davinci_003 = "text-davinci-003"
    text_davinci_002 = "text-davinci-002"
    text_davinci_001 = "text-davinci-001"
    code_davinci_002 = "code-davinci-002"
    text_curie_001 = "text-curie-001"
    text_babbage_001 = "text-babbage-001"
    text_ada_001 = "text-ada-001"


class ChatModelEnum(Enum):
    gpt_4 = "gpt-4"
    gpt_4_0314 = "gpt-4-0314"
    gpt_4_0613 = "gpt-4-0613"
    gpt_4_32k = "gpt-4-32k"
    gpt_4_32k_0314 = "gpt-4-32k-0314"
    gpt_4_32k_0613 = "gpt-4-32k-0613"
    gpt_3_5_turbo = "gpt-3.5-turbo"
    gpt_3_5_turbo_16k = "gpt-3.5-turbo-16k"
    gpt_3_5_turbo_0301 = "gpt-3.5-turbo-0301"
    gpt_3_5_turbo_0613 = "gpt-3.5-turbo-0613"
    gpt_3_5_turbo_16k_0613 = "gpt-3.5-turbo-16k-0613"


class BaseCreateArgs(BaseModel):
    model: Union[str, CompletionModelEnum] = Field(
        ...,
        description="ID of the model to use. You can use the list models API (https://platform.openai.com/docs/api-reference/models/list) to see all of your available models, or see our model overview (https://platform.openai.com/docs/models/overview) for descriptions of them.",
    )
    max_tokens: Optional[conint(ge=0)] = Field(
        16,
        description="The maximum number of tokens (https://platform.openai.com/tokenizer) to generate in the completion. The token count of your prompt plus `max_tokens` cannot exceed the model's context length. Example Python code for counting tokens (https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb).",
        example=16,
    )
    temperature: Optional[confloat(ge=0.0, le=2.0)] = Field(
        1,
        description="What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or `top_p` but not both.",
        example=1,
    )
    top_p: Optional[confloat(ge=0.0, le=1.0)] = Field(
        1,
        description="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. We generally recommend altering this or `temperature` but not both.",
        example=1,
    )
    n: Optional[conint(ge=1, le=128)] = Field(
        1,
        description="How many completions to generate for each prompt. **Note:** Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for `max_tokens` and `stop`.",
        example=1,
    )
    stream: Optional[bool] = Field(
        False,
        description="Whether to stream back partial progress. If set, tokens will be sent as data-only server-sent events (https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format) as they become available, with the stream terminated by a `data: [DONE]` message. Example Python code (https://github.com/openai/openai-cookbook/blob/main/examples/How_to_stream_completions.ipynb).",
    )
    stop: Optional[Union[str, List[str]]] = Field(
        None,
        description="Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.",
    )
    presence_penalty: Optional[confloat(ge=-2.0, le=2.0)] = Field(
        0,
        description="Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. See more information about frequency and presence penalties (https://platform.openai.com/docs/guides/gpt/parameter-details)",
    )
    frequency_penalty: Optional[confloat(ge=-2.0, le=2.0)] = Field(
        0,
        description="Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. See more information about frequency and presence penalties (https://platform.openai.com/docs/guides/gpt/parameter-details)",
    )
    logit_bias: Optional[Dict[str, int]] = Field(
        None,
        description="Modify the likelihood of specified tokens appearing in the completion. Accepts a json object that maps tokens (specified by their token ID in the GPT tokenizer) to an associated bias value from -100 to 100. You can use this tokenizer tool(https://platform.openai.com/tokenizer?view=bpe) (which works for both GPT-2 and GPT-3) to convert text to token IDs. Mathematically, the bias is added to the logits generated by the model prior to sampling. The exact effect will vary per model, but values between -1 and 1 should decrease or increase likelihood of selection; values like -100 or 100 should result in a ban or exclusive selection of the relevant token. As an example, you can pass `{'50256': -100}` to prevent the <|endoftext|> token from being generated.",
    )
    user: Optional[str] = Field(
        None,
        description="A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. Learn more (https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).",
        example="user-1234",
    )


class CompletionCreateArgs(BaseCreateArgs):
    prompt: Union[str, List[str], List[int], List[List[int]]] = Field(
        ...,
        description="The prompt(s) to generate completions for, encoded as a string, array of strings, array of tokens, or array of token arrays. Note that <|endoftext|> is the document separator that the model sees during training, so if a prompt is not specified the model will generate as if from the beginning of a new document.",
    )
    suffix: Optional[str] = Field(
        None,
        description="The suffix that comes after a completion of inserted text.",
        example="test.",
    )
    logprobs: Optional[conint(ge=0, le=5)] = Field(
        None,
        description="Include the log probabilities on the `logprobs` most likely tokens, as well the chosen tokens. For example, if `logprobs` is 5, the API will return a list of the 5 most likely tokens. The API will always return the `logprob` of the sampled token, so there may be up to `logprobs+1` elements in the response.\n\nThe maximum value for `logprobs` is 5.\n",
    )
    echo: Optional[bool] = Field(
        False, description="Echo back the prompt in addition to the completion\n"
    )
    best_of: Optional[conint(ge=0, le=20)] = Field(
        1,
        description="Generates `best_of` completions server-side and returns the 'best' (the one with the highest log probability per token). Results cannot be streamed.\n\nWhen used with `n`, `best_of` controls the number of candidate completions and `n` specifies how many to return – `best_of` must be greater than `n`.\n\n**Note:** Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for `max_tokens` and `stop`.\n",
    )

@app.command()
def completion(
    prompt: Annotated[
        str,
        typer.Option(help=CompletionCreateArgs.model_fields["prompt"].description),
    ],
    model: Annotated[
        str,
        typer.Option(help=CompletionCreateArgs.model_fields["model"].description),
    ] = "gpt-3.5-turbo-instruct",
    suffix: Annotated[
        str,
        typer.Option(help=CompletionCreateArgs.model_fields["suffix"].description),
    ] = CompletionCreateArgs.model_fields["suffix"].default,
    max_tokens: Annotated[
        int,
        typer.Option(help=CompletionCreateArgs.model_fields["max_tokens"].description),
    ] = CompletionCreateArgs.model_fields["max_tokens"].default,
    temperature: Annotated[
        float,
        typer.Option(help=CompletionCreateArgs.model_fields["temperature"].description),
    ] = CompletionCreateArgs.model_fields["temperature"].default,
    top_p: Annotated[
        float,
        typer.Option(help=CompletionCreateArgs.model_fields["top_p"].description),
    ] = CompletionCreateArgs.model_fields["top_p"].default,
    n: Annotated[
        int,
        typer.Option(help=CompletionCreateArgs.model_fields["n"].description),
    ] = CompletionCreateArgs.model_fields["n"].default,
    stream: Annotated[
        bool,
        typer.Option(help=CompletionCreateArgs.model_fields["stream"].description),
    ] = CompletionCreateArgs.model_fields["stream"].default,
    logprobs: Annotated[
        int,
        typer.Option(help=CompletionCreateArgs.model_fields["logprobs"].description),
    ] = CompletionCreateArgs.model_fields["logprobs"].default,
    echo: Annotated[
        bool,
        typer.Option(help=CompletionCreateArgs.model_fields["echo"].description),
    ] = CompletionCreateArgs.model_fields["echo"].default,
    stop: Annotated[
        List[str],
        typer.Option(help=CompletionCreateArgs.model_fields["stop"].description),
    ] = CompletionCreateArgs.model_fields["stop"].default,
    presence_penalty: Annotated[
        float,
        typer.Option(help=CompletionCreateArgs.model_fields["presence_penalty"].description),
    ] = CompletionCreateArgs.model_fields["presence_penalty"].default,
    frequency_penalty: Annotated[
        float,
        typer.Option(help=CompletionCreateArgs.model_fields["frequency_penalty"].description),
    ] = CompletionCreateArgs.model_fields["frequency_penalty"].default,
    best_of: Annotated[
        int,
        typer.Option(help=CompletionCreateArgs.model_fields["best_of"].description),
    ] = CompletionCreateArgs.model_fields["best_of"].default,
#    logit_bias: Annotated[
#        List[Tuple[int, int]],
#        typer.Option(help=CompletionCreateArgs.model_fields["logit_bias"].description),
#    ] = CompletionCreateArgs.model_fields["logit_bias"].default,
    user: Annotated[
        str,
        typer.Option(help=CompletionCreateArgs.model_fields["user"].description),
    ] = CompletionCreateArgs.model_fields["user"].default,
):
    """
    A completion
    https://platform.openai.com/docs/api-reference/completions
    """

    args = CompletionCreateArgs(
        prompt=prompt,
        model=model,
        suffix=suffix,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        n=n,
        stream=stream,
        logprobs=logprobs,
        echo=echo,
        stop=stop or None,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        best_of=best_of,
        logit_bias={},
        user=user or "",
    )
#    rich.print(args)

    completion = openai.Completion.create(**args.model_dump())
    if args.stream:
        for piece in completion:
            typer.echo(piece.choices[0]["text"], nl=False)
    else:
        typer.echo(completion.choices[0]["text"])



class Role(Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    function = "function"


class FunctionCall(BaseModel):
    name: str = Field(..., description="The name of the function to call.")
    arguments: str = Field(
        ...,
        description="The arguments to call the function with, as generated by the model in JSON format. Note that the model does not always generate valid JSON, and may hallucinate parameters not defined by your function schema. Validate the arguments in your code before calling your function.",
    )


class ChatCompletionRequestMessage(BaseModel):
    role: Role = Field(
        ...,
        description="The role of the messages author. One of `system`, `user`, `assistant`, or `function`.",
    )
    content: str = Field(
        ...,
        description="The contents of the message. `content` is required for all messages, and may be null for assistant messages with function calls.",
    )
    name: Optional[str] = Field(
        None,
        description="The name of the author of this message. `name` is required if role is `function`, and it should be the name of the function whose response is in the `content`. May contain a-z, A-Z, 0-9, and underscores, with a maximum length of 64 characters.",
    )
    function_call: Optional[FunctionCall] = Field(
        None,
        description="The name and arguments of a function that should be called, as generated by the model.",
    )


class ChatCompletionFunctionParameters(BaseModel):
    pass

    class Config:
        extra = Extra.allow


class ChatCompletionFunctions(BaseModel):
    name: str = Field(
        ...,
        description="The name of the function to be called. Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length of 64.",
    )
    description: Optional[str] = Field(
        None,
        description="A description of what the function does, used by the model to choose when and how to call the function.",
    )
    parameters: ChatCompletionFunctionParameters


class FunctionCallEnum(Enum):
    none = "none"
    auto = "auto"


class ChatCompletionFunctionCallOption(BaseModel):
    name: str = Field(..., description='The name of the function to call.')


class ChatCreateArgs(BaseCreateArgs):
    messages: List[ChatCompletionRequestMessage] = Field(
        ...,
        description="A list of messages comprising the conversation so far. Example Python code (https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb).",
        min_items=1,
    )
    functions: Optional[List[ChatCompletionFunctions]] = Field(
        None,
        description="A list of functions the model may generate JSON inputs for.",
        max_items=128,
        min_items=1,
    )
    function_call: Optional[
        Union[FunctionCallEnum, ChatCompletionFunctionCallOption]
    ] = Field(
        None,
        description="Controls how the model responds to function calls. `none` means the model does not call a function, and responds to the end-user. `auto` means the model can pick between an end-user or calling a function.  Specifying a particular function via `{'name': 'my_function'}` forces the model to call that function. `none` is the default when no functions are present. `auto` is the default if functions are present.",
    )



@app.command()
def chat(
    user_message: Annotated[
        str,
        typer.Option(help="The content of the user message"),
    ],
    model: Annotated[
        str,
        typer.Option(help=CompletionCreateArgs.model_fields["model"].description),
    ] = "gpt-3.5-turbo",
    max_tokens: Annotated[
        int,
        typer.Option(help=CompletionCreateArgs.model_fields["max_tokens"].description),
    ] = CompletionCreateArgs.model_fields["max_tokens"].default,
    temperature: Annotated[
        float,
        typer.Option(help=CompletionCreateArgs.model_fields["temperature"].description),
    ] = CompletionCreateArgs.model_fields["temperature"].default,
    top_p: Annotated[
        float,
        typer.Option(help=CompletionCreateArgs.model_fields["top_p"].description),
    ] = CompletionCreateArgs.model_fields["top_p"].default,
    n: Annotated[
        int,
        typer.Option(help=CompletionCreateArgs.model_fields["n"].description),
    ] = CompletionCreateArgs.model_fields["n"].default,
    stream: Annotated[
        bool,
        typer.Option(help=CompletionCreateArgs.model_fields["stream"].description),
    ] = CompletionCreateArgs.model_fields["stream"].default,
    stop: Annotated[
        List[str],
        typer.Option(help=CompletionCreateArgs.model_fields["stop"].description),
    ] = CompletionCreateArgs.model_fields["stop"].default,
    presence_penalty: Annotated[
        float,
        typer.Option(help=CompletionCreateArgs.model_fields["presence_penalty"].description),
    ] = CompletionCreateArgs.model_fields["presence_penalty"].default,
    frequency_penalty: Annotated[
        float,
        typer.Option(help=CompletionCreateArgs.model_fields["frequency_penalty"].description),
    ] = CompletionCreateArgs.model_fields["frequency_penalty"].default,
#    logit_bias: Annotated[
#        List[Tuple[int, int]],
#        typer.Option(help=CompletionCreateArgs.model_fields["logit_bias"].description),
#    ] = CompletionCreateArgs.model_fields["logit_bias"].default,
    user: Annotated[
        str,
        typer.Option(help=CompletionCreateArgs.model_fields["user"].description),
    ] = CompletionCreateArgs.model_fields["user"].default,
):
    """
    A chat completion
    https://platform.openai.com/docs/api-reference/chat
    """
    args = ChatCreateArgs(
        messages=[
            ChatCompletionRequestMessage(
                role = Role.user,
                content = user_message,
            ),
        ],
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        n=n,
        stream=stream,
        stop=stop or None,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        logit_bias={},
        user=user or "",
    )
#    rich.print(args)
#    rich.print(args.model_dump_json(exclude_none=True))

    completion = openai.ChatCompletion.create(**json.loads(args.model_dump_json(exclude_none=True)))

    if stream:
        for piece in completion:
            typer.echo(piece.choices[0]["delta"].get("content", "\n"), nl=False)
    else:
        typer.echo(completion.choices[0].message.content)






