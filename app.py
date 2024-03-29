from flask import Flask, render_template_string, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from response import * 


app = Flask(__name__)

global  final_docs_list, uploaded, pinecone_environment, pinecone_index_name, pinecone_api_key, embeddings, unique_id

app.config['UPLOAD_FOLDER'] = "/documents" 

uploaded = False
openai.api_key = get_api(hexcode="736b2d56534975564878354d444669374b45733054704c5433426c626b464a6f4c316c7556506b696767546469465574496379")
unique_id = "aaa365fe031e4b5ab90aba54eaf6012e"

pinecone_environment = "gcp-starter"
pinecone_index_name  = "arabic-bot"
pinecone_api_key = "83ffe0ca-4d89-4d5e-9a46-75bf76d6106f"

embeddings = create_embeddings_load_data()


uploaded = False

keywords = {

"Safety contact Emergency Services Lost Items" : [ "What are the safety precautions I should take during Hajj?",
"Who should I contact in case of emergencies?",
"What emergency response services are available in Mecca and Medina?",
"What are the procedures for lost and found items and missing pilgrims?" ] ,

"Hotel Room Service book Hajj" : [ "What types of accommodation are available during Hajj?" , 
"How can I book a hotel or other suitable lodging?", 
"What amenities and services are typically provided by hotels during Hajj?" , 
"What are the regulations and protocols for hotel check-in and check-out during Hajj?"
 ] ,

" Waste Trash Clean" : [ "How can I contribute to a clean and sanitary environment during Hajj?",
"Where can I dispose of waste properly?",
"What are the environmental regulations for pilgrims?", 
"Are there initiatives to promote sustainable practices during Hajj?" ] , 

"Health Medical vaccine " : 
[ "What common health risks are associated with Hajj?" ,
"What vaccinations are required or recommended for pilgrims?",
"Where can I find medical assistance in Mecca and Medina?",
"Will my medicare cover any medical expenses incurred during Hajj?" ] , 

"Transportation" : [ "How can I get around Mecca and Medina during Hajj?" ,
"Is public transportation available?",
"Are there private transportation options?",
"What are the regulations for car rentals and hiring taxis?" ],

    "Food Water Diet" : [ "What kind of food will be available?",
"Do I need to bring my own food and water?", 
"Are there dietary restrictions in Mecca and Medina?", 
"Where can I find safe and hygienic drinking water?" ] , 

    "cars": ["What is the best car to buy?", "How to maintain your car?", "How to sell your car?"],
    "animals": ["What are some endangered animals?", "How to adopt a pet?", "How to train your dog?"],
    "sports": ["Who won the last Olympics?", "How to play soccer?", "How to improve your fitness?"]
}


@app.route("/suggestions")
def suggestions():
    # Get the term from the query string
    term = request.args.get("term")
    # Initialize an empty list for the suggestions
    suggestions = []
    # Loop through the keywords and phrases
    for keyword, phrases in keywords.items():
        # Check if the term matches or is a substring of the keyword
        if term == keyword or term in keyword:
            # Add the phrases to the suggestions list
            suggestions.extend(phrases)
    # Return the suggestions as JSON data
    return jsonify(suggestions)



@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    global messages
    if request.method == 'POST':
        if 'files' in request.files.getlist('files'):
            uploaded = False
            print("No files found")
    return  render_template("upload.html")

@app.route('/uploading', methods=['POST'])
def uploading():
    unique_id = "aaa365fe031e4b5ab90aba54eaf6012e"
    if request.method == 'POST':
       if 'files' in request.files.getlist('files'):
            files = request.files.getlist('files')
            filenames = []
            for file in files:
                print(file.filename)
                
                file.save(os.path.join( app.config['UPLOAD_FOLDER'], filename ))
    
            docs = create_docs(app.config['UPLOAD_FOLDER'] , unique_id, )
            docs_chunk = split_docs(documents, chunk_size=1000, chunk_overlap=0)
            embeddings = create_embeddings_load_data()
            push_to_pinecone(pinecone_apikey,pinecone_environment,pinecone_index_name, embeddings, docs_chunk)
            return redirect(url_for('upload_page', messages=messages, uploaded=True))


@app.route('/doc-chat', methods=['GET', 'POST'])
def doc_chat():
    global messages
    unique_id = "aaa365fe031e4b5ab90aba54eaf6012e"

    if request.method == 'POST':
        
        if 'send'  in  request.form:
            unique_id = "aaa365fe031e4b5ab90aba54eaf6012e"
            query = request.form.get('message')
            # if files : 
            #     docs = create_docs(app.config['UPLOAD_FOLDER'] , unique_id)
            #     docs_chunk = split_docs(documents, chunk_size=1000, chunk_overlap=0)
            #     final_doc_list = docs_chunk
            if len(messages) == 0 : 
                qa_chain = define_qa()
                relevant_docs = get_relevant_docs(query, embeddings, unique_id)
            else :
                relevant_docs = get_relevant_docs(query, embeddings, unique_id)
                answer = get_answer(query, qa_chain, relevant_docs)
            message = request.form.get('message')
            # messages.append({'text': message, 'sender': 'user'}) 
            messages.append({'text': f'Possible answer from document: {answer}' , 'sender': f"{message}" } )

        elif 'reset' in request.form:
            messages = []
    return render_template('chat_document.html', messages=messages)



# @app.route('/ask_anything', methods=['GET', 'POST'])
# def smart_tourist():
#     global messages
#     if request.method == 'POST':

#         if 'send'   in  request.form:
#             user_input = request.form.get('message')
#             resoponse = get_response(user_input)
#             # messages.append({'text': message, 'sender': 'user'}) 
#             messages.append({'response': f'{resoponse}' , 'sender': f"{user_input}" } )
        
#         elif 'revert' in request.form:
#             try : messages = messages[:-1]
#             except: messages = []
            
#         elif 'reset'  in request.form:
#             messages = []

#     return render_template('smart_tourist_llm.html', messages=messages)




# Use a global list for simplicity. In a real application, you'd use a database.

global messages
messages = []

@app.route('/', methods=['GET', 'POST'])
def home():
    global messages
    if request.method == 'POST':

        if 'send'   in  request.form:
            user_input = request.form.get('message')
            # resoponse = get_response(user_input)
            # messages.append({'text': message, 'sender': 'user'}) 
            messages.append({'response': f'{resoponse}' , 'sender': f"{user_input}" } )
        elif 'revert' in request.form:
            messages = messages[:-1]

        elif 'reset'  in request.form:
            messages = []

    return render_template('smart_tourist_llm.html', messages=messages)



# 
