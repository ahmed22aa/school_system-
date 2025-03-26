from celery import shared_task
from django.core.files.base import ContentFile
from .models import Lesson
import whisper
import uuid


model = whisper.load_model("base")

@shared_task
def add_numbers(x, y):
    return x + y


@shared_task
def speech_rec(lesson_id):
    lesson_ = Lesson.objects.get(pk=lesson_id)
    result = model.transcribe(lesson_.file_audio.path)
    txt = result["text"]
    filename = f"{uuid.uuid4().hex}.txt"
    text_file = ContentFile(txt.encode('utf-8'))
    lesson_.audio_file_transcribe.save(filename, text_file)
    lesson_.save()
    return lesson_.audio_file_transcribe.name