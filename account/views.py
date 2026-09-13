from django.shortcuts import render
import base64
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from .models import *
import face_recognition



# Create your views here.
@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        face_image_data = request.POST.get('face_image')
        face_image_data = face_image_data.split(',')[1]  # Remove the data URL prefix
        face_image = ContentFile(base64.b64decode(face_image_data), name=f"{username}.jpg")

        try:
            user = User.objects.create_user(username=username)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Username already exists.'})

        UserImages.objects.create(user=user, face_image=face_image)
        return JsonResponse({'status': 'success', 'message': 'User registered successfully.'})
    return render(request, 'register.html')
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        face_image_data = request.POST['face_image']

        # Get the user by username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'})

        # Convert base64 image data to a file
        face_image_data = face_image_data.split(",")[1]
        uploaded_image = ContentFile(base64.b64decode(face_image_data), name=f'{username}_face.jpg')

        # Compare the uploaded face image with the stored face image
        uploaded_face_image = face_recognition.load_image_file(uploaded_image)
        uploaded_face_encoding = face_recognition.face_encodings(uploaded_face_image)

        if uploaded_face_encoding:
             
             uploaded_face_encoding = uploaded_face_encoding[0]
             user_image = UserImages.objects.filter(user = user).first()
             stored_face_image = face_recognition.load_image_file(user_image.face_image.path)
             stored_face_encoding = face_recognition.face_encodings(stored_face_image)[0]

             print(stored_face_image,stored_face_encoding)
            # Compare the faces
             match = face_recognition.compare_faces([stored_face_encoding], uploaded_face_encoding)
             if match[0]:
                return JsonResponse({'status': 'success', 'message': 'Login successful!'})
             else:
                return JsonResponse({'status': 'error', 'message': 'Face recognition failed.'})

        return JsonResponse({'status': 'error', 'message': 'No face detected in the image.'})

    return render(request, 'login.html')