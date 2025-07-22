from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    
    def ready(self):
        from .patch_ckeditor import patch_ckeditor_upload # UPD -- using that patch to ckeditor upload view
        patch_ckeditor_upload()

        from .keepalive import djKeepAlive
        if djKeepAlive.enabled:
            def delayed_start():
                import time
                time.sleep(90)
                djKeepAlive.start()
            
            import threading
            thread = threading.Thread(target=delayed_start, daemon=True)
            thread.start()