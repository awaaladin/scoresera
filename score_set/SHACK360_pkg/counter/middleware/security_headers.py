from django.conf import settings

class SecurityHeadersMiddleware:
    """Add security-related HTTP headers to all responses.

    Headers set:
    - Content-Security-Policy (from settings.CSP_HEADER)
    - Referrer-Policy (from settings.REFERRER_POLICY)
    - Permissions-Policy (from settings.PERMISSIONS_POLICY)
    - X-Content-Type-Options (nosniff)
    - X-Frame-Options (from settings.X_FRAME_OPTIONS)
    """

    def process_response(self, request, response):
        # Content Security Policy
        csp = getattr(settings, 'CSP_HEADER', None)
        if csp:
            response['Content-Security-Policy'] = csp

        # Referrer Policy
        refp = getattr(settings, 'REFERRER_POLICY', None)
        if refp:
            response['Referrer-Policy'] = refp

        # Permissions Policy
        perms = getattr(settings, 'PERMISSIONS_POLICY', None)
        if perms:
            response['Permissions-Policy'] = perms

        # Ensure X-Content-Type-Options
        if not response.get('X-Content-Type-Options'):
            response['X-Content-Type-Options'] = 'nosniff'

        # Ensure X-Frame-Options (honour existing setting)
        xfo = getattr(settings, 'X_FRAME_OPTIONS', None)
        if xfo and not response.get('X-Frame-Options'):
            response['X-Frame-Options'] = xfo

        return response
