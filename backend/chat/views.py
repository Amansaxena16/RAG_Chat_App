from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from implementations.answer import answer_question

class AskLLM(APIView):

    def post(self, request):
        question = request.data.get('question')
        if not question:
            return Response({'error': 'Could not find Question'}, status=status.HTTP_400_BAD_REQUEST)

        history = request.data.get('history', [])

        answer, docs = answer_question(question, history)

        history.append({'role': 'user', 'content': question})
        history.append({'role': 'assistant', 'content': answer})

        sources = [
            {'content': d.page_content, 'doc_type': d.metadata.get('doc_type')}
            for d in docs
        ]

        return Response(
            {'answer': answer, 'sources': sources, 'history': history},
            status=status.HTTP_200_OK,
        )