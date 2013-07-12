"""Checkouts application middleware"""

import logging
import time

logger = logging.getLogger('analytics')

class Analytics():
    """Tracks request details useful for analysis of usage patterns.
    
    To ensure that the name of the logged in user can be accessed, this
    middleware should come after Django's built-in AuthenticationMiddleware
    in the project settings.
    """
    
    def collect_request_details(self, request):
        """Gathers information of interest from the request and returns a dictionary."""
        context = {
            'ip':        request.META['REMOTE_ADDR'],
            'method':    request.method,
            'path':      request.path,
        }
        
        try:
            context['useragent'] = request.META['HTTP_USER_AGENT']
        except KeyError:
            context['useragent'] = 'None'
        
        if hasattr(request, 'user') and request.user.is_authenticated():
            context['user'] = request.user.username
        else:
            context['user'] = 'anonymous'
        
        return context
    
    def process_request(self, request):
        """Captures the current time and saves it to the request object."""
        request._analytics_start_time = time.time()
    
    def process_response(self, request, response):
        """Organizes info from each request/response and saves it to a log."""
        context = self.collect_request_details(request)
        context['status'] = response.status_code
        context['bytes'] = len(response.content)
        
        if hasattr(request, '_analytics_start_time'):
            elapsed = (time.time() - request._analytics_start_time) * 1000.0
            context['elapsed'] = elapsed
        else:
            context['elapsed'] = -1.0
        
        template = "client=%(user)s@%(ip)s method=%(method)s path=%(path)s real=%(elapsed).0fms status=%(status)s bytes=%(bytes)s useragent=\"%(useragent)s\""
        logger.info(template % context)
        
        return response
