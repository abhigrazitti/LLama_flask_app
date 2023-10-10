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
print("loaded all packages")

#main function
def llama2_main_function(file):

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
    
    
    #adding custom prompts
    #custom prompt for langchain
    combine_custom_prompt='''
    Generate only important points of the following text that includes the following elements:

    * Bullet points that list the key points of the text..
    Text:`{text}`
    '''

    map_custom_prompt='''
    Write only important action items of individuals from the followling text in bullet points if action items is not important then do not write it.:
    TEXT:`{text}`
    Action Items:
    '''


    llm = HuggingFacePipeline(pipeline=generate_text)
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



    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 6000,
        chunk_overlap = 400
    )

    sam_docs = text_splitter.split_documents(sm_doc)

    result = chain.run(sam_docs)

    return result

