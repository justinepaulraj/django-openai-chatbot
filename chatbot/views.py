import os
import tempfile
import openai
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.views.decorators.http import require_POST
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from .forms import SignUpForm
from .models import Conversation, Message, Document

VECTORSTORE_DIR = os.path.join(settings.BASE_DIR, "vectorstores")

def get_vectorstore(doc):
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    store_path = os.path.join(VECTORSTORE_DIR, str(doc.id))
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)

    if os.path.exists(store_path):
        return Chroma(persist_directory=store_path, embedding_function=embeddings)
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            for chunk in doc.file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(texts, embeddings, persist_directory=store_path)
        os.unlink(tmp_path)
        return vectorstore
    
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("chat")
    else:
        form = SignUpForm()
    return render(request, "chatbot/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("chat")
    else:
        form = AuthenticationForm()
    return render(request, "chatbot/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def chat_view(request):
    conversation_id = request.GET.get("conversation_id") or request.session.get("conversation_id")
    conversation = None

    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        except Conversation.DoesNotExist:
            conversation = None

    messages = conversation.messages.all() if conversation else []

    if request.method == "POST":
        user_input = request.POST.get("user_question", "").strip()
        doc_file = request.FILES.get("document_file")

        if user_input or doc_file:
            if not conversation:
                conversation = Conversation.objects.create(
                    user=request.user,
                    type="normal",
                    title="New Conversation"
                )
                request.session["conversation_id"] = conversation.id

            if doc_file and not user_input:
                doc = Document.objects.create(user=request.user, file=doc_file)
                conversation.document = doc
                conversation.type = "doc"
                conversation.save()

                vectorstore = get_vectorstore(doc)
                retriever = vectorstore.as_retriever()
                docs = retriever.invoke("Provide a short summary of this document.")
                context = "\n\n".join([d.page_content for d in docs])

                llm = ChatOpenAI(temperature=0, api_key=settings.OPENAI_API_KEY)
                summary = llm.invoke(f"Summarize this document:\n\n{context}").content
                Message.objects.create(conversation=conversation, role="assistant", content=summary)

            elif doc_file and user_input:
                doc = Document.objects.create(user=request.user, file=doc_file)
                conversation.document = doc
                conversation.type = "mixed"
                conversation.save()

                Message.objects.create(conversation=conversation, role="user", content=user_input)

                vectorstore = get_vectorstore(doc)
                retriever = vectorstore.as_retriever()
                docs = retriever.invoke(user_input)
                context = "\n\n".join([d.page_content for d in docs])

                llm = ChatOpenAI(temperature=0, api_key=settings.OPENAI_API_KEY)
                answer = llm.invoke(f"Answer based on this document:\n\n{context}\n\nQuestion: {user_input}").content
                Message.objects.create(conversation=conversation, role="assistant", content=answer)

            else:
                Message.objects.create(conversation=conversation, role="user", content=user_input)

                chat_history = [{"role": msg.role, "content": msg.content} for msg in messages]
                chat_history.append({"role": "user", "content": user_input})

                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=chat_history,
                    temperature=0.7
                )
                assistant_reply = response.choices[0].message.content.strip()
                Message.objects.create(conversation=conversation, role="assistant", content=assistant_reply)

            last_n_msgs = conversation.messages.order_by('-id')[:1]
            if last_n_msgs.exists():
                max_chars_per_msg = 50
                titles = []
                for msg in reversed(list(last_n_msgs)):
                    text = msg.content.replace("\n", " ")
                    if len(text) > max_chars_per_msg:
                        text = text[:max_chars_per_msg] + "…"
                    titles.append(text)
                conversation.title = " | ".join(titles)
                conversation.save()

        return redirect("chat")

    conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "chatbot/chat.html", {
        "messages": messages,
        "conversations": conversations,
        "current_conversation": conversation
    })

@login_required
@require_POST
def new_conversation(request):
    request.session["conversation_id"] = None
    if request.headers.get("HX-Request"):
        response = HttpResponse()
        response["HX-Redirect"] = reverse('chat')
        return response
    return redirect("chat")

@login_required
@require_POST
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.delete()
    remaining = Conversation.objects.filter(user=request.user).order_by("-created_at")

    current_convo_id = request.session.get("conversation_id")
    if str(conversation_id) == str(current_convo_id):
        if remaining.exists():
            request.session["conversation_id"] = remaining.first().id
        else:
            new_convo = Conversation.objects.create(
                user=request.user,
                type="normal",
                title="New Conversation"
            )
            request.session["conversation_id"] = new_convo.id

    if request.headers.get("HX-Request"):
        response = HttpResponse()
        response["HX-Redirect"] = f"{reverse('chat')}?conversation_id={request.session['conversation_id']}"
        return response
    return redirect("chat")