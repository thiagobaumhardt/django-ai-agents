from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
import openai
import time

@login_required
def agent_chat_view(request, agent_slug):
    agent_config = settings.AGENTS_CONFIG.get(agent_slug)
    
    if not agent_config:
        raise Http404("Agente não encontrado.")

    openai.api_key = agent_config["api_key"]
    assistant_id = agent_config["assistant_id"]
    template = agent_config["template"]
    agent_name = agent_slug  # Ou coloque um campo "name" se quiser um nome mais bonito

    response_text = None

    if request.method == "POST":
        user_message = request.POST.get("message")

        if user_message:
            # Criar uma thread
            thread = openai.beta.threads.create()

            # Adicionar a mensagem do usuário
            openai.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message,
            )

            # Criar o run
            run = openai.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id,
            )

            # Esperar o run finalizar
            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id,
                )
                if run_status.status == "completed":
                    break
                elif run_status.status in ["failed", "cancelled", "expired"]:
                    response_text = "Erro ao processar a resposta."
                    break
                time.sleep(1)

            # Pegar a última resposta da thread
            messages = openai.beta.threads.messages.list(thread_id=thread.id)
            response_parts = []
            for msg in messages.data:
                if msg.role == "assistant":
                    for content in msg.content:
                        if content.type == "text":
                            response_parts.append(content.text.value)

            response_text = "\n".join(response_parts)

    context = {
        "agent_slug": agent_slug,
        "agent_name": agent_name,
        "response": response_text,
    }

    return render(request, template, context)


def home_redirect_view(request):
    if request.user.is_authenticated:
        return redirect('menu')
    else:
        return redirect('login')
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email not in settings.ALLOWED_EMAILS:
            messages.error(request, 'Email não autorizado.')
            return redirect('login')

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('menu')
        else:
            messages.error(request, 'Credenciais inválidas.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # ✅ Verificar se o e-mail é permitido
        if email not in settings.ALLOWED_EMAILS:
            messages.error(request, 'Email não autorizado.')
            return redirect('register')

        # ✅ Verificar se o usuário já existe
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Usuário já existe.')
            return redirect('register')

        # ✅ Criar usuário
        user = User.objects.create_user(username=email, email=email, password=password)
        messages.success(request, 'Cadastro realizado com sucesso.')
        return redirect('login')

    return render(request, 'register.html')

def forgot_password_view(request):
    return render(request, 'forgot_password.html')

@login_required
def menu_view(request):
    user_email = request.user.username
    agents = settings.USER_AGENT_ACCESS.get(user_email, [])
    return render(request, 'menu.html', {"agents": agents})
