import json
import sys
import os 
import importlib.util
from rouge_score import rouge_scorer
import pandas as pd
from bert_score import BERTScorer

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
scorer = BERTScorer(model_type="microsoft/deberta-v3-large", lang="en", device='cuda:1')

def calculate_rouge_scores(reference_summaries, generated_summaries):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    results = []

    for ref, gen in zip(reference_summaries, generated_summaries):
        scores = scorer.score(ref, gen)
        result = {
            'Reference Summary': ref,
            'Generated Summary': gen,
            'ROUGE-1 Precision': scores['rouge1'].precision,
            'ROUGE-1 Recall': scores['rouge1'].recall,
            'ROUGE-1 F1': scores['rouge1'].fmeasure,
            'ROUGE-2 Precision': scores['rouge2'].precision,
            'ROUGE-2 Recall': scores['rouge2'].recall,
            'ROUGE-2 F1': scores['rouge2'].fmeasure,
            'ROUGE-L Precision': scores['rougeL'].precision,
            'ROUGE-L Recall': scores['rougeL'].recall,
            'ROUGE-L F1': scores['rougeL'].fmeasure,
        }
        results.append(result)
    
    return pd.DataFrame(results)

def calculate_bertscore(reference_summaries, generated_summaries):
    P, R, F1 = scorer.score(generated_summaries, reference_summaries)
    bert_results = []

    for p, r, f1 in zip(P, R, F1):
        result = {
            'BERTScore Precision': p.item(),
            'BERTScore Recall': r.item(),
            'BERTScore F1': f1.item(),
        }
        bert_results.append(result)
    
    return pd.DataFrame(bert_results)

if __name__ == "__main__":

    # === Global variables ===
    report_files = os.listdir("../../data/process_data")

    for result_file in report_files:
        eval_dir = f'../../data/process_data/{result_file}/AgenticIR_result'
        source_dir = f"../../data/process_data/{result_file}/AgenticIR_result"

        eval_filename = "eval.json"
        result_filename = "summary.json"

        sys.stdout.write(f"Processing file: {result_file}\r")
        sys.stdout.flush()

        # load summary result
        with open(f"{source_dir}/{result_filename}", 'r', encoding='utf-8') as f:
            report_list = json.load(f)

        paragraphs_path = f"../../data/process_data/{result_file}/full_paragraphs.txt"

        # === import report template, and ground truth ===
        script_dir = os.path.abspath(os.path.join("../../data/process_data", result_file))
        module_path = os.path.join(script_dir, "report_template.py") 
        ground_truth_path = os.path.join(script_dir, "groundtruth.py")

        module_name = f"report_template_{result_file}"
        module_name_ground_truth = f"ground_truth_{result_file}"

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        report_template = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(report_template) 

        spec_ground_truth = importlib.util.spec_from_file_location(module_name_ground_truth, ground_truth_path)
        ground_truth = importlib.util.module_from_spec(spec_ground_truth)
        spec_ground_truth.loader.exec_module(ground_truth) 

        report_template_dict = report_template.ordered_result
        ground_truth_dict = ground_truth.groundtruth_summary

        # === Evaluate ===
        with open(f"{paragraphs_path}") as f:
            climate_report = f.read()


        all_context = f"climate report: \n{climate_report}"

        for i, (report_query, ground_truth) in enumerate(zip(report_list, ground_truth_dict.values())):
            if 'rouge' not in report_query:
                if list(report_query.values())[0] == "Missing":
                    rouge_result = {
                        'Reference Summary': '',
                        'Generated Summary': '',
                        'ROUGE-1 Precision': 0,
                        'ROUGE-1 Recall': 0,
                        'ROUGE-1 F1': 0,
                        'ROUGE-2 Precision': 0,
                        'ROUGE-2 Recall': 0,
                        'ROUGE-2 F1': 0,
                        'ROUGE-L Precision': 0,
                        'ROUGE-L Recall': 0,
                        'ROUGE-L F1': 0,
                    }
                    report_query["rouge"] = rouge_result
                else:
                    rouge_results = calculate_rouge_scores([ground_truth], list(report_query.values()))
                    rouge_score_dic = rouge_results.to_dict(orient='records')[0]
                    report_query["rouge"] = rouge_score_dic

            if 'bertscore' in report_query:
                if list(report_query.values())[0] == "Missing":
                    bert_result = {
                        'BERTScore Precision': 0,
                        'BERTScore Recall': 0,
                        'BERTScore F1': 0,
                    }
                    report_query["bertscore"] = bert_result
                else:
                    bert_results = calculate_bertscore([ground_truth], list(report_query.values())[:1])
                    bert_score_dic = bert_results.to_dict(orient='records')[0]
                    report_query["bertscore"] = bert_score_dic

        with open(f"{eval_dir}/{eval_filename}", 'w', encoding='utf-8') as f:
            json.dump(report_list, f, ensure_ascii=False, indent=4)

    sys.stdout.write("\nProcessing complete.\n")
    sys.stdout.flush()

