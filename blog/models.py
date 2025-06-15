from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
import bleach
from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.utils.html import mark_safe


class Tag(models.Model):
	name = models.CharField(max_length=50, unique=True)
	slug = models.SlugField(max_length=50, unique=True, blank=True)

	def save(self, *args, **kwargs):
		# if thats an existing tag
		if self.pk:
			try: # -- get old version from DB
				old_tag = Tag.objects.get(pk=self.pk)

				# if slug is changing → create alias
				if old_tag.slug != slugify(self.name) and old_tag.slug:
					TagAlias.objects.get_or_create(tag=self, alias=old_tag.slug)
			except Tag.DoesNotExist:
				pass

		# else → GENERATE NEW SLUG
		self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('tag-detail', kwargs={'slug': self.slug})


class TagAlias(models.Model):
	""" PURPOSE -- store old slugs for tags to maintain url consistency """
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='aliases')
	alias = models.SlugField(unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.alias} → {self.tag.name}" # alt + 26

	class Meta:
		verbose_name_plural = "Tag Aliases"


class Post(models.Model):
	title = models.CharField(
		max_length=50,
		validators=[MaxLengthValidator(50)]
	)
	content = CKEditor5Field('Content', config_name='default')
	date_posted = models.DateTimeField(default=timezone.now)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
	view_count = models.PositiveIntegerField(default=0)

	summary = models.TextField(blank=True, null=True, help_text="AI-generated summary")
	summary_generated_at = models.DateTimeField(blank=True, null=True)
	needs_summary_update = models.BooleanField(default=True)
	summary_model_version = models.CharField(max_length=50, blank=True, null=True)

	# UPD -- REPOST mechanics
	original_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reposts')
	is_repost = models.BooleanField(default=False)

	def __str__(self):
		return self.title

	def get_absolute_url(self): return reverse('post-detail', kwargs={'pk': self.pk})

	@property
	def upvotes(self): return self.votes.filter(vote_type=Vote.UPVOTE).count()

	@property
	def downvotes(self): return self.votes.filter(vote_type=Vote.DOWNVOTE).count()

	@property
	def score(self): return self.upvotes - self.downvotes

	@property
	def comments_count(self): 
		return self.comments.count()

	@property
	def reposts_count(self): 
		return self.reposts.count()

	@property
	def word_count(self):
		import re
		clean_txt = re.sub(r'<[^>]+>', '', self.content)
		return len(clean_txt.split())

	@property
	def has_summary(self):
		return bool(self.summary and self.summary.strip())

	def get_safe_content(self):
		try:
			return bleach.clean(
				self.content,
				tags = settings.BLEACH_ALLOWED_TAGS,
				attributes = settings.BLEACH_ALLOWED_ATTRIBUTES,
				css = settings.BLEACH_ALLOWED_STYLES,
				strip=True
			)
		except TypeError:
			return bleach.clean(
				self.content,
				tags = settings.BLEACH_ALLOWED_TAGS,
				attributes = settings.BLEACH_ALLOWED_ATTRIBUTES,
				strip=True
			)

	def clean(self):
		from django.core.exceptions import ValidationError
		if self.title and len(set(self.title)) < 3:
			raise ValidationError('Title must have more variety of characters.')

	def save(self, *args, **kwargs):
		if self.pk:
			try:
				old_post = Post.objects.get(pk=self.pk)
				if old_post.content != self.content:
					self.needs_summary_update = True
			except Post.DoesNotExist: pass
		else: self.needs_summary_update = True # new post → always needs summary update
		super().save(*args, **kwargs)

class Vote(models.Model):
	UPVOTE = 'upvote'
	DOWNVOTE = 'downvote'
	VOTE_TYPES = [
		(UPVOTE, 'Upvote'),
		(DOWNVOTE, 'Downvote'),
	]

	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	vote_type = models.CharField(max_length=10, choices=VOTE_TYPES)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('post', 'user')

	def __str__(self):
		return f"{self.user.username}'s {self.vote_type} on {self.post.title}"


class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	content = CKEditor5Field('Content', config_name='basic')
	date_posted = models.DateTimeField(default=timezone.now)
	parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
	is_edited = models.BooleanField(default=False)
	edited_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ['-date_posted']

	def __str__(self):
		return f"Comment by {self.author.username} on {self.post.title}"

	def get_safe_content(self):
		"""
		return -- safe rendered comment contet -- html sanitzation, consistent output for all comment levels
		"""
		if not self.content:
			return mark_safe("<p></p>")  # empty par

		cleaned = bleach.clean(
			self.content,
			tags=settings.BLEACH_ALLOWED_TAGS,
			attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
			strip=True
		)

		# at least paragraph tags for proper rendering
		if not cleaned.startswith('<p>'):
			cleaned = f'<p>{cleaned}</p>'

		return mark_safe(cleaned)
	# def get_safe_content(self):
	# 	return bleach.clean(
	# 		self.content,
	# 		tags=settings.BLEACH_ALLOWED_TAGS,
	# 		attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
	# 		strip=True
	# 	)

	@property
	def upvotes(self):
		return self.votes.filter(vote_type='up').count()

	@property
	def downvotes(self):
		return self.votes.filter(vote_type='down').count()

	def save(self, *args, **kwargs):
		if self.pk:  # upd existing comment
			self.is_edited = True
			self.edited_at = timezone.now()
		super().save(*args, **kwargs)


class CommentVote(models.Model):
	UP = 'up'
	DOWN = 'down'
	VOTE_TYPES = [
		(UP, 'Upvote'),
		(DOWN, 'Downvote'),
	]

	comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	vote_type = models.CharField(max_length=4, choices=VOTE_TYPES)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('comment', 'user')

	def __str__(self):
		return f"{self.user.username}'s {self.vote_type} on comment"