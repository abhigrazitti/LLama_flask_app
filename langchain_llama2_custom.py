#loading packges
from torch import cuda, bfloat16
import transformers
from transformers import StoppingCriteria, StoppingCriteriaList
import torch
from langchain.document_loaders import UnstructuredFileLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
print("loaded all packages")

device = f'cuda:{cuda.current_device()}' if cuda.is_available() else 'cpu'

print("Printing Device...")
print(device)

print("loading model....")
model_id ="meta-llama/Llama-2-13b-chat-hf"
hf_auth = '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'
model_config = transformers.AutoConfig.from_pretrained(
    model_id,
    use_auth_token=hf_auth
)

bnb_config = transformers.BitsAndBytesConfig(load_in_4bit = True,
bnb_4bit_quant_tyoe = 'nf4',
bnb_4bit_use_double_quant=True,
bnb_4bit_compute_dtype=bfloat16
)


model = transformers.AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    config=model_config,
    quantization_config=bnb_config,
    device_map='auto',
    use_auth_token=hf_auth,
    offload_folder="save_folder"
)


# Load model directly
tokenizer = transformers.AutoTokenizer.from_pretrained(model_id, use_auth_token=hf_auth)



generate_text = transformers.pipeline(
    model=model, tokenizer=tokenizer,
    return_full_text=True, 
    task='text-generation',
    temperature=0.1,  
    max_new_tokens=4096,  
    repetition_penalty=1.1 
)

print("loaded model")
llm = HuggingFacePipeline(pipeline=generate_text)



def llama2_main_function1(file):
    
    #adding custom prompts
    #custom prompt for langchain
    # combine_custom_prompt='''
    # Generate only important points of the following text that includes the following elements:

    # * Bullet points that list the key points of the text..
    # Text:`{text}`
    # '''

    combine_custom_prompt='''
    Identify and generate the most important action items for each individual in the following text, in bullet points, without repeating individual names. Only include the most salient points, and omit any supporting details or less important information.
    Text:`{text}`
    '''

    # map_custom_prompt='''
    # Write only important action items of individuals from the followling text with individuals name in bullet points if action items is not important then do not write it.:
    # TEXT:`{text}`
    # Action Items:
    # '''
    map_custom_prompt='''
    Identify and write the most important action items for each individual in the following text, in bullet points. If an action item is not important, omit it.
    TEXT:`{text}`
    Action Items:
    '''
    
    combine_prompt_template = PromptTemplate(
        template=combine_custom_prompt,
        input_variables=['text']
    )
    map_prompt_template = PromptTemplate (
        input_variables=['text'],
        template=map_custom_prompt
    )
    chain = load_summarize_chain(llm = llm,
                                chain_type="map_reduce",
                                map_prompt=map_prompt_template,
                                combine_prompt=combine_prompt_template,
                                verbose=True)

   
    sm_loader = UnstructuredFileLoader(file)
    sm_doc = sm_loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 6000,
        chunk_overlap = 400
    )
    sam_docs = text_splitter.split_documents(sm_doc)
    result = chain.run(sam_docs)
    return result


def llama2_main_function2(file):
    
    #adding custom prompts
    #custom prompt for langchain
    combine_custom_prompt='''
    Summarize the discussed items in the following text in bullet points, ignoring irrelevant discussion.
    Text:`{text}`
    '''

    map_custom_prompt='''
    Summarize the discussed items in the following meeting transcript in bullet points, ignoring irrelevant discussion.
    TEXT:`{text}`
    Discussed Items:
    '''
    
    combine_prompt_template = PromptTemplate(
        template=combine_custom_prompt,
        input_variables=['text']
    )
    map_prompt_template = PromptTemplate (
        input_variables=['text'],
        template=map_custom_prompt
    )
    chain = load_summarize_chain(llm = llm,
                                chain_type="map_reduce",
                                map_prompt=map_prompt_template,
                                combine_prompt=combine_prompt_template,
                                verbose=True)

   
    sm_loader = UnstructuredFileLoader(file)
    sm_doc = sm_loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 6000,
        chunk_overlap = 400
    )
    sam_docs = text_splitter.split_documents(sm_doc)
    result = chain.run(sam_docs)
    return result

