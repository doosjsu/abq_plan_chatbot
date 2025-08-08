
# Streamlit - Web application framework for creating interactive data apps
import streamlit as st

# LangChain - Framework for building applications with LLMs
from langchain_openai import ChatOpenAI  # OpenAI's chat model interface
from langchain.chains import RetrievalQA  # Chain for question-answering over documents
from langchain_community.vectorstores import Chroma  # Vector database for storing document embeddings
from langchain.text_splitter import CharacterTextSplitter  # Splits text into chunks for processing
from langchain_openai import OpenAIEmbeddings  # OpenAI's text embedding model
from langchain.memory import ConversationBufferMemory  # Stores conversation history
from langchain.chains import ConversationalRetrievalChain  # Chain for conversational QA with memory

# Standard Python libraries
import os  # Operating system interface for environment variables
from dotenv import load_dotenv  # Loads environment variables from .env file
import json  # JSON encoder/decoder for saving conversation history
from datetime import datetime  # Date and time utilities for timestamping

# Web scraping and HTTP requests
from bs4 import BeautifulSoup  # HTML/XML parser for web scraping
import requests  # HTTP library for making web requests

# PDF processing
import PyPDF2  # PDF text extraction
import io  # Input/output operations for file handling

# Load environment variables from .env file
load_dotenv()

def scrape_cabq_pages(urls):
    """
    Scrapes multiple CABQ Planning Department webpages and extracts text content.
    
    Args:
        urls (list): List of URLs to scrape
        
    Returns:
        str: Combined extracted text content from all webpages
    """
    combined_text = ""
    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            combined_text += f"\n\n--- Content from {url} ---\n\n"
            combined_text += page_text
        except Exception as e:
            st.warning(f"Could not scrape {url}: {str(e)}")
    
    return combined_text

def extract_pdf_text(pdf_file):
    """
    Extracts text content from a PDF file.
    
    Args:
        pdf_file: PDF file object (from st.file_uploader or similar)
        
    Returns:
        str: Extracted text content from the PDF
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += f"\n\n--- Page {page_num + 1} ---\n\n"
            text_content += page.extract_text()
        
        return text_content
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return ""

def get_service_links():
    """
    Returns a dictionary of service-specific links for CABQ Planning Department.
    
    Returns:
        dict: Dictionary mapping service keywords to their direct links
    """
    return {
        "permit": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "license": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "application": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "account": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "create account": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "new account": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "register": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "login": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "sign in": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "status": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "check status": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "application status": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "permit status": "https://cityofalbuquerquenmtrain-energovweb.tylerhost.net/apps/selfservice#/home",
        "contact": "https://www.cabq.gov/planning/contact",
        "location": "https://www.cabq.gov/planning/contact",
        "located": "https://www.cabq.gov/planning/contact",
        "address": "https://www.cabq.gov/planning/contact",
        "where": "https://www.cabq.gov/planning/contact",
        "phone": "https://www.cabq.gov/planning/contact",
        "bill": "https://www.cabq.gov/311/pay-a-bill",
        "payment": "https://www.cabq.gov/311/pay-a-bill",
        "pay": "https://www.cabq.gov/311/pay-a-bill",
        "planning": "https://www.cabq.gov/planning",
        "division": "https://www.cabq.gov/planning/contact",
        "divisions": "https://www.cabq.gov/planning/contact",
        "building": "https://www.cabq.gov/planning/contact",
        "code": "https://www.cabq.gov/planning/contact",
        "development": "https://www.cabq.gov/planning/contact",
        "urban": "https://www.cabq.gov/planning/contact",
        "agis": "https://www.cabq.gov/planning/contact",
        "business": "https://www.cabq.gov/planning/contact",
        "311": "https://www.cabq.gov/311",
        "help": "https://www.cabq.gov/311",
        "assistance": "https://www.cabq.gov/311",
        "support": "https://www.cabq.gov/311",
        "violation": "https://www.cabq.gov/planning/report-a-violation",
        "complaint": "https://www.cabq.gov/planning/report-a-violation",
        "report": "https://www.cabq.gov/planning/report-a-violation"
    }

def save_conversation_history(conversation_history):
    """
    Saves conversation history to a timestamped JSON file.
    
    Args:
        conversation_history (list): List of tuples containing (user_message, assistant_message)
        
    Returns:
        str: Filename of the saved conversation history
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_history_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(conversation_history, f, indent=2)
    return filename

def load_conversation_history():
    """
    Loads conversation history from Streamlit session state or creates new empty list.
    
    Returns:
        list: Current conversation history from session state
    """
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    return st.session_state.conversation_history

@st.cache_resource(show_spinner=False)
def setup_qa_chain():
    """
    Sets up the conversational question-answering chain with memory and document retrieval.
    
    This function:
    1. Scrapes the CABQ Planning Department website
    2. Processes any uploaded PDF files
    3. Splits the content into manageable chunks
    4. Creates embeddings and stores them in a vector database
    5. Sets up a conversational chain with memory for context
    
    Returns:
        ConversationalRetrievalChain: Configured QA chain with memory, or None if setup fails
    """
    # Get URL from environment variable
    url = os.getenv("CABQ_PLANNING_URL")
    if not url:
        st.error("CABQ_PLANNING_URL not found in environment variables. Please set it in your .env file.")
        return None
    
    # Scrape and process the CABQ Planning Department webpages
    urls_to_scrape = [
        url,  # Main planning page
        "https://www.cabq.gov/planning/department-contact-information",  # Contact information page
        "https://www.cabq.gov/planning/contact",  # Planning contact page with location
        "https://www.cabq.gov/planning",  # Main planning page (duplicate to ensure comprehensive coverage)
        "https://www.cabq.gov/planning/about-the-planning-department",  # About page for division details
        "https://www.cabq.gov/311/pay-a-bill"  # Bill payment page
    ]
    text = scrape_cabq_pages(urls_to_scrape)
    
    # Process PDF files if available
    pdf_text = ""
    
    # Check for uploaded PDF in session state
    if 'uploaded_pdf' in st.session_state and st.session_state.uploaded_pdf is not None:
        pdf_text = extract_pdf_text(st.session_state.uploaded_pdf)
        if pdf_text:
            text += f"\n\n--- PDF User Guide Content ---\n\n{pdf_text}"
    
    # Check for PDF file in project directory
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    if pdf_files:
        try:
            with open(pdf_files[0], 'rb') as pdf_file:
                pdf_text = extract_pdf_text(pdf_file)
                if pdf_text:
                    text += f"\n\n--- PDF User Guide Content ({pdf_files[0]}) ---\n\n{pdf_text}"
        except Exception as e:
            st.warning(f"Could not process PDF file {pdf_files[0]}: {str(e)}")
    
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.create_documents([text])
    
    # Create embeddings and vector store for document retrieval
    embedding = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(docs, embedding)
    
    # Get model from environment variable
    model_name = os.getenv("OPENAI_MODEL")
    if not model_name:
        st.error("OPENAI_MODEL not found in environment variables. Please set it in your .env file.")
        return None
    
    # Validate and correct common model name issues
    if model_name == "gpt-4o-nano":
        model_name = "gpt-3.5-turbo"  # Use a more cost-effective model as fallback
        st.warning(f"Model name corrected from 'gpt-4o-nano' to '{model_name}'. Please update your .env file.")
    
    try:
        llm = ChatOpenAI(model=model_name)
    except Exception as e:
        st.error(f"Error creating LLM with model '{model_name}': {str(e)}")
        st.info("Please check your OPENAI_MODEL setting in the .env file. Valid models include: gpt-3.5-turbo, gpt-4o, gpt-4o-mini, gpt-4")
        return None
    
    # Create memory for conversation history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"  # Explicitly specify which output to store in memory
    )
    
    # Use ConversationalRetrievalChain instead of RetrievalQA for better conversation handling
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory,
        return_source_documents=True,
        chain_type="stuff",  # Use "stuff" for better context handling
        max_tokens_limit=4000,  # Limit tokens for better performance
        rephrase_question=True  # Rephrase question for better context understanding
    )
    
    return chain

# Streamlit UI Components
# Hide Streamlit menu and running status
st.markdown(
    """
    <style>
    /* Hide the main menu (three dots) */
    [data-testid="stToolbar"] { display: none !important; }
    /* Hide the running status spinner/text */
    [data-testid="stStatusWidget"] { display: none !important; }
    /* Hide footer */
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("ABQ Planning Assistant")

# Main chat interface
user_input = st.text_input("How can I help you today?")
if user_input:
    qa_chain = setup_qa_chain()
    if qa_chain:
        # Get response with conversation context
        result = qa_chain({"question": user_input})
        answer = result["answer"]
        
        # Check if the answer is unhelpful and provide 311 suggestion
        unhelpful_phrases = ["i don't know", "i don't have", "no information", "cannot find", "unable to", "not available"]
        answer_lower = answer.lower()
        
        if any(phrase in answer_lower for phrase in unhelpful_phrases):
            answer = f"I don't have specific information about that topic in my current knowledge base. For this question, I recommend contacting 311 at 505-768-2000 or dialing 311 from any phone. They can connect you with the appropriate department or provide the most current information about your inquiry."
        
        # Check for specific service requests and provide direct links
        service_links = get_service_links()
        user_input_lower = user_input.lower()
        
        # Check if user is asking about specific services
        relevant_links = {}  # Use dict to avoid duplicates by URL
        for keyword, link in service_links.items():
            if keyword in user_input_lower:
                relevant_links[link] = keyword  # Store by URL to avoid duplicates
        
        # Filter out specific personal contact information
        personal_info_phrases = [
            "alan varela", "james aranda", "jeremy keiser", 
            "director", "deputy director", "deputy directors",
            "[email protected]", "email at", "via email"
        ]
        
        if any(phrase in answer_lower for phrase in personal_info_phrases):
            # Replace with general contact information
            if "violation" in answer_lower or "complaint" in answer_lower:
                answer = "To file a complaint for a permit violation, you can contact the Planning Department at 505-924-3860 or dial 311 (505-768-2000). They will connect you with the appropriate staff member to handle your complaint. Be sure to provide details about the violation, including the specific permit in question, so they can better assist you."
            else:
                answer = "For this inquiry, please contact the Planning Department at 505-924-3860 or dial 311 (505-768-2000). They will connect you with the appropriate staff member to assist you."
        
        # Check if answer mentions visiting the website and add planning department link
        website_phrases = ["visit the planning department", "visit the website", "planning department's website", "planning website"]
        if any(phrase in answer_lower for phrase in website_phrases):
            # Add planning department link to relevant links
            relevant_links["https://www.cabq.gov/planning"] = "planning"
        
        # Check if answer mentions violation reporting and add violation link
        violation_phrases = ["report a violation", "file a complaint", "violation", "complaint"]
        if any(phrase in answer_lower for phrase in violation_phrases) and "website" in answer_lower:
            # Add violation reporting link
            relevant_links["https://www.cabq.gov/planning/report-a-violation"] = "violation"
        
        # Display the question and answer in a clean format
        st.write("**Answer:**")
        st.write(answer)
        
        # Display relevant direct links only if there are any
        if relevant_links:
            st.write("**🔗 Direct Links:**")
            for link, keyword in relevant_links.items():
                if keyword in ["permit", "license", "application"]:
                    st.markdown(f"• **ABQ-PLAN**: [Apply Online]({link})", unsafe_allow_html=True)
                elif keyword in ["account", "create account", "new account", "register", "login", "sign in"]:
                    st.markdown(f"• **ABQ-PLAN**: [Account Services]({link})", unsafe_allow_html=True)
                elif keyword in ["status", "check status", "application status", "permit status"]:
                    st.markdown(f"• **ABQ-PLAN**: [Check Status]({link})", unsafe_allow_html=True)
                elif keyword in ["contact", "location", "located", "address", "where", "phone"]:
                    st.markdown(f"• **Contact Information**: [View Details]({link})", unsafe_allow_html=True)
                elif keyword in ["bill", "payment", "pay"]:
                    st.markdown(f"• **Bill Payment**: [Pay Online]({link})", unsafe_allow_html=True)
                elif keyword == "planning":
                    st.markdown(f"• **Planning Department**: [Main Page]({link})", unsafe_allow_html=True)
                elif keyword in ["division", "divisions", "building", "code", "development", "urban", "agis", "business"]:
                    st.markdown(f"• **Contact Information**: [View Details]({link})", unsafe_allow_html=True)
                elif keyword in ["311", "help", "assistance", "support"]:
                    st.markdown(f"• **311 Services**: [Get Help]({link})", unsafe_allow_html=True)
                elif keyword in ["violation", "complaint", "report"]:
                    st.markdown(f"• **Violation Reporting**: [File a Complaint]({link})", unsafe_allow_html=True)
        
        # Save to conversation history (hidden from UI)
        conversation_history = load_conversation_history()
        conversation_history.append((user_input, answer))
        st.session_state.conversation_history = conversation_history
