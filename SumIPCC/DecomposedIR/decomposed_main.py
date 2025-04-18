from bot_pool import generate_result_with_retrieved_chunk, re_generate_result_with_retrieved_chunk, summarize, reflection
import os
import json
from embed import Stella_Embedding
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
import argparse
import sys
import importlib.util

def load_txt_report(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()
    
def report_to_json(report, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--reflection", action="store_true", help="Is self-reflection")
    args = parser.parse_args()

    report_files = os.listdir("../../data/SumIPCC/process_data")

    for transcript_file in report_files:
        sys.stdout.write(f"Processing file: {transcript_file}\r")
        sys.stdout.flush()


        # === Create Result Path ===
        result_path = f"../../data/SumIPCC/process_data/{transcript_file}/DecomposedIR_result"
        result_file = f"summary.json"

        if not os.path.exists(result_path):
            os.makedirs(result_path)

        paragraph_path = f"../../data/SumIPCC/process_data/{transcript_file}/full_paragraphs.txt"
        paragraph = load_txt_report(paragraph_path)

        # =================== Embedding ===================
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        text_chunks = text_splitter.create_documents([paragraph])

        text_chunks_list = [chunk.page_content for chunk in text_chunks]

        embeddings = Stella_Embedding(model_name="NovaSearch/stella_en_1.5B_v5", device = 'cuda:1', trust_remote_code = True, documents = text_chunks_list)
        
        # === import decomposed query ===
        script_dir = os.path.abspath(os.path.join("../../data/SumIPCC/process_data", transcript_file))
        module_path = os.path.join(script_dir, "question_decomposed.py")  # ensure complete Python file path

        if not os.path.exists(module_path):
            print(f"Warning: {module_path} does not exist, skipping...")
            continue

        module_name = f"question_{transcript_file}"  # dynamic naming to prevent name conflicts

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        report_template = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(report_template)  # execute module

        question_prompt_dict = report_template.question_prompt_dict  # get `ordered_result`

        question_answer_string = ""
        final_report = []
        for i, (key, questions) in tqdm(enumerate(question_prompt_dict.items())):
            report_list = []
            layer_1 = {}
            for j, question in enumerate(questions):

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
                result = generate_result_with_retrieved_chunk(question, relevant_text)
                result = result.content

                if args.reflection:
                    reflection_feedback = reflection(question, result)
                    reflection_feedback = reflection_feedback.content
                    result = re_generate_result_with_retrieved_chunk(question, result, relevant_text, reflection_feedback)
                    result = result.content

                report_dict['init_answer'] = result

                report_list.append(report_dict)

                question_answer_string += f"Question {j}: {question}\nAnswer {j}: {result}\n\n"

            layer_1_aspect = key

            summary = summarize(question_answer_string, layer_1_aspect)
            layer_1[layer_1_aspect] = {"summary": summary.content, "report": report_list}
            final_report.append(layer_1)

        report_to_json(final_report, f"{result_path}/{result_file}")

    sys.stdout.write("\nProcessing complete.\n")
    sys.stdout.flush()