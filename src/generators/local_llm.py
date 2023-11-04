from typing import Callable, Iterable, List

from langchain.schema import Document
from llama_cpp import ChatCompletionMessage, Completion, Llama
from formatters import MarxFormatter


class LLM_Model():
    def __init__(self, 
                 model_path:str, 
                 n_gpu_layers:int=0, 
                 n_batch:int=512, 
                 temperature:float=0.25, 
                 max_tokens:int=2000, 
                 n_ctx:int=2048,
                 embedding: bool = False,
                 verbose:bool=True):
        
        self.model_path = model_path

        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers, # TODO: make it work with GPU
            #n_batch=n_batch,
            temperature=temperature,
            max_tokens=max_tokens,
            n_ctx=n_ctx,
            verbose=verbose,
            embedding=embedding,
            stream = False
        ) # type: ignore
    
    system_message = """You are a helpful assistant. You are helping a user with a question.
        Answer in a concise way in a few sentences.
        Use the following context to answer the user's question.
        If the given given context does not have the information to answer the question, you should answer "I don't know" and don't say anything else."""

    def RAG_QA_chain(self, retrieved_docs: List[Document], query: str) -> str:
        assert self.llm is not None, "LLM is not initialized"

        context: ChatCompletionMessage = ChatCompletionMessage(
            role="system", 
            content=self.system_message+"\n"+ \
                "\n".join("- " + doc.page_content for doc in retrieved_docs)
        )
        # We ignore the type because it is entirely dependent on streaming

        prompt = MarxFormatter().call([context, ChatCompletionMessage(role="user", content=query)])
        result: Completion = self.llm.create_completion(prompt=prompt.prompt, stop=prompt.stop, temperature=0.1) # type: ignore

        # return generated text
        return result["choices"][0]["text"]