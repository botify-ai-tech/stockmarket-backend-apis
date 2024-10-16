import logging
from server.utils.pinecone import PineconeExecute


def background_pinecone_task(doc, user_id):
    all_text = ""
    # Loop through each page in the PDF and extract text
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Load the page by its index
        text = page.get_text("text")  # Extract text from the page
        all_text += text  # Append the text to the all_text string

    if all_text:
        pinecone_executor = PineconeExecute(user_id=user_id, texts=[all_text])
        pinecone_executor.create_embeddings()

    logging.info(f"Successfully created embeddings for user {user_id}")
