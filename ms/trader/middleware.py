import cProfile
import pstats
import io
from django.http import HttpResponse

class cProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'profile' in request.GET:
            prof = cProfile.Profile()
            prof.enable()
            response = self.get_response(request)

            prof.disable()

            s = io.StringIO()

            ps = pstats.Stats(prof, stream=s).sort_stats('cumulative')

            ps.print_stats(25)
            print("="*50)
            print(f"cProfile results for: {request.path}")
            print("="*50)
            print(s.getvalue())
            print("="*50)

        else:
      
            response = self.get_response(request)
            
        return response