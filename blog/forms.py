from django import forms
from django.utils.text import slugify

from .models import Post, Tag, Vote, Comment
from django_ckeditor_5.widgets import CKEditor5Widget
from django.core.validators import MaxLengthValidator


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': CKEditor5Widget(
                config_name='basic',
                attrs={'class': 'django_ckeditor_5'},
            )
        }


class PostForm(forms.ModelForm):
    title = forms.CharField( # UPD -- custom title w/ strict len lim
        max_length = 50,  # adujstable | UPD -- 100 → 50
        validators = [MaxLengthValidator(50)],
        widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a title (max 50 characters)'
        }),
        help_text="Keep titles under 50 characters for better readability."
    )

    class Meta:
        model = Post
        fields = ['title','content','tags']
        widgets = {
            'content': CKEditor5Widget(
                config_name='default',
                attrs={'class': 'django_ckeditor_5'},
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['tags'].widget.attrs.update({
        #     'class': 'select2-tags',
        #     'data-placeholder': 'Select or create tags...',
        #     'required': 'required'
        # })
        # self.fields['tags'].help_text = 'Select at least one tag. You can create new tags by typing.'
        if 'tags' in self.fields:
            self.fields['tags'].required = False

    def clean_title(self):
        title = self.cleaned_data.get('title')
        # 4MYSELF -- title shouldnt be sum like 'AAAAAAAAAAAAAAAAAAAAAAAA'
        if title and len(set(title))<3:  # if less than 3 unique chars
            raise forms.ValidationError('Title must contain more variety of characters.')
        return title

    def clean(self):
        cleaned_data = super().clean()

        existing_tags = self.data.getlist('tags')
        new_tags = [tag for tag in self.data.getlist('tags_new') if tag.strip()]

        if not existing_tags and not new_tags:
            raise forms.ValidationError('Please select at least one tag.')

        return cleaned_data

    def save(self, commit=True):
        """ save func to handle tag creation n assign processes """
        xmpl = super().save(commit=False)

        if commit: xmpl.save()

        tags_to_add = []

        xst_tag_ids = self.data.getlist('tags') # existing
        print(f"Debug - Processing existing tag IDs: {xst_tag_ids}")

        for tag_id in xst_tag_ids:
            try:
                tag = Tag.objects.get(id=int(tag_id))
                tags_to_add.append(tag)
                print(f"Debug - Added existing tag: {tag.name}")
            except (Tag.DoesNotExist, ValueError) as e:
                print(f"Debug - Failed to find tag with ID {tag_id}: {e}")

        new_tag_names = [tag.strip() for tag in self.data.getlist('new_tags') if tag.strip()]
        print(f"Debug - Processing new tag names: {new_tag_names}")

        for tag_name in new_tag_names:
            # tag -- create || get
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            tags_to_add.append(tag)

            print(f"Debug - Created new tag: {tag_name}" if created else f"Debug - Found existing tag: {tag_name}")

        # UPD -- always setting tags even if commit=False
        if tags_to_add:
            if commit:
                xmpl.tags.set(tags_to_add)
                print(f"Debug - Assigned {len(tags_to_add)} tags to post: {xmpl.title}")
            else: # store tags to be set later
                self._tags_to_set = tags_to_add
                print(f"Debug - Stored {len(tags_to_add)} tags for later assignment")

        else: print("Debug - No tags to assign!")

        return xmpl

    def save_m2m(self):
        """ overriding save_m2m to handle tag logic """
        super().save_m2m()

        # if tags were stored earlier → set them now
        if hasattr(self, '_tags_to_set') and self._tags_to_set:
            self.xmpl.tags.set(self._tags_to_set)
            print(f"Debug - Applied stored tags: {[tag.name for tag in self._tags_to_set]}")
            delattr(self, '_tags_to_set')

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name','slug']
        widgets = { 'slug': forms.TextInput(attrs={'placeholder': 'Leave blank to auto-generate from name'}),}
        help_texts = {'slug': 'URL-friendly version of the name. Will be auto-generated if left blank.'}