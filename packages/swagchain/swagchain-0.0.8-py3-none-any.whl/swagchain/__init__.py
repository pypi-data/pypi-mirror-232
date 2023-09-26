from dataclasses import dataclass, field

from .memory import *
from .tools import *


@dataclass(
	frozen=True,
	order=True,
	unsafe_hash=True
)
class Agent(ABC):
	
	
	llm:LanguageModel = field(default=LanguageModel())
	memory:Memory = field(default=Memory())
	namespace:str = field(default="main")
	n:int = field(default=4)
	

	@abstractmethod
	async def chain(self, text:str,prompt:str)->str:
		"""
		Chain a text
		"""
		...

class Swagchain(Agent):
	"""
	Swagchain: A retrieval augmented generation agent
	----------------------

	This class is a wrapper around the OpenAI Chat API and Pinecone Embeddings API
	"""
	llm:LanguageModel = field(default=LanguageModel())
	memory:Memory = field(default=Memory())
	namespace:str = field(default="main")
	n:int = field(default=4)

	async def chain(self, text:str, prompt:str)->str:
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

		knn = await self.memory.search(text=text, namespace=self.namespace, top_k=self.n)
		if len(knn) == 0:
			response = await self.llm.chat(text=text)
		else:
			context = prompt+"\n"+"Suggestions:\n" + "\n".join(knn)
			response = await self.llm.chat(text=text, context=context)
		await self.memory.save(texts=[text, response], namespace=self.namespace)
		return response
	

	async def stream_chain(self, text:str)->AsyncGenerator[str, None]:
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
		full_response = ""
		knn = await self.memory.search(text=text, namespace=self.namespace, top_k=self.n)
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


	async def assist(self,text:str)->str:
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