import openai
from securitygpt.schema import schema_base_prompt
from securitygpt.schema.schema_base_prompt import SystemMessage, UserMessage, PromptContext, ChatCompletionMessage, MessageRole, Message
from securitygpt.schema.schema_stock_rec import StockSentimentJson
from securitygpt.schema.schema_base_openai import OpenAISchema
from securitygpt.prompts.prompts_stock_rec import PromptStockrecRole, PromptStockrecTask, PromptStockrecOutput, PromptStockrecExample, PrompStockrectTips, PromptStockrecExample, PromptStockrecReflect, PromptStockrecInputString


def plan_run(system_message, user_message, schemas):

    task = ChatCompletionMessage (
                        #model = "gpt-3.5-turbo-0613",
                        model = "gpt-3.5-turbo-16k",
                        max_tokens = 1000,
                        temperature = 0.1,
                        functions = [StockSentimentJson.openai_schema],
                        #functions = [GoogleLinksSchema.openai_schema],
                        messages=[system_message,user_message]
                    )

    completion = openai.ChatCompletion.create(**task.kwargs)
    import json
    #GoogleLinksSchema.from_response(completion)
    function_name = completion.choices[0].message.function_call.name
    args = json.loads (completion.choices[0].message.function_call.arguments)
    print (json.loads (completion.choices[0].message.function_call.arguments))

    print (completion.choices[0].message.function_call)

    #func(args).run(args)

existing_research = "NA"


#prompt_string = PromptResearchObjective().return_string.format (research_objective="legacy of oppenheimer") + PromptMarkdownRole().return_string + PromptMarkdownTask().return_string + PromptMarkdownOutput().return_string + PromptMarkdownExample().return_string + PromptMarkdownInputString().return_string.format(url="www.google.com",url_text=url_text) + PromptMarkdownExisting().return_string.format(current_knowledge = existing_research)

def plan_run_no_functions():
    task = ChatCompletionMessageNoFunctions (
                    model = "gpt-3.5-turbo-16k",
                    max_tokens = 1000,
                    temperature = 0.1,
                    messages=[system_message,user_message]
                )

    print (task.kwargs)
    completion = openai.ChatCompletion.create(**task.kwargs)
