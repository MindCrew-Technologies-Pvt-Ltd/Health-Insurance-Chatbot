from django.shortcuts import render
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from collections import deque
from .getContent import extrctContent
import re
import random

def process_message_by_pdf(question,content):
        pdf_temp='''you have to act like a simple ai chatbot.
            i am providing content which is related to medical insurance:-
                    content= '{content}'
            -----------------------
            Please review all the provided content and check if any of it matches the question. If there is
            relevant content, please provide a detailed response based on the precise information found in the content.
            -----------------------
                    question = '{question}'
           If there is a match of at least '0.01%' between the question and the content, please provide
           the complete answer using only the information present in the provided content. 
           ---------------------------------------------------------
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

        pattern = r'(\d+[A-Za-z]*)'

        found_number = None
        user_input = user_input.lower()
        if user_input in greetings:
            bot_response = random.choice(responses) 
        else:
            for text in user_input_lst[::-1]:
                match = re.search(pattern, text)
                if match:
                    found_number = match.group()
                    break
            if found_number:
                content = extrctContent(found_number)
                if content != None:
                    process_message_by_pdf(user_input, content)
                    bot_response = process_message_by_pdf(user_input, content)
                else:
                    bot_response = f"Sorry ! there are no policies as per given policy / insurance number {found_number}"
            elif 'newdata' in user_input:
                content = extrctContent('newdata')
                if content != None:
                    process_message_by_pdf(user_input, content)
                    bot_response = process_message_by_pdf(user_input, content)    
            
            else:
                bot_response = "Please provide insurance number or policy number to proceed further!"
        
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



