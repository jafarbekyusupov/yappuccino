from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)

@register.inclusion_tag('blog/includes/tag_badge.html')
def render_tag(tag):
	return {'tag': tag}


@register.filter
def truncate_content(content, max_length=200):
	""" sentence/space break, adds '...' if needed """

	if not content: return ""

	if len(content) <= max_length: return content # no need for truncatino

	# UPD -- finding good breaking point FIRST - endl or space are in higer priority
	truncated = content[:max_length]
	break_point = max(
		truncated.rfind('. '),
		truncated.rfind('! '),
		truncated.rfind('? '),
		truncated.rfind('\n'),
		truncated.rfind(' ')
	)

	# truncated = content[:break_point+1] if break_point>max_length*0.7 else content[:max_length].rsplit(' ', 1)[0]
	if break_point > max_length*0.7:
		truncated = content[:break_point + 1]
	else:
		truncated = content[:max_length].rsplit(' ', 1)[0]  # breaking at last whole wrd

	return truncated + '...'


@register.filter
def truncate_words(content, max_words=30):
	"""
	trunc-te txt to max num of words
	second element in return tuple -- bool indicating if truncation occurred
  """
	if not content:
		return "", False

	words = content.split()

	if len(words) <= max_words: return content, False

	truncated_words = words[:max_words]

	# add ellipis
	result = ' '.join(truncated_words)

	# trying to end at sentence if possible → looking for ending marks
	last_sentence_end = max(
		result.rfind('. '),
		result.rfind('! '),
		result.rfind('? ')
	)

	if last_sentence_end > len(result) * 0.7:
		result = result[:last_sentence_end + 1]

	return result + '...', True