### **2025-04-01** - Version 0.0.4
#### 🔧 **Bug Fix**
- Handle the case when `label` are not present during CLI evaluation. (#24)

### **2025-01-25** - Version 0.0.3
#### 🆕 **New Features**
- Added support for two new datasets: [`Safe-RLHFmini`](https://github.com/ThuCCSLab/JailbreakEval/blob/main/data/Safe-RLHFmini.csv) and [`JAILJUDGEmini`](https://github.com/ThuCCSLab/JailbreakEval/blob/main/data/JAILJUDGEmini.csv). For the original details, please visit [Safe-RLHF](https://github.com/PKU-Alignment/safe-rlhf) and [JAILJUDGE](https://github.com/PKU-Alignment/safe-rlhf).
- Add support for LlamaGuard3.
- Add evaluation results on the new dataset.

### **2024-12-11** - Version 0.0.2
#### 🔧 **Bug Fix**
- Adapted the framework to support the latest version of `transformers`

### **2024-05-25** - Version 0.0.1
#### 🚀 **Initial Release**
- Launched `JailbreakEval`, an integrated toolkit for evaluating jailbreak attempts.
- Included core functionalities with support for benchmarking using human-labeled datasets.
