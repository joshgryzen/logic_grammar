Recommended Python version 3.10+. 

Install requirements with: 

`pip install -r requirements.txt`

Run **get_model_response.py** to test a how hugging face model can translate the ruletaker dataset into ASP.

Example running with **Llama** on 1 test from the dataset:

`python get_model_response.py --model=meta-llama/Llama-3.2-3B-Instruct --n_tests=1`

To run the baseline comparison, simply run: 

`python get_model_response.py --model=meta-llama/Llama-3.2-3B-Instruct --n_tests=1 --baseline`

It is important to note that these currently only support Instruct fine-tuned hugging face models. 
The hugging face pipeline is different for Instruct and pretrain only models. 
