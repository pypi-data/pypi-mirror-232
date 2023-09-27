# Medium multiply
A small demo library for a Medium publication about publishing libraries.

### Installation
```
pip install synthetic_rx
```

### Get started
How to multiply one number by another with this lib:

```Python
import pandas as pd
from rx.stats import reportgeneration
real_data = pd.read_csv("real data url")
synthetic_data = pd.read_csv('synthetic data url')
output="output.pdf"
report=reportgeneration(real_data,synthetic_data)
user_name = input("Enter User Name: ")
tool_used = input("Enter the Tool Used for Synthetic Data Generation: ")
### Create Report
report.create_pdf_report(output,user_name,tool_used)
```