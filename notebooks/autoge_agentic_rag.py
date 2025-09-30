"""
Simple Agentic RAG Demo with Two Data Sources
This demo shows an agent that intelligently decides which data source to query
based on the user's question using AutoGen's memory capabilities.
"""

import asyncio
import os
from typing import List

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_core.memory import ListMemory, MemoryContent, MemoryMimeType
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient


# Simulated Data Source 1: Product Catalog
PRODUCT_CATALOG = {
    "laptop": {
        "name": "UltraBook Pro",
        "price": "$1299",
        "specs": "16GB RAM, 512GB SSD, Intel i7",
        "stock": 15
    },
    "phone": {
        "name": "SmartPhone X",
        "price": "$899",
        "specs": "128GB Storage, 5G, OLED Display",
        "stock": 42
    },
    "tablet": {
        "name": "TabletMax",
        "price": "$599",
        "specs": "10-inch Display, 64GB Storage",
        "stock": 8
    }
}

# Simulated Data Source 2: Customer Support KB
SUPPORT_KB = {
    "shipping": {
        "topic": "Shipping Information",
        "info": "Standard shipping takes 3-5 business days. Express shipping is 1-2 days.",
        "cost": "Standard: $5.99, Express: $15.99"
    },
    "returns": {
        "topic": "Return Policy",
        "info": "Returns accepted within 30 days of purchase with original packaging.",
        "process": "Contact support with order number to initiate return."
    },
    "warranty": {
        "topic": "Warranty Coverage",
        "info": "All products come with 1-year manufacturer warranty.",
        "details": "Extended warranty available for purchase at checkout."
    }
}


async def search_product_catalog(query: str) -> str:
    """
    Search the product catalog for product information.
    
    Args:
        query: Product search query (e.g., 'laptop', 'phone', 'tablet')
    
    Returns:
        Product information as a formatted string
    """
    query_lower = query.lower()
    
    # Simple keyword matching
    for product_key, product_data in PRODUCT_CATALOG.items():
        if product_key in query_lower or product_data["name"].lower() in query_lower:
            return (
                f"Product: {product_data['name']}\n"
                f"Price: {product_data['price']}\n"
                f"Specifications: {product_data['specs']}\n"
                f"In Stock: {product_data['stock']} units"
            )
    
    # Return all products if no specific match
    results = []
    for product_data in PRODUCT_CATALOG.values():
        results.append(f"- {product_data['name']}: {product_data['price']}")
    
    return "Available Products:\n" + "\n".join(results)


async def search_support_kb(query: str) -> str:
    """
    Search the customer support knowledge base.
    
    Args:
        query: Support query (e.g., 'shipping', 'returns', 'warranty')
    
    Returns:
        Support information as a formatted string
    """
    query_lower = query.lower()
    
    # Simple keyword matching
    for kb_key, kb_data in SUPPORT_KB.items():
        if kb_key in query_lower or any(word in query_lower for word in kb_data["topic"].lower().split()):
            result = f"Topic: {kb_data['topic']}\n"
            result += f"Information: {kb_data['info']}\n"
            
            # Add optional fields if they exist
            if "cost" in kb_data:
                result += f"Cost: {kb_data['cost']}\n"
            if "process" in kb_data:
                result += f"Process: {kb_data['process']}\n"
            if "details" in kb_data:
                result += f"Details: {kb_data['details']}\n"
            
            return result
    
    # Return all topics if no specific match
    topics = [f"- {kb_data['topic']}" for kb_data in SUPPORT_KB.values()]
    return "Available Support Topics:\n" + "\n".join(topics)


async def main():
    """
    Main function to run the agentic RAG demo.
    """
    print("=" * 60)
    print("Agentic RAG Demo - Two Data Sources")
    print("=" * 60)
    print()
    
    # Initialize memory with context about the data sources
    agent_memory = ListMemory()
    
    # Add information about available data sources to memory
    await agent_memory.add(
        MemoryContent(
            content=(
                "You have access to two data sources:\n"
                "1. Product Catalog (search_product_catalog): Use this for product inquiries, "
                "pricing, specifications, and inventory questions.\n"
                "2. Support Knowledge Base (search_support_kb): Use this for customer support "
                "questions about shipping, returns, warranty, and policies."
            ),
            mime_type=MemoryMimeType.TEXT
        )
    )
    
    await agent_memory.add(
        MemoryContent(
            content=(
                "Decision Guidelines:\n"
                "- For product-related questions (price, specs, stock): use search_product_catalog\n"
                "- For policy/support questions (shipping, returns, warranty): use search_support_kb\n"
                "- You can call both tools if the question requires information from both sources"
            ),
            mime_type=MemoryMimeType.TEXT
        )
    )
    
    # Create the model client
    model_client = AzureOpenAIChatCompletionClient(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    )
    
    # Create the assistant agent with both tools and memory
    assistant = AssistantAgent(
        name="rag_assistant",
        model_client=model_client,
        tools=[search_product_catalog, search_support_kb],
        memory=[agent_memory],
        system_message=(
            "You are a helpful shopping assistant. You have access to a product catalog "
            "and a customer support knowledge base. Intelligently decide which data source(s) "
            "to query based on the user's question. Provide clear and helpful responses."
        )
    )
    
    # Test queries that require different data sources
    test_queries = [
        "What laptops do you have available?",
        "What's your return policy?",
        "How much does the phone cost and how long does shipping take?"
    ]
    
    print("Running test queries...\n")
    
    for query in test_queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print('=' * 60)
        
        # Run the agent with the query
        stream = assistant.run_stream(task=query)
        await Console(stream)
        
        print()
    
    # Close the model client
    await model_client.close()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
