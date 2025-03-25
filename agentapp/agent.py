from dataclasses import dataclass
import json
import operator
import traceback
import random
import numpy as np
import pandas as pd
import os

import time

from typing import Any, Dict, TypedDict, List, Union, Annotated
from pydantic import BaseModel, Field

from analysisapp.models import Company, FinDataA, AssetNote, AnalystUser
from fundamentals.calculations import addIndicators

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, WebBaseLoader
from langchain_google_community import GoogleSearchAPIWrapper

from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from langgraph.constants import Send

from .prompts import *



MODEL_4o = "gpt-4o"
MODEL_4o_mini = "gpt-4o-mini"
MODEL_o3_mini = "o3-mini"


ANALYSTS = [
    {"name": "Ray Dalio", "role": "Macro Investor", "description": "Focuses on economic cycles, monetary policy, and global macroeconomic trends to guide long-term investment decisions."},
    {"name": "Warren Buffett", "role": "Value Investor", "description": "Seeks fundamentally strong companies trading below their intrinsic value with a long-term, high-conviction approach."},
    {"name": "Peter Lynch", "role": "Growth Investor", "description": "Identifies companies with high earnings growth potential and strong competitive advantages before they become widely recognized."},
]

QUESTIONS = [
    "What asset class does this investment belong to, and what are its defining characteristics?",
    "How does this asset create, preserve, or generate value over time?",
    "What are the primary risks and uncertainties associated with this asset?",
    "What external factors or global trends could significantly impact the asset's value and performance?",
    "What are the key market features, such as liquidity and accessibility, that affect this asset?"
]


def sleep():
    time.sleep(5)
    
@dataclass
class Analyst:
    name: str
    role: str
    description: str
    
    @classmethod
    def create_all(cls, data:List[Dict]) -> List["Analyst"]:
        return [cls(a["name"], a["role"], a["description"]) for a in data]
    
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nDescription: {self.description}"


class AnalystQuestionState(TypedDict):
    analyst: Analyst
    analysts_question: str
    context: Annotated[List[str], operator.add]
    answers: List[str]
    
class SumarizedQuestionState(TypedDict):
    question_analysts: List[Analyst]
    question: str
    web_research: str
    answers: Annotated[List[str], operator.add]
    sections: Annotated[List[Dict[str, str]], operator.add]
 
class ResearchState(TypedDict):
    analysts: List[Analyst]
    questions: Annotated[List[str], operator.add]
    user_query: str
    sections: Annotated[List[Dict[str, str]], operator.add]
    introduction: str
    conclusion: str
    report: str
        

class QuestionModel(BaseModel):
    text: str = Field(description="The question being asked to experts.")

class QuestionsListModel(BaseModel):
    questions: List[QuestionModel] = Field(description="List of structured questions any particular aspect of sumbject of research.")


class SearchQueryModel(BaseModel):
    phrase: str = Field(description="The optimized search phrase for retrieving fundamental analysis information.")

class SearchQueriesListModel(BaseModel):
    queries: List[SearchQueryModel] = Field(description="A list of optimized search phrases to find relevant information for fundamental analysis.")
    
class CompanyResearchAgent():
    USER_AGENTS = {}
    
    def __init__(self, user: AnalystUser, company_id:int, user_query:str, file_list:list, model:str=MODEL_4o_mini):
        # app
        self.user = user
        self.company = Company.objects.get(id=company_id)
        df = FinDataA.getDataframe(company_id=company_id, sortby="year")
        addIndicators(df)
        self.df_dict = df.replace({np.nan: None}).to_dict(orient='list')
        self.asset_info = self.process_company_data()
        self.user_query = user_query
        self.file_list = file_list
        
        # ai
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.user.openai_api_key)
        self.vector_store = None
        self.llm = ChatOpenAI(model=model)
        
        # init
        self.analystQuestionGraph = None
        self.sumarizedQuestionGraph = None
        self.researchGraph = None
        self.createAgent()
        self.saveGraphImage(self.researchGraph, "agent_graph")
        
        self.results = None
        
        
    def generateReport(self, questions=None, analysts=None, user_query=None):
        self.results = {
            "success": False,
            "logs": [],
            "errors": [],
            "report": None,
        }
        
        if self.user.id in self.USER_AGENTS:
            self.results["success"] = False
            self.results["errors"].append("The agent is currently working on a task. Please wait until it finishes before assigning another task.")
        else:
            self.USER_AGENTS[self.user.id] = self
            
            if questions is None:
                questions = QUESTIONS
            if analysts is None:
                analysts = ANALYSTS
            if user_query is None:
                user_query = self.user_query
            if user_query is None:
                user_query = "User did not provide query."
            
            state = {
                "analysts": Analyst.create_all(analysts) if analysts else Analyst.create_all(ANALYSTS),
                "questions": questions if questions else QUESTIONS,
                "user_query": user_query if user_query else self.user_query,
                "sections": [],
                "introduction": "",
                "conclusion": "",
                "report": "",
            }
            try:
                sate = self.researchGraph.invoke(state)
                report = sate.get("report")
                self.results["success"] = True
                self.results["report"] = report 
            except Exception as e:
                self.results["success"] = False
                self.results["errors"].append(f"Error acours: {e}")
            del self.USER_AGENTS[self.user.id]
        return self.results
    
    
    # LOW LEVEL GRAPH ##################################################################################################################    
    def searchFilesProvidedByUser(self, state: AnalystQuestionState):
        results = self.search_faiss(state["analysts_question"], k=5)
        context = "\n\n".join([f"[{result.metadata.get("source", "No source...")}]\n{result.page_content}" for result in results])
        return {"context": [context]}
    
    def answerQuestion(self, state: AnalystQuestionState):
        context_str = "\n\n".join([self.asset_info] + state["context"])
        messages = [
            SystemMessage(content=sys_answerQuestion.format(analyst=state["analyst"].persona)),
            HumanMessage(content=hum_answerQuestion.format(question=state["analysts_question"], context=context_str)),
        ]
        sleep()
        aimsg = self.llm.invoke(messages)
        answer = f"{state["analyst"].role}:\n{aimsg.content}"
        
        return {"answers": [answer]}
    
    
    def createAnalystQuestionGraph(self):
        self.analystQuestionGraphBuilder = StateGraph(AnalystQuestionState)
        self.analystQuestionGraphBuilder.add_node("company_files", self.searchFilesProvidedByUser)
        self.analystQuestionGraphBuilder.add_node("answer_question", self.answerQuestion)
            
        self.analystQuestionGraphBuilder.add_edge(START, "company_files")
        self.analystQuestionGraphBuilder.add_edge("company_files", "answer_question")
        self.analystQuestionGraphBuilder.add_edge("answer_question", END)
        
        self.analystQuestionGraph = self.analystQuestionGraphBuilder.compile()
        
    # MIDLE LEVEL GRAPH ##################################################################################################################
    def callQuestionGraph(self, state: SumarizedQuestionState):
        sleep()
        return [Send("question_graph", 
                     {"analyst": analyst, 
                      "analysts_question": state["question"],
                      }) for analyst in state["question_analysts"] ]
    def searchWeb(self, state: SumarizedQuestionState):
        question = state["question"]
        log(f"--> searchWeb, question: {question}")
        messages = [
            SystemMessage(content=sys_searchWeb),
            HumanMessage(content=hum_searchWeb.format(question=question)),
        ]
        sleep()
        aimsg = self.llm.invoke(messages)
        phrase = aimsg.content.strip()
        web_research = ""
        if len(phrase) > 0:
            documents = self.process_web_search(phrase, num_results=5)
            web_research = self.query_web_search(query=question, documents=documents, k=2)
            log(f"--> searchWeb, web_research:\n{web_research}")
        return {"web_research": web_research}
        
    def summarizeAnswers(self, state: SumarizedQuestionState):            
        answersStr = "\n\n".join(state["answers"])
        messages = [
            SystemMessage(content=sys_summarizeAnswers.format()),
            HumanMessage(content=hum_summarizeAnswers.format(question=state["question"], answers=answersStr, web_research=state["web_research"])),
        ]
        sleep()
        aimsg = self.llm.invoke(messages)
        
        question = state["question"]
        answer = aimsg.content
        return {"sections": [{question: answer}]}
    
    def createSumarizedQuestionGraph(self):
        self.sumarizedQuestionGraphBuilder = StateGraph(SumarizedQuestionState)
        self.sumarizedQuestionGraphBuilder.add_node("question_graph", self.analystQuestionGraph)
        self.sumarizedQuestionGraphBuilder.add_node("web_search", self.searchWeb)
        self.sumarizedQuestionGraphBuilder.add_node("summarize_answers", self.summarizeAnswers)
        
        self.sumarizedQuestionGraphBuilder.add_conditional_edges(START, self.callQuestionGraph, ["question_graph"])
        self.sumarizedQuestionGraphBuilder.add_edge("question_graph", "web_search")
        self.sumarizedQuestionGraphBuilder.add_edge("web_search", "summarize_answers")
        self.sumarizedQuestionGraphBuilder.add_edge("summarize_answers", END)
        
        self.sumarizedQuestionGraph = self.sumarizedQuestionGraphBuilder.compile()
    
    # HIGH LEVEL GRAPH ##################################################################################################################   
    def querySafaGuard(self, state: ResearchState):
        messages = [
            SystemMessage(content=sys_filterUserQuery),
            HumanMessage(content=hum_filterUserQuery.format(user_query=state["user_query"])),
        ]
        sleep()
        aimsg = self.llm.invoke(messages)
        safe_query = aimsg.content
        return {"user_query": safe_query}

    def loadFiles(self, state: ResearchState):
        self.process_uploaded_files(self.file_list)
        return {}

    def createUserBasedQuestions(self, state: ResearchState):
        ctx_lsit = [
            f"Company data:\n{self.process_company_data()}",
        ]
        
        messages = [
            SystemMessage(content=sys_userQuestions.format()),
            HumanMessage(content=hum_userQuestions.format(context="\n\n".join(ctx_lsit), user_query=state["user_query"])),
        ]
        
        structured_llm = self.llm.with_structured_output(QuestionsListModel)
        sleep()
        result = structured_llm.invoke(messages)
        questions = [q.text for q in result.questions]
        if questions is None:
            questions = []
        return {"questions": questions}
    
    
    def callAnswerGraph(self, state: ResearchState):
        sections = []
        for question in state["questions"]:
            sleep()
            result = self.sumarizedQuestionGraph.invoke({
                "question": question,
                "question_analysts": state["analysts"]
            })
            sections.extend(result.get("sections", []))
        return {"sections": sections}
        
    def writeIntroduction(self, state: ResearchState):
        all_answers = "\n\n".join(["\n".join([f"### {question}\n{answer}" for question, answer in section.items()]) for section in state["sections"]])
        messages = [
            SystemMessage(content=sys_writeIntroduction),
            HumanMessage(content=hum_writeIntroduction.format(context=self.asset_info, answers=all_answers)),
        ]
        sleep()
        aimsg = self.llm.invoke(messages)
        introduction = aimsg.content
        return {"introduction": introduction}

    def writeConclusion(self, state: ResearchState):
        all_answers = "\n\n".join(["\n".join([f"### {question}\n{answer}" for question, answer in section.items()]) for section in state["sections"]])
        
        messages = [
            SystemMessage(content=sys_writeConclusion),
            HumanMessage(content=hum_writeConclusion.format(context=self.asset_info, answers=all_answers)),
        ]
        sleep()
        aimsg = self.llm.invoke(messages)
        conclusion = aimsg.content
        return {"conclusion": conclusion}

    def writeReport(self, state: ResearchState):
        introduction = state["introduction"]
        conclusion = state["conclusion"]
        
        sections = "\n\n".join(["\n".join([f"### {question}\n{answer}" for question, answer in section.items()]) for section in state["sections"]])
        
        report = f"{introduction}\n\n#Questions:\n{sections}\n\n{conclusion}"
        
        return {"report": report}
     
    def createResearchGraph(self):
        self.researchGraphBuilder = StateGraph(ResearchState)
        self.researchGraphBuilder.add_node("get_user_query", self.querySafaGuard)
        self.researchGraphBuilder.add_node("load_files", self.loadFiles)
        self.researchGraphBuilder.add_node("add_questions", self.createUserBasedQuestions)
        self.researchGraphBuilder.add_node("answer_graph", self.callAnswerGraph)                                       
        self.researchGraphBuilder.add_node("write_introduction", self.writeIntroduction)
        self.researchGraphBuilder.add_node("write_conclusion", self.writeConclusion)
        self.researchGraphBuilder.add_node("write_report", self.writeReport)

        self.researchGraphBuilder.add_edge(START, "get_user_query")
        self.researchGraphBuilder.add_edge("get_user_query", "load_files")
        self.researchGraphBuilder.add_edge("load_files", "add_questions")

        self.researchGraphBuilder.add_edge("add_questions", "answer_graph")                            
        self.researchGraphBuilder.add_edge("answer_graph", "write_introduction")
        self.researchGraphBuilder.add_edge("answer_graph", "write_conclusion")
        self.researchGraphBuilder.add_edge("write_introduction", "write_report")
        self.researchGraphBuilder.add_edge("write_conclusion", "write_report")
        self.researchGraphBuilder.add_edge("write_report", END) 
        
        self.researchGraph = self.researchGraphBuilder.compile()
        
        
        
    ###################################################################################################################    
    def createAgent(self):
        self.createAnalystQuestionGraph()
        self.createSumarizedQuestionGraph()
        self.createResearchGraph()
        
    ###################################################################################################################
    
    def process_company_data(self):
        if not self.company:
            self.results["logs"].append("Unable to retrieve asset data because the object is not defined.")
            return"User did not provide asset to analyze."
        else:
            data = []
            data.append(f"asset name: {self.company.name}")
            data.append(f"asset tikcer: {self.company.ticker}")
            data.append(f"asset description: {self.company.description}")
            data.append(f"asset country: {self.company.country}")
            data.append(f"currency of financial data: {self.company.currency}")
            data.append(f"asset financial statements:")
            data.append(str(self.df_dict))
            return "\n".join(data)
    
    def process_web_search(self, phrase: str, num_results: int = 10, chunk_size:int=1000, chunk_overlap:int=200, max_doc_length=10000):
        google = GoogleSearchAPIWrapper(google_api_key=self.user.google_api_key, google_cse_id=self.user.google_cse_id)
        search_results = None
        try:
            search_results = google.results(phrase, num_results=num_results)
            urls = [result['link'] for result in search_results]
        except Exception as e:
            return [] 

        documents = []
        for url in urls:
            try:
                loader = WebBaseLoader(
                    [url],
                    bs_get_text_kwargs={'strip': True},
                    continue_on_failure=True,
                    requests_kwargs={"timeout": 10}
                )
                loaded_docs = loader.load()
                for d in loaded_docs:
                    doc_length = len(d.page_content)
                    if doc_length > max_doc_length:
                        start_idx = random.randint(0, doc_length - max_doc_length)
                        d.page_content = d.page_content[start_idx : start_idx + max_doc_length]
                    else:
                        d.page_content = d.page_content[ : max_doc_length]
                documents.extend(loaded_docs)
            except Exception as e:
                self.results["logs"].append(f"Error for phrase ({phrase}), while loading page ({url}): {e}")
        if len(documents) > 0:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            split_texts = text_splitter.split_documents(documents)
            return split_texts  
        else:
            return []
    
    def query_web_search(self, query: str, documents, k=2):
        try:
            temp_vector_store = FAISS.from_documents(documents, self.embeddings)
            results = temp_vector_store.similarity_search(query, k=k)
            context = "\n\n".join([f"source: {result.metadata.get("source", "No source...")}\n{result.page_content}" for result in results])
            return f"Found information on the web for the query: {query}\n{context}"
        except Exception as e:
            self.results["logs"].append(f"Error for query ({query}), while searching through websites: {e}")
            return f"No information found for the query: {query}"
        

    def process_uploaded_files(self, uploaded_files, chunk_size:int=500, chunk_overlap:int=100):
        documents = []
        for f in uploaded_files:
            file_extension = os.path.splitext(f.name)[1].lower()  

            if file_extension == ".pdf":
                loader = PyPDFLoader(f)
                docs = loader.load()
            elif file_extension == ".txt":
                file_content = f.read().decode('utf-8')
                docs = [Document(page_content=file_content, metadata={"source": f.name})]
            else:
                continue  

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            split_docs = text_splitter.split_documents(docs)

            for doc in split_docs:
                doc.metadata["source"] = f.name

            documents.extend(split_docs)
        self.update_faiss_db(documents)

    def update_faiss_db(self, docs):
        if docs is None or len(docs) == 0:
            return
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(docs, self.embeddings)
        else:
            self.vector_store.add_documents(docs)
            
    def search_faiss(self, query, k=5):
        if self.vector_store is None:
            return []
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def add_chunked_text_list(self, texts: List[str], sources: List[str], chunk_size:int=500, chunk_overlap:int=100):
        docs = [Document(page_content=text, metadata={"source": source}) for text, source in zip(texts, sources)]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        split_docs = text_splitter.split_documents(docs)
        self.update_faiss_db(split_docs)

    def add_full_text(self, text: str, source: str):
        docs = [Document(page_content=text, metadata={"source": source})]
        self.update_faiss_db(docs)
