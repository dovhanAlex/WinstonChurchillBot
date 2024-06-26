# -*- coding: utf-8 -*-
"""streamlit_app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/17XtiJaynoIj7I4cpf_4Ch4VcjXeaf1zV
"""

# !pip3 install transformers datasets peft bitsandbytes streamlit

import os

import torch
import streamlit as st

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)
from peft import PeftConfig, PeftModel

from dotenv import load_dotenv

load_dotenv()

os.environ['HF_TOKEN'] = os.getenv("HUGGINGFACEHUB_API_TOKEN")

checkpoint = 'OleksiiVNTU/task_fine_tuning_Mistral_7b_v0.1_CLM'

config = PeftConfig.from_pretrained(checkpoint)

model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path,
                                             quantization_config=BitsAndBytesConfig(load_in_4bit=True,
                                                                                    bnb_4bit_compute_dtype=torch.bfloat16,
                                                                                    bnb_4bit_quant_type="nf4"
                                                                                    ),
                                             torch_dtype=torch.bfloat16,
                                             )

tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)

lora_model = PeftModel.from_pretrained(model, checkpoint)


def get_str_input(query):
    with torch.no_grad():
        output = lora_model.generate(tokenizer(query)['input_ids'],
                                     pad_token_id=tokenizer.pad_token_id)

    yield tokenizer.batch_decode(output)[0]


st.title('Winston Churchill Bot')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        for m in st.session_state.messages:
            stream = get_str_input(m['content'])
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})