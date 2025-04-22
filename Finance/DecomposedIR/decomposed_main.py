from bot_pool import generate_result_with_retrieved_chunk, re_generate_result_with_retrieved_chunk, summarize, reflection
import os
from question_decomposed_llm import question_prompt_dict
import json
from embed import Fin_Mpnet_Base
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
from transfer_file import get_previous_and_next_quarter, export_json_of_time, report_to_json, find_files_with_company
import argparse
import sys

class Metadata:
    def __init__(self, company, year, quarter):
        assert company in ["INTC", "GFS", "SSNLF", "TSM", "UMC"]
        self.company = company
        self.year = year
        self.quarter = quarter

def load_json_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data = json.dumps(data, ensure_ascii=False)
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--company", type=str, help="Company name", choices=["INTC", "GFS", "SSNLF", "TSM", "UMC"], required=True)
    parser.add_argument("-r", "--reflection", action="store_true", help="Is self-reflection")

    args = parser.parse_args()

    transcript_files = find_files_with_company("../data/transcript", args.company)

    for transcript_file in transcript_files:
        sys.stdout.write(f"Processing file: {transcript_file}\r")
        sys.stdout.flush()

        year, quarter = transcript_file.split("_")[1], transcript_file.split("_")[2].split(".")[0]

        if year == '2019' or year == '2020':
            continue

        metadata = Metadata(company=args.company , year=year, quarter=quarter)

        # === Create Result Path ===
        result_path = f"YOUR_SUMMARY_RESULT_PATH"  # Replace with your desired path
        result_file = f"{metadata.company}_{metadata.year}_{metadata.quarter}.json"

        if os.path.exists(f"{result_path}/{result_file}"):
            continue
        if not os.path.exists(result_path):
            os.makedirs(result_path)

        last_quarter, next_quarter = get_previous_and_next_quarter(f"{metadata.year} {metadata.quarter}")


        transcript_path = f"../data/transcript/{transcript_file}"
        transcript = load_json_transcript(transcript_path)


        # =================== Embedding ===================
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        text_chunks = text_splitter.create_documents([transcript])

        text_chunks_list = [chunk.page_content for chunk in text_chunks]

        embeddings = Fin_Mpnet_Base(model_name="mukaj/fin-mpnet-base", device = 'cuda', trust_remote_code = True, documents = text_chunks_list)

        statement_json = export_json_of_time({"calendarYear": metadata.year, "period": metadata.quarter}, [f"../data/income-statement/{metadata.company}.json", f"../data/balance-sheet-statement/{metadata.company}.json", f"../data/cash-flow-statement/{metadata.company}.json"])
        
        question_answer_string = ""
        final_report = []
        for i, (key, questions) in tqdm(enumerate(question_prompt_dict.items())):
            # print(f"{key}...")
            report_list = []
            layer_1 = {}
            for j, question in enumerate(questions):
                question = question.replace("#TIME#", f"{metadata.year} {metadata.quarter}"). replace("#NEXT_QUARTER#", next_quarter).replace("#LAST_QUARTER#", last_quarter)

                # ==== Retrieve Relevant Chunk by Embedding ====
                scores, indices = embeddings.retrieve_relevant_chunk(query_list = [question], top_k = 3)

                report_dict = {}
                report_dict['question'] = question
                retrieved_list = []

                for j, idx in enumerate(indices[0]):
                    retrieved_list.append(text_chunks[idx].page_content)
                report_dict['retrieved'] = retrieved_list
                # =================== Embedding ===================


                # =================== Generation ===================
                relevant_text = "\n".join(retrieved_list)
                result = generate_result_with_retrieved_chunk(question, relevant_text, statement_json)
                result = result.content
                
                if args.reflection:
                    reflection_feedback = reflection(question, result)
                    reflection_feedback = reflection_feedback.content
                    result = re_generate_result_with_retrieved_chunk(question, result, relevant_text, statement_json, reflection_feedback)
                    result = result.content

                report_dict['init_answer'] = result

                report_list.append(report_dict)

                question_answer_string += f"Question {j}: {question}\nAnswer {j}: {result}\n\n"


            layer_1_aspect = key.replace("#TIME#", f"{metadata.year} {metadata.quarter}"). replace("#NEXT_QUARTER#", next_quarter).replace("#LAST_QUARTER#", last_quarter)

            summary = summarize(question_answer_string, layer_1_aspect)
            layer_1[layer_1_aspect] = {"summary": summary.content, "report": report_list}
            final_report.append(layer_1)

        report_to_json(final_report, f"{result_path}/{result_file}")

    sys.stdout.write("\nProcessing complete.\n")
    sys.stdout.flush()

