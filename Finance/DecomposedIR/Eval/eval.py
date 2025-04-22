from decomp_eval import DecompEval, ChatEval
import argparse 
import json
from evaluate_prompt import evaluate_prompt_dict
from chat_evaluate_prompt import chat_evaluate_prompt_dict
import sys
import os 

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
from transfer_file import find_files_with_company, export_json_of_time

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--company", type=str, help="Company name", choices=["INTC", "GFS", "SSNLF", "TSM", "UMC"], required=True)

    args = parser.parse_args()

    # === Global variables ===
    eval_dir = 'YOUR_EVAL_DIR'  # Replace with your actual evaluation directory
    source_dir = f"YOUR_SUMMARY_RESULT_DIR"  # Replace with your actual summary result directory

    result_files = find_files_with_company(f"{source_dir}", args.company)
    for result_file in result_files:
        sys.stdout.write(f"Processing file: {result_file}\r")
        sys.stdout.flush()

        if os.path.exists(f'../{eval_dir}/{args.company}/{result_file}'):
            with open(f"../{eval_dir}/{args.company}/{result_file}", 'r', encoding='utf-8') as f:
                report_list = json.load(f)
        else:
            with open(f"{source_dir}/{result_file}", 'r', encoding='utf-8') as f:
                report_list = json.load(f)


        year, quarter = result_file.split("_")[1], result_file.split("_")[2].split(".")[0]

        all_data = export_json_of_time({"calendarYear": year, "period": quarter}, [f"../../data/income-statement/{args.company}.json", f"../../data/balance-sheet-statement/{args.company}.json", f"../../data/cash-flow-statement/{args.company}.json"])

        transcript_path = f"../../data/transcript/{result_file}"


        # === Evaluate ===
        decomp = DecompEval(model_name='gpt-4o-mini')
        chat_eval = ChatEval(model_name="gpt-4o-mini")

        with open(f"{transcript_path}") as f:
            transtript = json.load(f)
            transtript = transtript['content']
            transtript = json.dumps(transtript)

        all_context = f"Earnings call: {transtript}\n\nFinancial Number{all_data}"

        for i, report_query in enumerate(report_list):
            if 'decomp_score' not in next(iter(report_list[i].values())):
                decomp_score_list = []
                for key, value in evaluate_prompt_dict.items():
                    question = value

                    # === DecompEval ===
                    results = decomp.evaluate(all_context, next(iter(report_query.values()))['summary'], question)
                    final_score = decomp.get_final_score(results)

                    decomp_dic = {}
                    decomp_dic[key] = f"{final_score:.2f}"

                    decomp_score_list.append(decomp_dic)

                next(iter(report_list[i].values()))["decomp_score"] = decomp_score_list

            if 'chat_eval' not in next(iter(report_list[i].values())):
                chat_eval_score = []
                for key, value in chat_evaluate_prompt_dict.items():
                    question = value

                    # === Chat Eval ===
                    final_score = chat_eval.get_final_score(next(iter(report_query.values()))['summary'], question)

                    chat_dic = {}
                    chat_dic[key] = f"{final_score:.2f}"

                    chat_eval_score.append(chat_dic)

                next(iter(report_list[i].values()))["chat_eval"] = chat_eval_score

        if not os.path.exists(f'../{eval_dir}/{args.company}/'):
            os.makedirs(f'../{eval_dir}/{args.company}/')

        with open(f"../{eval_dir}/{args.company}/{result_file}", 'w', encoding='utf-8') as f:
            json.dump(report_list, f, ensure_ascii=False, indent=4)

    sys.stdout.write("\nProcessing complete.\n")
    sys.stdout.flush()
