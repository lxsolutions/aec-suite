


from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

def process_rfp(rfp_path: str):
    """Process RFP documents and generate cost estimates."""

    # Load RFP documents
    loader = DirectoryLoader(rfp_path, glob="*.txt")
    docs = loader.load()

    # Split into manageable chunks if needed
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    split_docs = text_splitter.split_documents(docs)

    # Initialize LLM for cost estimation
    llm = ChatOpenAI(model="gpt-4o")

    results = []
    for doc in split_docs:
        prompt = "Analyze this RFP section and provide a detailed cost estimate:"
        response = llm.invoke(prompt + "\n\n" + doc.page_content)
        results.append(response)

    return {
        "cost_estimates": results,
        "total_rfp_text": "\n".join([doc.page_content for doc in docs])
    }

if __name__ == "__main__":
    # Example usage
    result = process_rfp("demo/rfp")
    print(f"Processed RFP with {len(result['cost_estimates'])} estimates")

