from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    
    def ready(self):
        from .patch_ckeditor import patch_ckeditor_upload # UPD -- using that patch to ckeditor upload view
        patch_ckeditor_upload()

        print("=== dj apps.py ready() called ===")
        from .keepalive import djKeepAlive
        print(f"keepalive enabled: {djKeepAlive.enabled}")
        if djKeepAlive.enabled:
            def delayed_start():
                import time
                print("keepalive -- waiting 90 secs before starting...")
                time.sleep(90)
                print("keepalive -- starting now!")
                djKeepAlive.start()
            
            import threading
            thread = threading.Thread(target=delayed_start, daemon=True)
            thread.start()
            print("| OK | keepalive -- delayed start thread created")
        else:
            print("| ERR | keepalive -- DISABLED → NOT STARTINGGGGG")