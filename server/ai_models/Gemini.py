import os
from dotenv import load_dotenv
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import BaseOutputParser
from langchain.schema import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from ai_models.data.training_data import (
    taskClassification_dataset,
    assistant_dataset,
    findName_dataset,
)

load_dotenv(dotenv_path="server/configs/.env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class MyOutputParser(BaseOutputParser):
    def parse(self, text: str) -> str:
        return text


# Since Google AI lacks support for SystemMessage, we are
# transforming it into HumanMessage instead.
def filterDataset(dataset):
    filtered_dataset = []
    for message in dataset:
        if isinstance(message, SystemMessage):
            message = HumanMessage(content=message.content)
        filtered_dataset.append(message)
    return filtered_dataset


llm = ChatGoogleGenerativeAI(model="gemini-pro", api_key=GOOGLE_API_KEY)

taskClassify_prompt = ChatPromptTemplate.from_messages(
    filterDataset(taskClassification_dataset)
)
taskClassificationChain = taskClassify_prompt | llm | MyOutputParser()

assistantPrompt = ChatPromptTemplate.from_messages(assistant_dataset)
assistantChain = (
    assistantPrompt | llm | MyOutputParser(filterDataset(assistant_dataset))
)

findNamePrompt = ChatPromptTemplate.from_messages(filterDataset(findName_dataset))
findNameChain = findNamePrompt | llm | MyOutputParser()

print("chain created")


# For classifying the user query into specific category
def classifyTask(query: str):
    response = taskClassificationChain.invoke({"text": query})
    return response


# For normal conversation and email writing
def generalAssistant(user_input):
    response = assistantChain.invoke({"text": user_input})
    return response


# To facilitate the Google contact automation process, it is
# necessary to extract and return any names included in the query.
def findName(user_input):
    response = findNameChain.invoke({"text": user_input})
    return response
