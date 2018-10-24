from django.shortcuts import render
from django.utils import timezone
from .models import Post
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud.tone_analyzer_v3 import ToneInput
from watson_developer_cloud import LanguageTranslatorV3
from watson_developer_cloud import LanguageTranslatorV3


service = ToneAnalyzerV3(
    ## url is optional, and defaults to the URL below. Use the correct URL for your region.
    # url='https://gateway.watsonplatform.net/tone-analyzer/api',
    username='c1696fbf-851a-4ddd-8810-90e9da6073ce',
    password='kPEKxmiYJ512',
    version='2017-09-26')

language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    iam_apikey='fSq7c74bPa4WAQceJ7c0iUWCMLN8vo36hLTVo49SzUhp',
   # url='https://gateway.watsonplatform.net/language-translator/api'
)


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

    for post in posts:
        posting = post.text
        translation = language_translator.translate(
            text= post.text, model_id='en-es').get_result()
        obj = (json.dumps(translation, indent=2, ensure_ascii=False))
        print(obj)
        obj2 = json.loads(obj)
        post.obj2 = obj2['translations'][0]['translation']
        post.w_count = obj2['word_count']
        post.c_count = obj2['character_count']

        tone_input = ToneInput(post.text)
        tone = service.tone(tone_input=tone_input, content_type="application/json")
        tone2 = str(tone)

        tone2_data = json.loads(tone2)
        tone_result = tone2_data['result'].get('document_tone').get('tones')
        #print('tone_result..result...', tone_result)
        tone_name = 'None'
        tone_score = 0
        for tone_id in tone_result:
            tone_name = tone_id.get('tone_name')
            tone_score = tone_id.get('score')

        print('tone_name..result...', tone_name)
        print('tone_score result---', tone_score)
        post.tone_name = tone_name
        post.tone_score = tone_score
        post.tone3 = (tone2[1:500])

        print(post.tone3)

    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
        return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
        return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

