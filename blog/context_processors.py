from django.db.models import Count
from blog.models import Tag, Post

def navigation_tags(request):
    """adds nav tags n sidebar tags to every req context"""
    try:
        tags = Tag.objects.all().annotate(post_count=Count('posts')).order_by('-post_count')
        num_of_tags_on_header_nav_bar = 4
        nav_tags = tags[:num_of_tags_on_header_nav_bar] # NAVBAR gonna have X most popular tags on it / twitterish
        
        for tag in tags: # all tags MUST have slugs
            if not hasattr(tag, 'slug') or not tag.slug:
                from django.utils.text import slugify
                tag.temp_slug = slugify(tag.name)
            else:
                tag.temp_slug = tag.slug

        # for pending summaries
        admin_context = {}
        if request.user.is_authenticated and request.user.is_staff:
            pndSmrs = Post.objects.filter(needs_summary_update=True,is_repost=False).count()
            admin_context['pending_summaries'] = pndSmrs

        return {'nav_tags': nav_tags,'tags': tags,**admin_context}
    except Exception as e: # ERROR HANDLING -- return empty list
        print(f"error in navigation_tags: {e}")
        return {'nav_tags': [], 'tags': []}