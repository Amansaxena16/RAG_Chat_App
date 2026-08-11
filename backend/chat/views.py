from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from implementations.answer import call_llm

class AskLLM(APIView):
    
    def post(self, request):
        question = request.data.get('question')
        if not question:
            return Response({'error': 'Could not find Question'}, status=status.HTTP_400_BAD_REQUEST)
        
        response = call_llm(question)
        return Response({'response': response},status=status.HTTP_200_OK)