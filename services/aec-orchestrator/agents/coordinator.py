


from langgraph import StateGraph
import base64

def create_coordinator_graph():
    """Create and compile the LangChain coordinator graph for AEC workflows."""

    # Initialize state graph
    graph = StateGraph()

    # Add bidding agent node (RFP parsing and cost estimation)
    def bidding_agent(state):
        from langchain.document_loaders import DirectoryLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.embeddings import OpenAIEmbeddings

        # Load RFP documents
        loader = DirectoryLoader("demo/rfp", glob="*.txt")
        docs = loader.load()

        # Process with LLM for cost estimation
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o")

        prompt = "Analyze this RFP and provide a detailed cost estimate:"
        response = llm.invoke(prompt + "\n\n" + docs[0].page_content)

        return {"cost_estimate": response, "rfp_text": docs[0].page_content}

    graph.add_node("bidding_agent", bidding_agent)

    # Add design agent node (BIM optimization with ifcopenshell)
    def design_agent(state):
        import ifcopenshell
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-4o")

        # Load IFC file and extract elements
        file_path = "demo/sample.ifc"
        ifc_file = ifcopenshell.open(file_path)

        walls = ifc_file.by_type("IfcWall")
        columns = ifc_file.by_type("IfcColumn")

        design_report = f"Found {len(walls)} walls and {len(columns)} columns in the BIM model."

        # Add sustainability analysis
        prompt = "Analyze this IFC data for sustainability improvements:\n\n"
        prompt += f"Walls: {len(walls)}, Columns: {len(columns)}\n"

        response = llm.invoke(prompt)

        return {"design_report": design_report, "sustainability_analysis": response}

    graph.add_node("design_agent", design_agent)

    # Add schedule agent node (Gantt predictions)
    def schedule_agent(state):
        import sympy as sp

        # Simple Gantt chart generation using sympy for task scheduling
        tasks = ["Foundation", "Structure", "Interiors"]
        durations = [30, 45, 60]  # days

        total_time = sum(durations)
        gantt_data = {task: {"duration": dur, "start": start} for task, dur, start in zip(tasks, durations, sp.cumsum([0] + [-1] * (len(durations) - 1)))}
        return {"gantt_chart": gantt_data, "total_duration_days": total_time}

    graph.add_node("schedule_agent", schedule_agent)

    # Add compliance agent node (ISO audits via RAG queries)
    def compliance_agent(state):
        from langchain_community.vectorstores.pgvector import PGVector
        from langchain.embeddings import OpenAIEmbeddings

        # Query vector store for ISO compliance documents
        embeddings = OpenAIEmbeddings()
        retriever = PGVector(embedding_function=embeddings).as_retriever()

        query = "ISO 19650 compliance requirements"
        docs = retriever.retrieve(query)

        return {"compliance_check": docs}

    graph.add_node("compliance_agent", compliance_agent)

    # Add maintenance agent node (sensor analysis)
    def maintenance_agent(state):
        import numpy as np

        # Mock sensor data analysis
        sensors = ["temperature", "humidity", "structural_integrity"]
        readings = [np.random.normal(20, 5), np.random.normal(40, 10), np.random.normal(95, 3)]

        maintenance_report = {
            "sensors": sensors,
            "readings": readings,
            "alerts": ["Structural integrity below threshold"] if readings[2] < 97 else []
        }

        return maintenance_report

    graph.add_node("maintenance_agent", maintenance_agent)

    # Define the workflow edges
    graph.add_edge("bidding_agent", "design_agent")
    graph.add_edge("design_agent", "schedule_agent")
    graph.add_edge("schedule_agent", "compliance_agent")
    graph.add_edge("compliance_agent", "maintenance_agent")

    return graph.compile()

# Example usage
if __name__ == "__main__":
    coordinator_graph = create_coordinator_graph()
    print("Coordinator graph created successfully!")
