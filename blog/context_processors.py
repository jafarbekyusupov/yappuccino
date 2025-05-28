from django.db.models import Count
from blog.models import Tag

def navigation_tags(request):
	""" adds nav tags n sidebar tags to every req context """
	try:
		# popular tags
		tags = Tag.objects.all().annotate(
			post_count=Count('posts')
		).order_by('-post_count')

		num_of_tags_on_header_nav_bar = 4 # adujsttable number

		nav_tags = tags[:num_of_tags_on_header_nav_bar] # NAVBAR gonna have X most popular tags on it / twitterish

		# all tags MUST have slugs
		for tag in tags:
			if not hasattr(tag, 'slug') or not tag.slug:
				from django.utils.text import slugify
				tag.temp_slug = slugify(tag.name)
			else:
				tag.temp_slug = tag.slug

		return {
			'nav_tags': nav_tags,
			'tags': tags  # adding all tags to cntxt
		}
	except Exception as e:
		# ERROR HANDLING -- return empty list
		print(f"Error in navigation_tags: {e}")
		return {'nav_tags': [], 'tags': []}