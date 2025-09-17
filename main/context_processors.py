# main/context_processors.py

def theme_processor(request):
    """
    Injects the user's theme preference into the context of every template.
    """
    if request.user.is_authenticated:
        theme = request.user.profile.theme
    else:
        # Default theme for logged-out users
        theme = 'dark'
        
    return {'theme': theme}