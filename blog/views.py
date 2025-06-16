# ==== CORE ====
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import (HttpResponseForbidden, HttpResponseRedirect,JsonResponse,)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.db import transaction
from django.db.utils import IntegrityError
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from blogpost.settings import BLEACH_ALLOWED_ATTRIBUTES, BLEACH_ALLOWED_TAGS

# === MODELS ===
from .models import Comment, CommentVote, Post, Tag, TagAlias, Vote

# === DATABASE ===
from django.db.models import Case, Count, F, IntegerField, Q, Sum, When

# auth & permissions
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User

# forms n messages
from .forms import CommentForm, PostForm, TagForm
from django.contrib import messages
#other
import bleach

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

def home(request):
	context = {
		'posts': Post.objects.all(),
    # 'title': 'Home Page',
	}
	return render(request, 'blog/home.html', context)


@login_required
def settings(request):
	if request.method == 'POST':
		# privacy settings
		if 'privacy_submit' in request.POST:
			profile = request.user.profile
			profile.show_email = 'show_email' in request.POST
			profile.show_activity = 'show_activity' in request.POST
			profile.save()
			messages.success(request, 'Privacy settings updated successfully!')
			return redirect('settings')

		# notif settings
		elif 'notification_submit' in request.POST:
			profile = request.user.profile
			profile.email_comments = 'email_comments' in request.POST
			profile.email_replies = 'email_replies' in request.POST
			profile.email_reposts = 'email_reposts' in request.POST
			profile.email_newsletter = 'email_newsletter' in request.POST
			profile.save()
			messages.success(request, 'Notification settings updated successfully!')
			return redirect('settings')

		# account deletion
		elif 'delete_account' in request.POST:
			user = request.user
			user.delete()
			messages.success(request, 'Your account has been deleted.')
			return redirect('blog-home')

	return render(request, 'users/settings.html')

class PostListView(ListView):
	model = Post
	template_name = 'blog/home.html'
	context_object_name = 'posts'
	ordering = ['-date_posted']
	paginate_by = 5

	def get(self, request, *args, **kwargs):  # UPD -- to support both OLD AND NEW Tag URLs
		# FOR BETTE READABILITY → CODE WIT MORE VARS -- APPARENTLY SOME FOLKS CANT READ TERNARY OP-R TOO LOL /_-_\
		# if request.GET.get('tag'):
		#     tag = Tag.objects.filter(Q(slug=request.GET.get('tag')) | Q(name=request.GET.get('tag'))).first()
		#     if not tag:
		#         tag = TagAlias.objects.filter(alias=request.GET.get('tag')).first().tag if TagAlias.objects.filter(alias=request.GET.get('tag')).first() else None
		#     if tag:
		#         return redirect('tag-detail', slug=tag.slug)
		# return super().get(request, *args, **kwargs)

		# if using old style tag parameter
		tag_param = request.GET.get('tag')
		if tag_param:
			# try finding tag by slug || name
			tag = Tag.objects.filter(Q(slug=tag_param) | Q(name=tag_param)).first()

			if not tag: # not found => check aliases
				alias = TagAlias.objects.filter(alias=tag_param).first()
				if alias:
					tag = alias.tag

			if tag: # found => redirect to X tag page
				return redirect('tag-detail', slug=tag.slug)

		return super().get(request, *args, **kwargs)

	def get_queryset(self):
		queryset = super().get_queryset()

		queryset = queryset.annotate(
			# score = up - down votes (where num of up is +, while num of down is -)
			vote_score=Sum(
				Case(
					When(votes__vote_type='upvote', then=1),
					When(votes__vote_type='downvote', then=-1),
					default=0,
					output_field=IntegerField()
				)
			),

			comment_count=Count('comments', distinct=True),
			popularity_score=F('view_count') + F('vote_score') + F('comment_count') * 2
		)

		# by tag if provided
		tag_name = self.request.GET.get('tag')
		if tag_name:
			# same mechanic as in get()
			tag_filter = Q(name=tag_name) | Q(slug=tag_name)
			tag = Tag.objects.filter(tag_filter).first()
			if tag:
				queryset = queryset.filter(tags=tag)

		# ------- SEARCH MECHANICS ------- #
		search = self.request.GET.get('search')
		if search:
			queryset = queryset.filter(
				Q(title__icontains=search) |
				Q(content__icontains=search) |
				Q(author__username__icontains=search)
			).distinct()

			# annotate with relevance score
			# TODO -- use postgresqls full txt search for better results
			queryset = queryset.annotate(
				relevance_score=Count(
					Case(
						When(title__icontains=search, then=3),  # TITLE matches worth more
						When(content__icontains=search, then=1),  # content matches
						default=0,
						output_field=IntegerField()
					)
				)
			)

		# sorting applied
		sort_by = self.request.GET.get('sort', 'date')
		order = self.request.GET.get('order', 'desc')

		# MAP SORT options
		sort_mapping = {
			'date': 'date_posted',
			'popularity': 'popularity_score',
			'comments': 'comment_count',
			'votes': 'vote_score',
			'relevance': 'relevance_score' if search else 'date_posted'
		}

		sort_field = sort_mapping.get(sort_by, 'date_posted')

		# 'its not readable'
		# queryset = queryset.order_by(sort_field, 'date_posted') if order == 'asc' else queryset.order_by(f'-{sort_field}', '-date_posted') if sort_field != 'date_posted' else queryset.order_by(sort_field if order == 'asc' else f'-{sort_field}')

		queryset = queryset.order_by(sort_field if order == 'asc' else f'-{sort_field}')
		if sort_field != 'date_posted': # 2nd sort by date
			queryset = queryset.order_by(sort_field, 'date_posted') if order == 'asc' else queryset.order_by(f'-{sort_field}', '-date_posted')

		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		# filter params to context
		context['current_sort'] = self.request.GET.get('sort', 'date')
		context['current_order'] = self.request.GET.get('order', 'desc')

		tag_slug = self.request.GET.get('tag')
		if tag_slug:
			tag_filter = Q(name=tag_slug) | Q(slug=tag_slug)
			tag = Tag.objects.filter(tag_filter).first()
			if tag:
				context['tag'] = tag.slug  # for ulr build
				context['tag_name'] = tag.name  # orig name -- TO PASS DISPLAY ON WEBSITE, instead of ugly slugs

		search = self.request.GET.get('search')
		if search:
			context['search'] = search
			context['show_relevance'] = True  # should_i_show_Show_Relevance_option_in_filter -- bool

		context['tags'] = Tag.objects.all() # tags for SIDEBAAAAAAARRRRRRRRRRRRRRRRRRRRRRR

		# user_votes = get_user_votes_for_posts(self.request.user, context['posts'])
		# for ii in context['posts']:
		# 	ii.user_vote = user_votes.get(ii.id)
		# 	ii.original_user_vote = user_votes.get(ii.original_post.id) if ii.is_repost and ii.original_post else None

		posts = context['posts']
		user_votes = get_user_votes_for_posts(self.request.user, posts) # users votes for all da pots

		# user votes to each post obj
		for post in posts:
			# -------- for REGULAR POSTS  -------- #
			post.user_vote = user_votes.get(post.id)

			# -------- for REPOSTS -------- TODO -- add voting for orig posts -- DONE -w-
			if post.is_repost and post.original_post:
				post.original_user_vote = user_votes.get(post.original_post.id)
			else:
				post.original_user_vote = None

		return context


class UserPostListView(ListView):
	model = Post
	template_name = 'blog/user_posts.html'
	context_object_name = 'posts'
	paginate_by = 5

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		queryset = Post.objects.filter(author=user)

		queryset = queryset.annotate(
			vote_score=Sum(
				Case(
					When(votes__vote_type='upvote', then=1),
					When(votes__vote_type='downvote', then=-1),
					default=0,
					output_field=IntegerField()
				)
			),
			comment_count=Count('comments', distinct=True),
			popularity_score=F('view_count') + F('vote_score') + F('comment_count') * 2
		)

		sort_by = self.request.GET.get('sort', 'date')
		order = self.request.GET.get('order', 'desc')

		sort_mapping = {
			'date': 'date_posted',
			'popularity': 'popularity_score',
			'comments': 'comment_count',
			'votes': 'vote_score'
		}

		sort_field = sort_mapping.get(sort_by, 'date_posted')

		queryset = queryset.order_by(sort_field if order == 'asc' else f'-{sort_field}')

		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context['current_sort'] = self.request.GET.get('sort', 'date')
		context['current_order'] = self.request.GET.get('order', 'desc')

		context['tags'] = Tag.objects.all()
		return context


class PostDetailView(DetailView):
	model = Post

	def get(self, request, *args, **kwargs):
		response = super().get(request, *args, **kwargs)
		post = self.object
		post.view_count = F('view_count') + 1
		post.save()
		post.refresh_from_db()
		return response

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		post = self.get_object()

		context['comment_form'] = CommentForm()
		comments = post.comments.filter(parent=None).select_related(
			'author', 'author__profile'
		).prefetch_related(
			'replies', 'replies__author', 'replies__author__profile',
			'votes', 'replies__votes'
		)

		if self.request.user.is_authenticated:
			comment_ids = [comment.id for comment in comments]
			for reply in comments:
				if reply.replies.exists():
					comment_ids.extend([r.id for r in reply.replies.all()])

			user_comment_votes = CommentVote.objects.filter(
				user=self.request.user,
				comment_id__in=comment_ids
			).values_list('comment_id', 'vote_type')

			user_votes_dict = {comment_id: vote_type for comment_id, vote_type in user_comment_votes}

			# vote info attached to each comment
			for cmt in comments:
				cmt.user_vote = user_votes_dict.get(cmt.id)
				for reply in cmt.replies.all():
					reply.user_vote = user_votes_dict.get(reply.id)

		context['comments'] = comments
		context['tags'] = Tag.objects.all()

		if self.request.user.is_authenticated:
			user_vote = post.votes.filter(user=self.request.user).first()
			context['user_vote'] = user_vote.vote_type if user_vote else None

			if post.is_repost and post.original_post:
				original_vote = post.original_post.votes.filter(user=self.request.user).first()
				context['original_user_vote'] = original_vote.vote_type if original_vote else None
			else:	context['original_user_vote'] = None

		return context

class PostCreateView(LoginRequiredMixin, CreateView):
	model = Post
	form_class = PostForm

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	def get_form(self, form_class=None):
		form = super().get_form(form_class)
		# form.fields['tags'].widget.attrs.update({
		# 	'class': 'select2-tags',
		# 	'data-placeholder': 'Select or create tags...'
		# })
		return form


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Post
	form_class = PostForm

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	def get_form(self, form_class=None):
		form = super().get_form(form_class)
		# form.fields['tags'].widget.attrs.update({
		# 	'class': 'select2-tags',
		# 	'data-placeholder': 'Select or create tags...'
		# })
		return form

	def test_func(self):
		post = self.get_object()
		return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Post
	success_url = '/'

	def test_func(self):
		post = self.get_object()
		return self.request.user == post.author


class UserActivityView(DetailView):
	model = User
	template_name = 'blog/user_activity.html'

	def get_object(self):
		return get_object_or_404(User, username=self.kwargs.get('username'))

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.get_object()

		context['user_obj'] = user

		posts = Post.objects.filter(author=user)

		posts = posts.annotate(
			vote_score=Sum(
				Case(
					When(votes__vote_type='upvote', then=1),
					When(votes__vote_type='downvote', then=-1),
					default=0,
					output_field=IntegerField()
				)
			),
			comment_count=Count('comments', distinct=True),
			# pop_formula = view_cnt + vote_cnt + ( 2 * comment_cnt )
			popularity_score=F('view_count') + F('vote_score') + F('comment_count')*2
		)

		# apply sort from req
		sort_by = self.request.GET.get('sort', 'date')
		order = self.request.GET.get('order', 'desc')

		sort_mapping = {
			'date': 'date_posted',
			'popularity': 'popularity_score',
			'comments': 'comment_count',
			'votes': 'vote_score'
		}

		sort_field = sort_mapping.get(sort_by, 'date_posted')
		posts = posts.order_by(sort_field if order == 'asc' else f'-{sort_field}')

		context['posts'] = posts
		context['posts_count'] = posts.count()

		# users -- COMMENTS -- #
		context['comments'] = Comment.objects.filter(author=user).order_by('-date_posted')
		context['comments_count'] = context['comments'].count()

		# users -- VOTES -- #
		context['votes_count'] = Vote.objects.filter(user=user).count()
		context['upvoted_posts'] = Vote.objects.filter(user=user, vote_type=Vote.UPVOTE)

		# users -- REPOSTS -- #
		context['reposts_count'] = Post.objects.filter(author=user, is_repost=True).count()

		context['tags'] = Tag.objects.all()

		# filter params
		context['current_sort'] = sort_by
		context['current_order'] = order

		return context


def about(request):
	# UPD -- NOW STATS INCLUDED
	from django.contrib.auth.models import User
	from blog.models import Post, Comment, Tag

	context = {
		'title': 'About',
		'posts_count': Post.objects.count(),
		'users_count': User.objects.filter(is_active=True).count(),
		'comments_count': Comment.objects.count(),
		'tags_count': Tag.objects.count(),
	}
	return render(request, 'blog/about.html', context)


@require_GET
def tag_suggestions(request):
	""" return tag suggestions for the tag widget """
	query = request.GET.get('q', '').strip()

	# tags = Tag.objects.annotate(post_count = Count('posts')).order_by('-post_count')[:12] if not query else Tag.objects.filter(name__icontains = query).annotate(post_count=Count('posts')).order_by('-post_count')[:10]

	if not query: # return pop tags if no query
		tags = Tag.objects.annotate(post_count = Count('posts')).order_by('-post_count')[:12]
	else: # search for matching tags
		tags = Tag.objects.filter(name__icontains = query).annotate(post_count=Count('posts')).order_by('-post_count')[:10]

	suggestions = [
		{
			'id': tag.id,
			'name': tag.name,
			'post_count': tag.post_count,
			'slug': tag.slug
		}
		for tag in tags
	]

	return JsonResponse({
		'suggestions': suggestions,
		'query': query
	})

@login_required
def vote_post(request, pk, vote_type):
	post = get_object_or_404(Post, pk=pk)
	user = request.user

	if vote_type not in ['upvote', 'downvote']:
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			return JsonResponse({
				'success': False,
				'message': 'Invalid vote type'
			}, status=400)
		messages.error(request, 'Invalid vote type')
		return HttpResponseRedirect(post.get_absolute_url())

	try:
		with transaction.atomic():
			# UPD -- to prevent race conditions → using SELECT_FOR_UPDATE
			curr_vote = Vote.objects.select_for_update().filter(post=post, user=user).first()

			if curr_vote:
				if curr_vote.vote_type == vote_type: # removing the vote
					curr_vote.delete()
					message = f'You removed your {vote_type}'
				else: # changing vote
					curr_vote.vote_type = vote_type
					curr_vote.save()
					message = f'Changed to {vote_type}'
			else: # new vote
				try:
					Vote.objects.create(post=post, user=user, vote_type=vote_type)
					message = f'Added {vote_type}'
				except IntegrityError: # to handle rare case when vote was created BTWN CHECK n CREATE
					existing_vote = Vote.objects.filter(post=post, user=user).first()
					if existing_vote:
						if existing_vote.vote_type == vote_type:
							existing_vote.delete()
							message = f'You removed your {vote_type}'
						else:
							existing_vote.vote_type = vote_type
							existing_vote.save()
							message = f'Changed to {vote_type}'
					else: raise # if ts still failing → ¯\_(--_--)_/¯

	except IntegrityError as e:
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			return JsonResponse({
				'success': False,
				'message': 'Please wait a moment before voting again'
			}, status=409)
		messages.error(request, 'Please wait a moment before voting again')
		return HttpResponseRedirect(post.get_absolute_url())
	except Exception as e:
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			return JsonResponse({
				'success': False,
				'message': 'An error occurred while voting'
			}, status=500)
		messages.error(request, 'An error occurred while voting')
		return HttpResponseRedirect(post.get_absolute_url())

	post.refresh_from_db()

	# ajax
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		return JsonResponse({
			'success': True,
			'upvotes': post.upvotes,
			'downvotes': post.downvotes,
			'score': post.score,
			'message': message,
			'post_id': post.id
		})

	# default reg resp
	messages.success(request, message)
	return HttpResponseRedirect(post.get_absolute_url())

@login_required
def add_comment(request, pk):
	post = get_object_or_404(Post, pk=pk)

	if request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			comment = form.save(commit=False)
			comment.post = post
			comment.author = request.user

			# if reply
			parent_id = request.POST.get('parent_id')
			if parent_id:
				parent_comment = get_object_or_404(Comment, id=parent_id)
				comment.parent = parent_comment

			comment.save()

			if request.headers.get('x-requested-with') == 'XMLHttpRequest':
				try: author_image = comment.author.profile.image.url
				except: author_image = '/media/default.jpg'

				# json resp with new comment data
				return JsonResponse({
					'success': True,
					'comment_id': comment.id,
					'comment_author': comment.author.username,
					'comment_content': comment.get_safe_content(),
					'comment_date': comment.date_posted.strftime('%B %d, %Y at %I:%M %p'),
					'post_id': post.id,
					'author_image': author_image
				})

			messages.success(request, 'Comment added successfully!')
			return redirect('post-detail', pk=post.pk)

		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			return JsonResponse({
				'success': False,
				'message': 'Invalid form data'
			}, status=400)

	return redirect('post-detail', pk=post.pk)


@login_required
def repost(request, pk):
	original_post = get_object_or_404(Post, pk=pk)

	repost = Post(
		title=f"Repost: {original_post.title}",
		content=original_post.content,
		author=request.user,
		original_post=original_post,
		is_repost=True
	)
	repost.save()

	for tag in original_post.tags.all(): repost.tags.add(tag)

	messages.success(request, f'You reposted "{original_post.title}"')
	return redirect('post-detail', pk=repost.pk)


class TagListView(ListView):
	model = Tag
	template_name = 'blog/tag_list.html'
	context_object_name = 'tags'


class TagCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
	model = Tag
	form_class = TagForm  # UPD -- to use custom form
	template_name = 'blog/tag_form.html'
	success_url = reverse_lazy('tag-list')

	def test_func(self):
		return self.request.user.is_staff


class TagUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	model = Tag
	form_class = TagForm  # UPD
	template_name = 'blog/tag_form.html'
	success_url = reverse_lazy('tag-list')

	def test_func(self):
		return self.request.user.is_staff


class TagDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Tag
	template_name = 'blog/tag_confirm_delete.html'
	success_url = reverse_lazy('tag-list')

	def test_func(self):
		return self.request.user.is_staff


class TagDetailView(ListView):
	model = Post
	template_name = 'blog/tag_posts.html'
	context_object_name = 'posts'
	paginate_by = 5

	def get(self, request, *args, **kwargs):
		tag_slug = self.kwargs.get('slug') #getting slug from url

		tag = Tag.objects.filter(slug=tag_slug).first() # check if this is cur tag slug

		if not tag: # check if its alias -- for old version tags that had no slugs
			alias = TagAlias.objects.filter(alias=tag_slug).first()
			if alias: # if has alies => redirect to the cur tag url
				return redirect('tag-detail', slug=alias.tag.slug)

		return super().get(request, *args, **kwargs)

	def get_queryset(self):
		tag_slug = self.kwargs.get('slug')
		tag = Tag.objects.filter(slug=tag_slug).first()

		if tag:
			queryset = Post.objects.filter(tags=tag)
			queryset = queryset.annotate(
				vote_score=Sum(
					Case(
						When(votes__vote_type='upvote', then=1),
						When(votes__vote_type='downvote', then=-1),
						default=0,
						output_field=IntegerField()
					)
				),
				comment_count=Count('comments', distinct=True),
				popularity_score=F('view_count') + F('vote_score') + F('comment_count')*2
			)

			sort_by = self.request.GET.get('sort', 'date')
			order = self.request.GET.get('order', 'desc')

			sort_mapping = {
				'date': 'date_posted',
				'popularity': 'popularity_score',
				'comments': 'comment_count',
				'votes': 'vote_score'
			}

			sort_field = sort_mapping.get(sort_by, 'date_posted')

			queryset = queryset.order_by(sort_field if order == 'asc' else f'-{sort_field}')
			return queryset

		else: # no tag found => mpty queryset
			return Post.objects.none()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		tag_slug = self.kwargs.get('slug')
		tag = Tag.objects.filter(slug=tag_slug).first()
		if tag:
			context['tag'] = tag
			context['tag_name'] = tag.name
		else:
			context['tag'] = tag_slug
			context['tag_name'] = tag_slug

		context['current_sort'] = self.request.GET.get('sort', 'date')
		context['current_order'] = self.request.GET.get('order', 'desc')

		context['tags'] = Tag.objects.all()
		return context


def get_user_votes_for_posts(user, posts):
	"""
	get hashmap of user votes for list of posts
	return -- dict - {'post_id' : 'vote_type'}
	"""
	if not user.is_authenticated:
		return {}

	post_ids = []
	for post in posts:
		post_ids.append(post.id)
		if post.is_repost and post.original_post:
			post_ids.append(post.original_post.id)

	user_votes = Vote.objects.filter(
		user=user,
		post_id__in=post_ids
	).values_list('post_id', 'vote_type')

	votes_dict = {post_id: vote_type for post_id, vote_type in user_votes}
	return votes_dict
	# user_votes = Vote.objects.filter(
	# 	user=user,
	# 	post__in=posts
	# ).values_list('post_id', 'vote_type')
	#
	# votes_dict = {post_id: vote_type for post_id, vote_type in user_votes} # convert to dict for easier lookup
	#
	# # MIGHT CHANGE THIS -- counting votes for orig posts in case of reposts
	# repost_originals = [post.original_post.id for post in posts if post.is_repost and post.original_post]
	# if repost_originals:
	# 	original_votes = Vote.objects.filter(
	# 		user=user,
	# 		post__in=repost_originals
	# 	).values_list('post_id', 'vote_type')
	#
	# 	for post_id, vote_type in original_votes:
	# 		votes_dict[post_id] = vote_type
	# return votes_dict


@login_required
@require_POST
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user != comment.author:
        return JsonResponse({'success': False,'message': 'Permission denied'},status=403)

    raw_content = request.POST.get('content', '').strip()

    if not raw_content:
        return JsonResponse({
            'success': False,
            'message': 'Comment cannot be empty'
        }, status=400)

    try:
        # U NEED A BLEACHHH
        cleaned_content = bleach.clean(
            raw_content,
            tags=BLEACH_ALLOWED_TAGS,
            attributes=BLEACH_ALLOWED_ATTRIBUTES,
            strip=True
        )

        # making sure its not empty
        if not cleaned_content or cleaned_content.strip() == '':
            return JsonResponse({
                'success': False,
                'message': 'Comment cannot be empty after formatting'
            }, status=400)

        # upd n save
        comment.content = cleaned_content
        comment.is_edited = True
        comment.save()

        return JsonResponse({
            'success': True,
            'content': comment.get_safe_content(),
            'edited': True
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error processing content. Please try again.'
            # 'message': f'Error: {str(e)}'
        }, status=400)

@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    # ONLY AUTHOR can DELETE their comment
    if request.user != comment.author:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'You are not authorized to delete this comment'
            }, status=403)
        return redirect('post-detail', pk=comment.post.pk)

    # save post_id before deleting -- for redirect command
    post_id = comment.post.id

    comment.delete()

    # ajax reqs
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Comment deleted successfully'
        })

    # redirect to post detail -- saving post_id before deleting
    messages.success(request, 'Comment deleted successfully!')
    return redirect('post-detail', pk=post_id)


@login_required
def vote_comment(request, pk):
	comment = get_object_or_404(Comment, pk=pk)
	vote_type = request.POST.get('vote_type', 'up')

	if vote_type not in ['up', 'down']:
		return JsonResponse({'success': False, 'message': 'Invalid vote type'}, status=400)

	# check if user alr voted
	curr_vote = CommentVote.objects.filter(comment=comment, user=request.user).first()

	if curr_vote:
		if curr_vote.vote_type == vote_type:
			curr_vote.delete()
			action = 'removed'
		else:
			curr_vote.vote_type = vote_type
			curr_vote.save()
			action = 'changed'
	else:
		CommentVote.objects.create(
			comment=comment,
			user=request.user,
			vote_type=vote_type
		)
		action = 'added'

	# cnt update
	upvotes = comment.votes.filter(vote_type='up').count()
	downvotes = comment.votes.filter(vote_type='down').count()

	# ajax
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		return JsonResponse({
			'success': True,
			'action': action,
			'upvotes': upvotes,
			'downvotes': downvotes
		})

	return redirect('post-detail', pk=comment.post.pk)


@staff_member_required
def summary_dashboard(request): #ADMIN PANEL -- dashboard for monitoring AI summarization
    # stats
    total_posts = Post.objects.filter(is_repost=False).count()
    summarized_posts = Post.objects.filter(is_repost=False, summary__isnull=False).exclude(summary='').count()
    pendPostCnt = Post.objects.filter(needs_summary_update=True,is_repost=False).count()
    completion_rate = round((summarized_posts / total_posts*100), 1) if total_posts>0 else 0
    recent_summaries = Post.objects.filter(is_repost=False,summary__isnull=False).exclude(summary='').order_by('-summary_generated_at')[:10]
    context = {
        'total_posts': total_posts,
        'summarized_posts': summarized_posts,
        'pending_posts': pendPostCnt,
        'completion_rate': completion_rate,
        'recent_summaries': recent_summaries,
    }
    return render(request, 'blog/summary_dashboard.html', context)