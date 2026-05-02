Recommended Python version 3.10+. 

Install requirements with: 

`pip install -r requirements.txt`

Run **get_model_response_with_pipe_strong_negation.py** to test a how hugging face model can translate the ruletaker dataset into ASP.

Example running with **Llama**:

`python get_model_response_with_pipe_strong_negation.py --model=meta-llama/Llama-3.2-3B-Instruct`

To run the baseline comparison, simpley run: 

`python get_model_response_baseline.py --model=meta-llama/Llama-3.2-3B-Instruct`

It is important to note that these currently only support Instruct fine-tuned hugging face models. 
The hugging face pipeline is different for Instruct and pretrain only models. 

**get_model_response.py** uses the outline library to restrict the LLM output to adhere to a grammar (has been moved to old tests). 
