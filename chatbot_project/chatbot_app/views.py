from django.shortcuts import render
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from collections import deque
import random

def get_ans(question):
    import os
    import PyPDF2
    import textwrap

    target_pdf_name = "//home//ubuntu//pdf//newdata.pdf"
    content=''
    with open(target_pdf_name, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            content += page.extract_text() + " "        
            paragraphs = content.split('\n\n')
    wrapped_paragraphs = [textwrap.fill(paragraph, width=1000) for paragraph in paragraphs]

    content = '\n\n'.join(wrapped_paragraphs)   



    pdf_temp='''you have to act like a simple ai chatbot and reply to basic conversational messages.
        here i am providing the content which is related to medical insurance:-
                content= '{content}'
        -----------------------
        Please review all the provided content and check if any of it matches the question. If there is
        relevant content, please provide response based on the precise information found in the content.
        -----------------------
                question = '{question}'
       please provide the complete answer using only the information present in the provided content. 
       ---------------------------------------------------------
       things the chatbot should avoid in response :-
                    Do not include any references to the content, title, question, or subheadings such as :-
                    "The answer to the question" , "As a chatbot, I would respond, According to the content, from provided content . or any kind of word that gives reference to the content."
               '''
    try:
        pdf_prompt=PromptTemplate(input_variables=['question','content'],
                            template=pdf_temp)
        llm=ChatOpenAI(openai_api_key="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",model_name='gpt-3.5-turbo-16k')
        chain=LLMChain(llm=llm,prompt=pdf_prompt)
        ans=chain.run({"question":question,'content':content})
        
        return ans
    except Exception as e:
        return None

def home(request):
    user_input = ''
    bot_response = ''
    context_chat_history=[]
    chat_history = request.session.get('chat_history', [])
    greetings = ["hello", "hi", "hey", "good morning", "good afternoon"]
    responses = ["Hello!", "Hi there!", "Hey!", "How can I help you today?","Hello! I am here to assist you","Hello! How can i help you"]

    user_input_lst = [message["message"] for message in chat_history if message["type"] == "user"]
    if request.method == "POST":
        user_input = request.POST.get("user_input", '').strip()        
        chat_history.append({"type": "user", "message": user_input})
        user_input_lst.append(user_input)

        if user_input in greetings:
            bot_response = random.choice(responses)
        else:
            bot_response=get_ans(user_input)
             
        chat_history.append({"type": "bot", "message": bot_response})
        context_chat_history = list(deque(chat_history, maxlen=10))
        request.session['chat_history'] = chat_history
    elif request.method == "GET":
        request.session['chat_history'] = []

    context = {
        "user_input": user_input,
        "bot_response": bot_response,
        "chat_history": context_chat_history,
    }
    return render(request, 'home.html', context)



