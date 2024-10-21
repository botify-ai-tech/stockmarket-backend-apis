from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
import uuid
import google.generativeai as genai
from fastapi import HTTPException
from pinecone import Pinecone, ServerlessSpec


from server.config import settings


class PineconeExecute:
    """
    A class to handle Pinecone operations, including embedding creation, searching, and interaction
    with generative models like OpenAI and Gemini.

    Attributes:
        user_id (str): Unique identifier for the user.
        texts (str or list): The text or texts to embed and store in Pinecone.
        index_name (str): The name of the Pinecone index to use for storing and searching vectors.
    """

    def __init__(self, user_id, texts, index_name="stock-ai") -> None:
        """
        Initialize the PineconeExecute class with user ID, texts to embed, and the Pinecone index name.

        Args:
            user_id (str): The user ID for namespace isolation in Pinecone.
            texts (str or list): The text or texts to embed and store in Pinecone.
            index_name (str): The name of the Pinecone index. Default is 'StockAI'.
        """
        self.user_id = user_id
        self.texts = texts
        self.index_name = index_name

        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        genai.configure(api_key=settings.GEMINI_AI_KEY)
        openai.api_key = settings.OPENAI_API_KEY

        self.create_index_if_not_exists()

    def create_index_if_not_exists(self):
        """Create Pinecone index if it doesn't already exist."""
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        self.index = self.pc.Index(self.index_name)

    def create_embeddings(self):
        """Create embeddings for the given text."""
        try:

            if isinstance(self.texts, list):
                combined_text = " ".join(self.texts)
            else:
                combined_text = self.texts

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=9000, chunk_overlap=200
            )

            splitted_text = text_splitter.split_text(combined_text)

            vectors = []
            for text in splitted_text:
                embedding = self.embed_text_with_retries(text)
                vectors.append(
                    {
                        "id": str(uuid.uuid4()),
                        "values": embedding,
                        "metadata": {"text": text},
                    }
                )

            self.index.upsert(vectors=vectors, namespace=self.user_id)

        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error creating embeddings: {e}"
            )

    def embed_text_with_retries(self, text):
        """
        Generate embeddings for a given text with retry logic.

        Args:
            text (str): The text to embed.

        Returns:
            list: The embedding vector for the text.

        Raises:
            HTTPException: If embedding generation fails.
        """
        try:
            embedding = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document",
                title="Document Embedding",
            )
            return embedding.get("embedding")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate embedding: {str(e)}"
            )

    def search_in_pinecone(self, query_embedding, top_k=5):
        """
        Search the Pinecone index using a query embedding.

        Args:
            query_embedding (list): The embedding vector to search with.
            top_k (int): The number of top results to return.

        Returns:
            list: A list of dictionaries containing search results with 'id', 'score', and 'metadata'.

        Raises:
            HTTPException: If the search operation fails.
        """
        try:
            index = self.pc.Index(self.index_name)
            response = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                namespace=self.user_id,
            )
            return [
                {
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match["metadata"],
                }
                for match in response["matches"]
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error during search in Pinecone: {str(e)}"
            )

    def construct_prompt(self, content, question):
        """
        Construct a prompt to ask a question based on provided text content using OpenAI GPT-4.

        Args:
            content (str): The text content to base the answer on.
            question (str): The question to ask.

        Returns:
            str: The generated response from OpenAI.

        Raises:
            HTTPException: If the OpenAI API call fails.
        """
        # data = {
        #     "model": "gpt-4",
        #     "messages": [
        #         {
        #             "role": "system",
        #             "content": "As an AI bot, your task is to generate a detailed response to the given question based on the provided text...",
        #         },
        #         {
        #             "role": "user",
        #             "content": f"Text:\n{content} \n\nQuestion: {question} \n\nAnswer:",
        #         },
        #     ],
        # }
        prompt = f"""Act as a helpful AI Assistant. You are SMART an AI based chatbot. \
TASK: Generate a well-detailed Answer \
for the Question based on the Text. Make sure to use the given Text to generate the response\
and structure the response. Carefully follow the TASK and \
give the most relevant response accordingly, Bot response should not include \
any generic information. Make sure that the answer is detailed and descriptive. Be sure to generate an Answer \
that is related to the Text only and it is in your own words. Make \
sure to include any relevant URLs present in the Text that are \
relevant and related to the Question. If the Question is not \
related to the Text, respond with 'Not enough information is \
available at this moment'. Do not add any additional \
information or any suggestions or links in the Answer. if someone greets \
you then greet back in formal way. \nQuestion:\n{question} \nContent:\n{content}."""

        try:
            # response = openai.ChatCompletion.create(
            #     model=data["model"],
            #     messages=data["messages"],
            #     temperature=0.5,
            #     max_tokens=500,
            #     frequency_penalty=0,
            #     presence_penalty=0,
            # )
            # return response.choices[0].message["content"]
            model = genai.GenerativeModel("gemini-1.5-flash")
            analysis = model.generate_content(prompt)
            
            return analysis.text

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error during formatting answer: {str(e)}"
            )
