from django.contrib import admin
from .models import Post, Tag, Vote, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('author', 'content', 'date_posted')
    readonly_fields = ('date_posted',)


class VoteInline(admin.TabularInline):
    model = Vote
    extra = 0
    fields = ('user', 'vote_type', 'created_at')
    readonly_fields = ('created_at',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_posted', 'display_tags', 'view_count', 'score', 'comments_count')
    list_filter = ('date_posted', 'author', 'tags', 'is_repost')
    search_fields = ('title', 'content')
    filter_horizontal = ('tags',)
    readonly_fields = ('view_count',)
    inlines = [CommentInline, VoteInline]

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    def score(self, obj):
        return obj.score

    def comments_count(self, obj):
        return obj.comments.count()

    display_tags.short_description = 'Tags'
    score.short_description = 'Score'
    comments_count.short_description = 'Comments'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = 'Number of Posts'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'short_content', 'date_posted', 'is_reply')
    list_filter = ('date_posted', 'author', 'post')
    search_fields = ('content', 'author__username', 'post__title')
    readonly_fields = ('date_posted',)

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    def is_reply(self, obj):
        return obj.parent is not None

    short_content.short_description = 'Content'
    is_reply.short_description = 'Is Reply'
    is_reply.boolean = True


class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'vote_type', 'created_at')
    list_filter = ('vote_type', 'created_at', 'post')
    search_fields = ('user__username', 'post__title')
    readonly_fields = ('created_at',)


admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Vote, VoteAdmin)