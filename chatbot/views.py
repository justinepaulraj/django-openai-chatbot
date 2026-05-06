import openai
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.conf import settings
from .forms import SignUpForm
from .models import Conversation, Message

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
    conversation_id = request.session.get("conversation_id")
    conversation = None

    if conversation_id:
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        except Conversation.DoesNotExist:
            conversation = None

    if not conversation:
        conversation = Conversation.objects.create(
            user=request.user,
            type="normal",
            title=f"Conversation {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    request.session["conversation_id"] = conversation.id
    messages = conversation.messages.all()

    if request.method == "POST":
        user_input = request.POST.get("user_question", "").strip()

        if user_input:
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

        return redirect("chat")

    return render(request, "chatbot/chat.html", {
        "messages": messages,
        "current_conversation": conversation
    })