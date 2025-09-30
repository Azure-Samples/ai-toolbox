# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from a .env file if present

from dataclasses import dataclass
from typing import Annotated

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureTextEmbedding,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.connectors.in_memory import InMemoryCollection
from semantic_kernel.data.vector import VectorStoreField, vectorstoremodel
from semantic_kernel.functions import KernelArguments

"""
This sample demonstrates a simple RAG application using Semantic Kernel.
It uses mock paragraph data, splits content by paragraphs, and performs RAG queries.
"""

# Mock paragraph data - sample documents about AI topics
MOCK_DOCUMENTS = """
Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals.

Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience. Deep learning, a subset of machine learning, uses neural networks with multiple layers to progressively extract higher-level features from raw input.

Natural language processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language. NLP is used to apply algorithms to identify and extract the natural language rules such that the unstructured language data is converted into a form that computers can understand.

Computer vision is an interdisciplinary scientific field that deals with how computers can gain high-level understanding from digital images or videos. From the perspective of engineering, it seeks to understand and automate tasks that the human visual system can do. Computer vision tasks include methods for acquiring, processing, analyzing and understanding digital images.

Reinforcement learning is an area of machine learning concerned with how intelligent agents ought to take actions in an environment in order to maximize the notion of cumulative reward. Reinforcement learning is one of three basic machine learning paradigms, alongside supervised learning and unsupervised learning.

Neural networks are computing systems inspired by the biological neural networks that constitute animal brains. Such systems learn to perform tasks by considering examples, generally without being programmed with task-specific rules. For instance, in image recognition, they might learn to identify images that contain cats by analyzing example images.

Generative AI refers to artificial intelligence systems capable of generating text, images, or other media in response to prompts. Generative AI models learn the patterns and structure of their input training data and then generate new data that has similar characteristics. Examples include large language models like GPT and image generation models like DALL-E.

The Transformer architecture is a neural network architecture that has become the foundation for many modern AI models. It uses self-attention mechanisms to process input data in parallel, making it highly efficient for tasks like language translation and text generation. Transformers have revolutionized natural language processing since their introduction in 2017.
"""

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
text_embedding = AzureTextEmbedding(service_id="embedding", api_key=api_key, endpoint=endpoint, deployment_name="text-embedding-3-large")


# Define a data model for storing document paragraphs
@vectorstoremodel(collection_name="documents")
@dataclass
class DocumentParagraph:
    id: Annotated[str, VectorStoreField("key")]
    text: Annotated[str, VectorStoreField("data")]
    embedding: Annotated[
        list[float] | str | None,
        VectorStoreField("vector", dimensions=1536, embedding_generator=text_embedding),
    ] = None

    def __post_init__(self):
        if self.embedding is None:
            self.embedding = self.text


def split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs by empty lines."""
    paragraphs = [p.strip() for p in text.strip().split('\n\n') if p.strip()]
    return paragraphs


async def main():
    # Initialize the kernel
    kernel = Kernel()

    # Add Azure OpenAI services
    kernel.add_service(AzureChatCompletion(service_id="chat", api_key=api_key, endpoint=endpoint, deployment_name="gpt-4.1"))
    kernel.add_service(text_embedding)

    # Create an in-memory vector collection
    async with InMemoryCollection(record_type=DocumentParagraph) as collection:
        await collection.ensure_collection_exists()
        
        # Split mock documents into paragraphs
        paragraphs = split_into_paragraphs(MOCK_DOCUMENTS)
        print(f"Loaded {len(paragraphs)} paragraphs into the vector store.\n")
        
        # Create DocumentParagraph objects and upsert into collection
        document_items = [
            DocumentParagraph(id=f"para_{i}", text=para)
            for i, para in enumerate(paragraphs)
        ]
        
        await collection.upsert(document_items)
        print("Documents successfully indexed.\n")
        
        # Create a search function for the collection
        kernel.add_function(
            "memory",
            collection.create_search_function(
                function_name="recall",
                description="Recalls information from the document collection.",
                string_mapper=lambda x: x.record.text,
            ),
        )
        
        # Example 1: Direct template-based RAG query
        print("=" * 60)
        print("Example 1: Template-based RAG Query")
        print("=" * 60)
        result = await kernel.invoke_prompt(
            function_name="rag_query_1",
            plugin_name="RAGPlugin",
            prompt="{{memory.recall 'machine learning'}} Based on the information above, what is machine learning?",
        )
        print(result)
        print()
        
        # Example 2: Let the LLM choose the function with auto function calling
        print("=" * 60)
        print("Example 2: LLM Auto Function Calling")
        print("=" * 60)
        result = await kernel.invoke_prompt(
            function_name="rag_query_2",
            plugin_name="RAGPlugin",
            prompt="What is the Transformer architecture and why is it important?",
            arguments=KernelArguments(
                settings=OpenAIChatPromptExecutionSettings(
                    function_choice_behavior=FunctionChoiceBehavior.Auto(),
                ),
            ),
        )
        print(result)
        print()
        
        # Example 3: Another auto function calling query
        print("=" * 60)
        print("Example 3: Complex Query with RAG")
        print("=" * 60)
        result = await kernel.invoke_prompt(
            function_name="rag_query_3",
            plugin_name="RAGPlugin",
            prompt="Compare and contrast computer vision and natural language processing.",
            arguments=KernelArguments(
                settings=OpenAIChatPromptExecutionSettings(
                    function_choice_behavior=FunctionChoiceBehavior.Auto(),
                ),
            ),
        )
        print(result)
        print()


if __name__ == "__main__":
    asyncio.run(main())
