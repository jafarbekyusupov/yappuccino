from django import forms
from django.utils.safestring import mark_safe
# from django.urls import reverse
# import json


class AdvancedTagWidget(forms.CheckboxSelectMultiple):
	""" tag selection widget w search n creation mechanics """

	template_name = 'blog/widgets/advanced_tag_widget.html'

	def __init__(self, attrs=None):
		default_attrs = { 'class': 'advanced-tag-widget'}
		if attrs: default_attrs.update(attrs)
		super().__init__(default_attrs)

	def format_value(self, value):
		if value is None: return []
		if isinstance(value, (list,tuple)): return [str(v) for v in value]
		return [str(value)]

	def render(self, name, value, attrs=None, renderer=None):
		context = self.get_context(name, value, attrs)
		return mark_safe(self._render_template(context))

	def _render_template(self, context):
		widget_html = f'''
        <div class="advanced-tag-selector" data-field-name="{context['widget']['name']}">
            <div class="tag-input-container" id="tagContainer-{context['widget']['name']}">
                <div class="selected-tags-container" id="selectedTags-{context['widget']['name']}">
                    
                </div>

                <div class="input-group">
                    <input type="text" 
                           class="form-control tag-input" 
                           id="tagInput-{context['widget']['name']}" 
                           placeholder="Type to search existing tags or create new ones..."
                           autocomplete="off">
                    <div class="input-group-append">
                        <button type="button" class="btn btn-outline-orange add-tag-btn" data-target="{context['widget']['name']}">
                            <i class="bi bi-plus"></i> Add
                        </button>
                    </div>
                </div>
            </div>

            <div class="popular-tags-section mt-3">
                <h6 class="popular-tags-title">
                    <i class="bi bi-fire"></i> Popular Tags
                </h6>
                <div class="popular-tags-grid" id="popularTags-{context['widget']['name']}">
                    <!-- pop tags -->
                </div>
            </div>

            <div class="tag-suggestions" id="tagSuggestions-{context['widget']['name']}">
                <!-- suggestions -->
            </div>

            <div class="hidden-tag-inputs" id="hiddenInputs-{context['widget']['name']}">
                <!-- hidden inputs -->
            </div>

            <div class="invalid-feedback" id="tagsError-{context['widget']['name']}">
                Please select at least one tag.
            </div>
        </div>
        '''
		return widget_html

	def value_from_datadict(self, data, files, name):
		existing_tags = data.getlist(f'{name}_existing')
		new_tags = data.getlist(f'{name}_new')

		# return -- COMBINED LIST
		result = []
		if existing_tags: result.extend(existing_tags)
		if new_tags: result.extend([f'new:{tag}' for tag in new_tags if tag.strip()])

		return result

	class Media:
		css = { 'all': ('blog/css/advanced_tag_widget.css',)}
		js = ('blog/js/advanced_tag_widget.js',)