# 📄 Template-Based Financial Report Generation in Agentic and Decomposed Information Retrieval

**Official Implementation**  of
**_Template-Based Financial Report Generation in Agentic and Decomposed Information Retrieval_**  
_To appear in the Proceedings of the 48th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR 2025)_

## 📄  Paper
📎 [Template-Based Financial Report Generation in Agentic and Decomposed Information Retrieval](https://arxiv.org/abs/2504.14233)

## 👤 Authors

<table>
  <tr>
    <!-- <td align="center" width="130"> -->
    <td align="center" width="140" style="background: #fff; border-radius: 12px; box-shadow: 0 1px 6px rgba(0,0,0,0.1); padding: 10px;">
      <a href="https://github.com/bryant-nn">
        <img src="https://github.com/bryant-nn.png" width="80px"><br>
        <sub><b>Yong-En Tian</b></sub>
      </a>
    </td>
    <!-- <td align="center" width="130"> -->
    <td align="center" width="140" style="background: #fff; border-radius: 12px; box-shadow: 0 1px 6px rgba(0,0,0,0.1); padding: 10px;">
      <a href="https://github.com/tommytyc">
        <img src="https://github.com/tommytyc.png" width="80px"><br>
        <sub><b>Yu-Chien Tang</b></sub>
      </a>
    </td>
    <!-- <td align="center" width="130"> -->
    <td align="center" width="140" style="background: #fff; border-radius: 12px; box-shadow: 0 1px 6px rgba(0,0,0,0.1); padding: 10px;">
      <a href="https://github.com/KuangDW">
        <img src="https://github.com/KuangDW.png" width="80px"><br>
        <sub><b>Kuang-Da Wang</b></sub>
      </a>
    </td>
  </tr>
</table>

---
## 🧾 Overview

This repository provides two generation pipelines (AgenticIR and DecomposedIR) for financial and climate report generation.  
It supports task decomposition, retrieval-based generation, and multiple evaluation strategies.


## 📦 Requirements
Set up the Python environment using Conda:
```
conda create -n myenv python=3.12.2
conda activate myenv
pip install -r requirements.txt
```
👉 Note: This project requires a .env file for API keys.
Create a file named .env in the root directory and include:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 📁 Project Structure
```
.
├── Finance/                      # Financial data (to be released)
├── SumIPCC/                      # Climate report generation
├── crawler.py                    # Script to crawl financial data
├── requirements.txt              # Dependencies
├── .env
└── README.md                     # This file         
```

## 📊 Finance
### 📚 Contents
- AgenticIR/ – Agent-based generation

- DecomposedIR/ – Report generation via decomposed queries

- data/ – Earnings call transcripts, balance-sheet, cash-flow and income statement

### 🔧 Features
1. **Agentic Report Generation**:
   - Uses agents to generate financial reports.
   - Supports task decomposition and retrieval-based generation.

2. **Decomposed Report Generation**:
   - Breaks down report generation into smaller subquery for improved accuracy.
   - Embedding-based retrieval of relevant data chunks.

3. **Evaluation Tools**:
   - Supports DecompEval and G-Eval metrics for reference-free evaluating the quality of generated summaries and readability of generated summaries.


### 🚀 Usage Instructions
#### 🧠 AgenticIR
1. Generate Reports
```
# Arguments:
# -r, self-reflection
# -c, company (="INTC", "GFS", "SSNLF", "TSM", "UMC")
python Finance/AgenticIR/agentic_main.py -c INTC [-r]
```
2. Evaluate Reports
```
# Arguments:
# -c, company (="INTC", "GFS", "SSNLF", "TSM", "UMC")
python Finance/AgenticIR/Eval/eval.py -c INTC
```
3. View Evaluation Results
```
Open notebook:
Finance/AgenticIR/Eval/result_eval.ipynb
```

#### 🧩 DecomposedIR
1. Generate Reports
```
# Arguments:
# -r, self-reflection
# -c, company (="INTC", "GFS", "SSNLF", "TSM", "UMC")
python Finance/DecomposedIR/decomposed_main.py -c INTC [-r]
```
2. Evaluate Reports
```
python Finance/DecomposedIR/Eval/eval.py
```
3. View Evaluation Results
```
Open notebook:
Finance/DecomposedIR/Eval/result_eval.ipynb
```


## 🌍 SumIPCC (Climate Report Generation)
### 📚 Contents
- AgenticIR/ – Agent-based generation

- DecomposedIR/ – Report generation via decomposed queries

- data/ – Original and processed SumIPCC data

### 🔧 Features
1. **Agentic Report Generation**:
   - Uses agents to generate climate reports.
   - Supports task decomposition and retrieval-based generation.

2. **Decomposed Report Generation**:
   - Breaks down report generation into smaller subquery for improved accuracy.
   - Embedding-based retrieval of relevant data chunks.

3. **Evaluation Tools**:
   - Supports ROUGE and BERTScore metrics for evaluating the quality of generated summaries.
   - Compares generated summaries with ground truth data.

4. **Data Processing**:
   - Processes datasets to create structured templates and ground truth for evaluation.

### 🚀 Usage Instructions
#### 🧠 AgenticIR
1. Generate Reports
```
# Arguments:
# -r, self-reflection
python SumIPCC/AgenticIR/agentic_main.py [-r]
```
2. Evaluate Reports
```
python SumIPCC/AgenticIR/Eval/eval.py
```
3. View Evaluation Results
```
Open notebook:
SumIPCC/AgenticIR/Eval/result_eval.ipynb
```

#### 🧩 DecomposedIR
1. Generate Reports
```
# Arguments:
# -r, self-reflection
python SumIPCC/DecomposedIR/decomposed_main.py [-r]
```
2. Evaluate Reports
```
python SumIPCC/DecomposedIR/Eval/eval.py
```
3. View Evaluation Results
```
Open notebook:
SumIPCC/DecomposedIR/Eval/result_eval.ipynb
```

#### 📂 Data Format
Original and processed SumIPCC data are organized as follows:
```
SumIPCC/data/
├── all_data/                       # Raw SumIPCC data
└── process_data/
    └── Report_1/                   # Example
        ├── AgenticIR_result/       # Agent-based outputs
        ├── DecomposedIR_result/    # Decomposed outputs
        ├── full_paragraphs.txt     # Original report
        ├── groundtruth.py          # Ground truth summaries
        ├── question_decomposed.py  # Query decompositions
        └── report_template.py      # Report template structure

```

## 📝 License

This project is licensed under the [MIT License](./LICENSE).


## 📄 Citation
Please cite our work if you find it helpful:
```
@inproceedings{tian2025template,
  title={Template-based financial report generation in agentic and decomposed information retrieval},
  author={Tian, Yong-En and Tang, Yu-Chien and Wang, Kuang-Da and Yen, An-Zi and Peng, Wen-Chih},
  booktitle={Proceedings of the 48th International ACM SIGIR Conference on Research and Development in Information Retrieval},
  pages={2706--2710},
  year={2025}
}

```
