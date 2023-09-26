# Define a list of OpenAI models, with descriptions, max tokens, and per-token costs
# for prompts and completions for each model
models = [
    {
        "name": "gpt-3.5-turbo-instruct",
        "description": "Same capabilities as the standard gpt-3.5-turbo model but "
        "uses completion rather than chat completion enpoint",
        "max_tokens": "4096",
        "prompt_cost_per_token": "0.0015 / 1000",
        "completion_cost_per_token": "0.002 / 1000",
    },
    {
        "name": "gpt-3.5-turbo",
        "description": "Most capable GPT-3.5 model and optimized for chat at 1/10th "
        "the cost of text-davinci-003. Will be updated with our latest model "
        "iteration.",
        "max_tokens": "4096",
        "prompt_cost_per_token": "0.0015 / 1000",
        "completion_cost_per_token": "0.002 / 1000",
    },
    {
        "name": "gpt-3.5-turbo-16k",
        "description": "Same capabilities as the standard gpt-3.5-turbo model but with "
        "4 times the context.",
        "max_tokens": "16385",
        "prompt_cost_per_token": "0.003 / 1000",
        "completion_cost_per_token": "0.004 / 1000",
    },
    {
        "name": "gpt-4-32k",
        "description": "Same capabilities as the base gpt-4 mode but with 4x the context length. Will be updated with our latest model iteration.",
        "max_tokens": "32768",
        "prompt_cost_per_token": "0.06 / 1000",
        "completion_cost_per_token": "0.12 / 1000",
    },
    {
        "name": "gpt-4",
        "description": "More capable than any GPT-3.5 model, able to do more complex tasks, and optimized for chat. Will be updated with our latest model iteration.",
        "max_tokens": "8192",
        "prompt_cost_per_token": "0.03 / 1000",
        "completion_cost_per_token": "0.06 / 1000",
    },
    {
        "name": "text-ada-001",
        "description": "Capable of very simple tasks, usually the fastest model in the GPT-3 series, and lowest cost.",
        "max_tokens": "2049",
        "prompt_cost_per_token": "0.0004 / 1000",
        "completion_cost_per_token": "0.0004 / 1000",
    },
    {
        "name": "text-babbage-001",
        "description": "Capable of straightforward tasks, very fast, and lower cost.",
        "max_tokens": "2049",
        "prompt_cost_per_token": "0.0005 / 1000",
        "completion_cost_per_token": "0.0005 / 1000",
    },
    {
        "name": "text-curie-001",
        "description": "Very capable, faster and lower cost than Davinci.",
        "max_tokens": "2049",
        "prompt_cost_per_token": "0.002 / 1000",
        "completion_cost_per_token": "0.002 / 1000",
    },
    {
        "name": "text-davinci-001",
        "description": None,
        "max_tokens": "8001",
        "prompt_cost_per_token": "0.02 / 1000",
        "completion_cost_per_token": "0.02 / 1000",
    },
    {
        "name": "text-davinci-002",
        "description": "Similar capabilities to text-davinci-003 but trained with supervised fine-tuning instead of reinforcement learning",
        "max_tokens": "4097",
        "prompt_cost_per_token": "0.02 / 1000",
        "completion_cost_per_token": "0.02 / 1000",
    },
    {
        "name": "text-davinci-003",
        "description": "Most capable GPT-3 model. Can do any task the other models can do, often with higher quality.",
        "max_tokens": "4097",
        "prompt_cost_per_token": "0.02 / 1000",
        "completion_cost_per_token": "0.02 / 1000",
    },
    {
        "name": "gpt-4-0314",
        "description": "Snapshot of gpt-4 from March 14th 2023. Unlike gpt-4, this "
        "model will not receive updates, and will be deprecated 3 "
        "months after a new version is released.",
        "max_tokens": "8192",
        "prompt_cost_per_token": "0.03 / 1000",
        "completion_cost_per_token": "0.06 / 1000",
    },
    {
        "name": "gpt-4-0613",
        "description": "Snapshot of gpt-4 from June 13th 2023 with function calling "
        "data. Unlike gpt-4, this model will not receive updates, and will be "
        "deprecated 3 months after a new version is released.",
        "max_tokens": "8192",
        "prompt_cost_per_token": "0.03 / 1000",
        "completion_cost_per_token": "0.06 / 1000",
    },
    {
        "name": "gpt-4-32k-0314",
        "description": "Snapshot of gpt-4-32 from March 14th 2023. Unlike gpt-4-32k, "
        "this model will not receive updates, and will be deprecated "
        "3 months after a new version is released.",
        "max_tokens": "32768",
        "prompt_cost_per_token": "0.06 / 1000",
        "completion_cost_per_token": "0.12 / 1000",
    },
    {
        "name": "gpt-4-32k-0613",
        "description": "Snapshot of gpt-4-32 from June 13th 2023. Unlike gpt-4-32k, "
        "this model will not receive updates, and will be deprecated 3 months after a "
        "new version is released.",
        "max_tokens": "32768",
        "prompt_cost_per_token": "0.06 / 1000",
        "completion_cost_per_token": "0.12 / 1000",
    },
    {
        "name": "gpt-3.5-turbo-0301",
        "description": "Snapshot of gpt-3.5-turbo from March 1st 2023. Unlike "
        "gpt-3.5-turbo, this model will not receive updates, and will "
        "be deprecated 3 months after a new version is released.",
        "max_tokens": "4096",
        "prompt_cost_per_token": "0.002 / 1000",
        "completion_cost_per_token": "0.002 / 1000",
    },
    {
        "name": "gpt-3.5-turbo-0613",
        "description": "Snapshot of gpt-3.5-turbo from June 13th 2023 with function "
        "calling data. Unlike gpt-3.5-turbo, this model will not receive updates, and "
        "will be deprecated 3 months after a new version is released.",
        "max_tokens": "4096",
        "prompt_cost_per_token": "0.0015 / 1000",
        "completion_cost_per_token": "0.002 / 1000",
    },
    {
        "name": "gpt-3.5-turbo-16k-0613",
        "description": "Snapshot of gpt-3.5-turbo-16k from June 13th 2023. Unlike "
        "gpt-3.5-turbo-16k, this model will not receive updates, and will be "
        "deprecated 3 months after a new version is released.",
        "max_tokens": "16385",
        "prompt_cost_per_token": "0.003 / 1000",
        "completion_cost_per_token": "0.004 / 1000",
    },
    {
        "name": "code-davinci-002",
        "description": "Optimized for code-completion tasks",
        "max_tokens": "8001",
        "prompt_cost_per_token": "0.002 / 1000",
        "completion_cost_per_token": "0.002 / 1000",
    },
    {
        "name": "davinci",
        "description": "Most capable GPT-3 model. Can do any task the other models "
        "can do, often with higher quality.",
        "max_tokens": "2049",
        "prompt_cost_per_token": "0.002 / 1000",
        "completion_cost_per_token": "0.0200 / 1000",
    },
    {
        "name": "curie",
        "description": "Very capable, but faster and lower cost than Davinci.",
        "max_tokens": "2049",
        "prompt_cost_per_token": None,
        "completion_cost_per_token": "0.0020 / 1000",
    },
    {
        "name": "babbage",
        "description": "Capable of straightforward tasks, very fast, and lower cost.",
        "max_tokens": "2049",
        "prompt_cost_per_token": None,
        "completion_cost_per_token": "0.0005 / 1000",
    },
    {
        "name": "ada",
        "description": "Capable of very simple tasks, usually the fastest model in "
        "the GPT-3 series, and lowest cost.",
        "max_tokens": "2049",
        "prompt_cost_per_token": None,
        "completion_cost_per_token": "0.0004 / 1000",
    },
    {
        "name": "code-davinci-001",
        "description": "Earlier version of code-davinci-002",
        "max_tokens": "8001",
        "prompt_cost_per_token": "0.002 / 1000",
        "completion_cost_per_token": "0.002 / 1000",
    },
    {
        "name": "code-cushman-002",
        "description": "Almost as capable as Davinci Codex, but slightly faster. "
        "This speed advantage may make it preferable for real-time "
        "applications.",
        "max_tokens": "2048",
        "prompt_cost_per_token": None,
        "completion_cost_per_token": None,
    },
    {
        "name": "code-cushman-001",
        "description": "Earlier version of code-cushman-002",
        "max_tokens": "2048",
        "prompt_cost_per_token": None,
        "completion_cost_per_token": None,
    },
]
