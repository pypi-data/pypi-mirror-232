import inspect
from abc import ABC, abstractmethod
from typing import TypeAlias

from aiohttp import ClientSession
from langchain.agents.agent_toolkits.openapi import planner
from langchain.agents.agent_toolkits.openapi.spec import reduce_openapi_spec
from langchain.chat_models import ChatOpenAI
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
from langchain.requests import RequestsWrapper

from .aws import *
from .database import *
from .lib.utils import async_io, handle_errors, process_time, retry
from .tools import *

MessagePromptMapping: TypeAlias = Dict[str,Role]

MESSAGE_TO_PROMPT_MAPPING:MessagePromptMapping = {
    "UserMessage": "user",
	"SystemMessage": "system",
	"AIMessage": "assistant"
}


class Agent(BaseModel, ABC):
    llm: LanguageModel
    memory: Memory
    namespace: str
    topK: int

    @abstractmethod
    async def chain(self, text: str, prompt: str) -> str:
        """
        Chain a text
        """
        ...


    @property
    def actions(self) -> List[str]:
        """
        Get the actions of the agent
        """
        return [name for name, _ in inspect.getmembers(self.__class__, inspect.isfunction) if not name.startswith("_")]

class Swagchain(Agent):
    """
    Swagchain: A retrieval augmented generation agent
    ----------------------

    This class is a wrapper around the OpenAI Chat API, Pinecone Emedding and DynamoDB Message History. It streamlines the process of creating a retrieval augmented generation agent.
    """

    llm: LanguageModel = Field(default=LanguageModel())
    memory: Memory = Field(default_factory=Memory)
    namespace: str = Field(default="common")
    topK: int = Field(default=4)


    @property
    def history(self) -> DynamoDBChatMessageHistory:
        return DynamoDBChatMessageHistory(
            table_name=self.__class__.__name__, session_id=self.namespace
        )
    
    @handle_errors
    @async_io
    def get_messages(self) -> List[Message]:
        """
        Get messages from the history
        ----------------------

        Args:

                prompt (str): The prompt to get messages from

        Returns:

                List[Message]: The messages
        """
        messages = self.history.messages
        return [ Message(role=MESSAGE_TO_PROMPT_MAPPING[message.__class__.__name__], content=message.content) for message in messages]  
    
    @handle_errors
    @async_io
    def add_ai_message(self, text: str) -> None:
        """
        Add an AI message to the history
        ----------------------

        Args:

                text (str): The text to add
        """
        self.history.add_ai_message(text)
    
    @handle_errors
    @async_io
    def add_user_message(self, text: str) -> None:
        """
        Add a user message to the history
        ----------------------

        Args:

                text (str): The text to add
        """
        self.history.add_user_message(text)

    @retry()
    @handle_errors
    @process_time
    async def chain(self, text: str, prompt: str="") -> str:
        """
        Retrieval Augmented Generation
        ----------------------

        Args:

                text (str): The text to retrieve from

        Returns:

                str: The generated text

        The agent will find for the KNN of the text into his memory namespace and generate from them
        a response
        """

        knn = await self.memory.search(
            text=text, namespace=self.namespace, top_k=self.topK
        )
        if len(knn) == 0:
            response = await self.llm.chat(text=text)
        else:
            context = prompt + "\n" + "Suggestions:\n" + "\n".join(knn)
            response = await self.llm.chat(text=text, context=context)
        await self.memory.save(texts=[text, response], namespace=self.namespace)
        return response

    
    async def stream_chain(self, text: str) -> AsyncGenerator[str, None]:
        """
        Retrieval Augmented Generation (stream)
        ----------------------

        Args:

                text (str): The text to retrieve from

        Returns:

                AsyncGenerator[str, None]: The generated text

        The agent will find for the KNN of the text into his memory namespace and generate from them
        a response
        """
        await self.add_user_message(text)   
        full_response = ""
        knn = await self.memory.search(
            text=text, namespace=self.namespace, top_k=self.n
        )
        if len(knn) == 0:
            async for response in self.llm.stream(text=text):
                full_response += response
                yield response
        else:
            context = "Suggestions:\n" + "\n".join(knn)
            async for response in self.llm.stream(text=text, context=context):
                full_response += response
                yield response
        await self.memory.save(texts=[text, full_response], namespace=self.namespace)
        await self.add_ai_message(full_response)

    @retry()
    @handle_errors
    @process_time
    async def assist(self, text: str) -> str:
        """
        Assist with GPT-3.5 instructions
        ----------------------

        Args:

                text (str): The text to assist with

        Returns:

                str: The generated text

        The agent will call the GPT-3.5 instruction completion API
        """

        return await self.llm.assist(text=text)
    
    @retry()
    @handle_errors
    @process_time
    async def plugin(self, url:str,text:str)->str:
        """
        OpenAPI Plugin
        ----------------------
        [TODO]] Add description
        """
        async with ClientSession() as session:
            response = await session.get(url+"/openapi.json")
            spec = await response.json()
            reduced_spec = reduce_openapi_spec(spec)
            agent_executor = planner.create_openapi_agent(api_spec=reduced_spec, requests_wrapper=RequestsWrapper(aiosession=session),llm=ChatOpenAI())
            return await agent_executor.arun(text)