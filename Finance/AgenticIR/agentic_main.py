import os
import json
from typing import Dict, List, Annotated
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
from autogen import AssistantAgent, UserProxyAgent, Cache, register_function
from transfer_file import get_previous_and_next_quarter, export_json_of_time, find_files_with_company, convert_to_json
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from report_template import report_template_dict
import sys
from dotenv import load_dotenv
import autogen
load_dotenv()
import textwrap
import argparse

class Metadata:
    """Class to handle company metadata."""
    def __init__(self, company: str, year: str, quarter: str):
        assert company in ["INTC", "GFS", "SSNLF", "TSM", "UMC"], "Invalid company code."
        self.company = company
        self.year = year
        self.quarter = quarter


class FinancialReportGenerator:
    def __init__(self, config_list: List[Dict], company: str, json_data: str, metadata: Metadata, reflection: bool):
        self.config_list = config_list
        self.company = company
        self.metadata = metadata
        self.reflection = reflection
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="mukaj/fin-mpnet-base", device="cuda", trust_remote_code=True
        )
        self.json_data = json_data
        self.termination_msg = lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")

        # Initialize agents
        self.planner = self.create_planner_agent()
        self.planner_user = self.create_planner_user()
        self.retriever = self.create_retriever_agent()
        self.financial_manager = self.create_financial_manager_agent()
        self.assistant = self.create_assistant_agent()
        self.user_proxy = self.create_user_proxy_agent()
        self.self_reflection_planner = self.create_self_reflection_planner_agent()
        self.self_reflection_reviewer = self.create_self_reflection_reviewer_agent()

        # Register functions
        self.register_functions()

    def create_planner_agent(self) -> AssistantAgent:
        return AssistantAgent(
            name="planner",
            llm_config={"config_list": self.config_list, "cache_seed": None},
            system_message="You are a helpful AI assistant. You suggest a feasible plan "
            "for finishing a complex task by decomposing it into lots of sub-queries. "
            "If the plan is not good, suggest a better plan. "
            "If the execution is wrong, analyze the error and suggest a fix.",
            code_execution_config=False,
        )
    
    def create_planner_user(self):
        return UserProxyAgent(
            name="planner_user",
            human_input_mode="NEVER",
            # is_termination_msg=self.termination_msg,
            code_execution_config=False,
        )

    def create_retriever_agent(self):
        return RetrieveUserProxyAgent(
            name="Financial_Retriever",
            system_message="You are Financial_Retriever, a content retrieval assistant. "
            "Retrieve financial data from external resources when prompted by the financial team. "
            "Aim to answer complex questions accurately and efficiently using relevant documents.",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
            retrieve_config={
                "task": "qa",
                "docs_path": f"../data/transcript/{self.company}_{self.metadata.year}_{self.metadata.quarter}.json",
                "get_or_create": True,
                "overwrite": True,
                "update_context": True,
                "custom_text_split_function": self.text_splitter.split_text,
                "embedding_function": self.embedding_model,
                "new_docs": True,
            },
            code_execution_config=False,
            llm_config={"config_list": self.config_list, "timeout": 60, "temperature": 0, "cache_seed": None},
            description="Financial_Retriever. Retrieves relevant messages and data for complex questions to aid financial analysis.",
        )

    def create_financial_manager_agent(self) -> AssistantAgent:
        return AssistantAgent(
            name="Financial_Manager",
            system_message="You are the Financial Manager. Your responsibility is to answer the question given the retrieved context.",
            code_execution_config={"work_dir": "coding", "use_docker": False},
            llm_config={"config_list": self.config_list, "timeout": 60, "temperature": 0, "cache_seed": None},
        )

    def create_assistant_agent(self) -> AssistantAgent:
        return AssistantAgent(
            name="assistant",
            system_message="You are a helpful AI assistant. "
            "You can use the task planner to decompose a complex task with report template into sub-queries. "
            "You can also use the retrieve data to get earnings call transcript by sub-queries."
            "You can use the self-reflection process to analyze the financial report answer and recall the retreived data with self reflection feedback again ."
            "Make sure to follow through with the sub-queries. "
            "Follow the template to generate the financial report in text format. "
            "Add or Return 'TERMINATE' only if the final report is completed.",
            code_execution_config=False,
            llm_config={"config_list": self.config_list, "cache_seed": None},
        )

    def create_user_proxy_agent(self) -> UserProxyAgent:
        return UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            is_termination_msg = lambda x: "content" in x \
                                and x["content"] is not None \
                                and "TERMINATE" in x["content"],
            code_execution_config={"work_dir": "coding", "use_docker": False},
            default_auto_reply="reply 'TERMINATE' if all sub-task is completed.",
            llm_config={"config_list": self.config_list, "timeout": 60, "temperature": 0, "cache_seed": None},
        )

    def create_self_reflection_planner_agent(self) -> AssistantAgent:
        """
        Create an agent responsible for analyzing the financial report answer
        and planning improvements if necessary.
        """
        return AssistantAgent(
            name="Self_Reflection_Planner",
            system_message="You are a self-reflection planner. Your job is to analyze the financial report answer and help to suggest improvements.",
            code_execution_config=False,
            llm_config={"config_list": self.config_list, "timeout": 60, "temperature": 0, "cache_seed": None},
        )

    def create_self_reflection_reviewer_agent(self) -> UserProxyAgent:
        """
        Create an agent responsible for reviewing the planned improvements and deciding whether the response needs revision.
        """
        return UserProxyAgent(
            name="reviewer_agent",
            human_input_mode="NEVER",
            # is_termination_msg=self.termination_msg,
            code_execution_config=False,
        )

    def self_reflection_process(self, answer: str, question: str) -> str:
        """
        Run the self-reflection process using Self_Reflection_Planner and Self_Reflection_Reviewer.

        Args:
            answer (str): The answer generated by Financial_Manager.
            question (str): The original question.

        Returns:
            str: The final answer after self-reflection.
        """
        # Step 1: Use Self_Reflection_Planner to analyze and suggest improvements
        reflection_prompt = textwrap.dedent(f"""\
        Review the following financial report question and answer:
        ###
        Question: {question}
        Answer: {answer}
        ###
        Your job is to analyze the financial report answer and identify missing elements based on the following criteria:"
        1. Provide key financial details or numbers (e.g., revenue, profit, earnings)."
        2. Provide context for the company's financial performance.
        3. Provide reasoning or explanations for trends or changes.
        4. Mention expectations or guidances for future performance.

        If any improvements are needed, provide a short suggestion for how to improve it.
        """)
        with Cache.disk(cache_seed=5) as cache:
            self.self_reflection_reviewer.initiate_chat(
                self.self_reflection_planner,
                message=reflection_prompt,
                max_turns=1,
                cache=None,
            )
        improvement_plan = self.self_reflection_reviewer.last_message()["content"]
        
        return improvement_plan
    
    def task_planner(self, task: Annotated[str, "Question to ask the planner."]) -> str:
        last_quarter, next_quarter = get_previous_and_next_quarter(f"{metadata.year} {metadata.quarter}")
        report_template_str = ""
        for i, (key, sub_sections) in enumerate(report_template_dict.items()):
            section = key.replace("#TIME#", f"{metadata.year} {metadata.quarter}").replace(
                "#NEXT_QUARTER#", next_quarter
            ).replace("#LAST_QUARTER#", last_quarter)

            report_template_str += f"Section {i+1}: {section}\n"

            for j, sub_section in enumerate(sub_sections):
                sub_section_ = sub_section.replace("#TIME#", f"{metadata.year} {metadata.quarter}").replace("#NEXT_QUARTER#", next_quarter).replace("#LAST_QUARTER#", last_quarter)
                report_template_str += f"Sub Section {i+1}.{j+1}: {sub_section_}\n"

        task_decomposed_prompt = f"""You should try to solve the task: {task} By decomposing the report template into sub-queries given the following template:\n"""
        task_decomposed_prompt = task_decomposed_prompt + f"\n\nReport Template:\n{report_template_str}"

        with Cache.disk(cache_seed=3) as cache:
            self.planner_user.initiate_chat(self.planner, message=task_decomposed_prompt, max_turns=1, cache=None)
        return self.planner_user.last_message()["content"]

    def retrieve_data(self, question: Annotated[str, "Question to ask the retriever."], n_results: int = 3) -> str:
        n_results = 3
        _context = {"problem": question, "n_results": n_results}
        retrieve_prompt = self.retriever.message_generator(self.retriever, None, _context).replace(
            "If you can't answer the question with or without the current context, you should reply exactly `UPDATE CONTEXT`.",
            "",
        )
        retrieve_prompt = retrieve_prompt + f"Financial Statement JSON:\n{self.json_data}"
        
        if not self.reflection:
            with Cache.disk(cache_seed=4) as cache:
                self.retriever.initiate_chat(
                    self.financial_manager,
                    message=retrieve_prompt,
                    max_turns=3,
                    problem=question,
                    cache=None,
                )
            first_answer = self.retriever.last_message()["content"]
            # chat_history = self.retriever.chat_messages()
            return first_answer
        
        elif self.reflection:
            with Cache.disk(cache_seed=8) as cache:
                self.retriever.initiate_chat(
                    self.financial_manager,
                    message=retrieve_prompt,
                    max_turns=3,
                    problem=question,
                    cache=None,
                )
            first_answer = self.retriever.last_message()["content"]
    
            feedback_prompt = self.self_reflection_process(answer=first_answer, question=question)
            feedback_prompt = textwrap.dedent(f"""\
        \n\nThe previous financial report answer needs improvement based on the following suggestion
        ###
        Question: {question}
        Answer: {first_answer}
        ###
        Feedback: {feedback_prompt}
        ###
        Please follow the feedback to improve the financial report answer.""")
            retrieve_feedback_prompt = retrieve_prompt + feedback_prompt

            with Cache.disk(cache_seed=7) as cache:
                self.retriever.initiate_chat(
                    self.financial_manager,
                    message=retrieve_feedback_prompt,
                    max_turns=3,
                    problem=question,
                    cache=None,
                )

            return self.retriever.last_message()["content"]


    
    def register_functions(self):
        def task_planner_func(question: str) -> str:
            return self.task_planner(question)

        def retrieve_data_func(question: str, n_results: int = 3) -> str:
            return self.retrieve_data(question, n_results)

        register_function(
            task_planner_func,
            caller=self.assistant,
            executor=self.user_proxy,
            name="task_planner",
            description="A task planner that can help you decompose a complex task into sub-tasks.",
        )
        register_function(
            retrieve_data_func,
            caller=self.assistant,
            executor=self.user_proxy,
            name="retrieve_data",
            description="A retriever that can retrieve financial data from external resources.",
        )

    def generate_report(self, metadata: Metadata, report_template_dict: Dict):
        last_quarter, next_quarter = get_previous_and_next_quarter(f"{metadata.year} {metadata.quarter}")

        report_template_str = ""
        for i, (key, sub_sections) in enumerate(report_template_dict.items()):
            section = key.replace("#TIME#", f"{metadata.year} {metadata.quarter}").replace(
                "#NEXT_QUARTER#", next_quarter
            ).replace("#LAST_QUARTER#", last_quarter)

            report_template_str += f"Section {i+1}: {section}\n"

            for j, sub_section in enumerate(sub_sections):
                sub_section_ = sub_section.replace("#TIME#", f"{metadata.year} {metadata.quarter}").replace("#NEXT_QUARTER#", next_quarter).replace("#LAST_QUARTER#", last_quarter)
                report_template_str += f"Sub Section {i+1}.{j+1}: {sub_section_}\n"
        
        task = \
        f"""\
        As a financial analyst, you are given the financial reports template composed of several sections. 
        The section includes:
        ###
        {report_template_str}\
        ###
        Your final task is to fill in the template with the financial data of {metadata.company} in {metadata.year} {metadata.quarter}.
        You can use the task planner to decompose the report-template into sub-queries.
        You can also call the given function tools to retrieve the needed information from the earnings call transcript.
        
        Remember to refine the financial number in your generated content to ensure the numerical accuracy of the report. 
        
        Please respond in plain text only, without using any markdown formatting, symbols, or special characters. Ensure that your output is simple text without headings, bullet points, or any additional formatting.
        ###
        Your output format:
        Sub section 1.1: [Your content]
        Sub section 1.2: [Your content]
        ###
        Now, generate the financial report based on the template.\
        """
        with Cache.disk(cache_seed=1) as cache:
            self.user_proxy.initiate_chat(self.assistant, message=task, cache=None, max_turns=60)

        for key, value in self.user_proxy.chat_messages.items():
            if isinstance(key, autogen.agentchat.assistant_agent.AssistantAgent):
                messages_list = value 
                break

        last_message = self.user_proxy.last_message()["content"]
        last_message = last_message.replace("\n", "")
        if not last_message == ("TERMINATE"):
            return last_message
        else:
            print(f"last second message: {messages_list[-2]['content']}")
            return messages_list[-3]["content"]


# Example Usage
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--company", type=str, help="Company name", choices=["INTC", "GFS", "SSNLF", "TSM", "UMC"], required=True)
    parser.add_argument("-r", "--reflection", action="store_true", help="Is self-reflection")
    args = parser.parse_args()

    # === Global variables ===
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    transcript_files = find_files_with_company("../data/transcript", args.company)

    config_list = [
        {"model": "gpt-4o-mini", "api_key": os.getenv("OPENAI_API_KEY")},
    ]
    os.environ["OAI_CONFIG_LIST"] = json.dumps(config_list)

    for transcript_file in transcript_files:
        sys.stdout.write(f"Processing file: {transcript_file}\r")
        sys.stdout.flush()

        year, quarter = transcript_file.split("_")[1], transcript_file.split("_")[2].split(".")[0]
        if year == '2019' or year == '2020':
            continue

        metadata = Metadata(company=args.company, year=year, quarter=quarter)

        result_path = f"YOUR_SUMMARY_RESULT_PATH"  # Replace with your desired path
        result_file = f"{metadata.company}_{metadata.year}_{metadata.quarter}.json"

        if os.path.exists(f"{result_path}/{result_file}"):
            continue

        all_data = export_json_of_time(
                {"calendarYear": metadata.year, "period": metadata.quarter},
                [
                    f"../data/income-statement/{metadata.company}.json",
                    f"../data/balance-sheet-statement/{metadata.company}.json",
                    f"../data/cash-flow-statement/{metadata.company}.json",
                ],
            )
        generator = FinancialReportGenerator(config_list=config_list, company=args.company, json_data=all_data, metadata=metadata, reflection=args.reflection)

        report = generator.generate_report(metadata, report_template_dict)
        report = report.replace("TERMINATE", "")
        
        # report to txt
        if not os.path.exists(result_path):
            os.makedirs(result_path)

        try:
            convert_to_json(report, f"{result_path}/{result_file}") 
        except Exception as e:
            print(e)
            with open("error_list.txt", "a") as f:
                f.write(f"{result_path}/{result_file}\n")
            break

    sys.stdout.write("\nProcessing complete.\n")
    sys.stdout.flush()
