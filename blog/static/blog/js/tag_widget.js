/* ================ TAG_WIDGET ================ */
$(document).ready(function(){
    // init all tag widgets on pg
    $('.advanced-tag-selector').each(function(){ initializeTagWidget($(this));});

    function initializeTagWidget($widget){
        const fieldName = $widget.data('field-name');
        const $tagInput = $widget.find(`#tagInput-${fieldName}`);
        const $selectedTags = $widget.find(`#selectedTags-${fieldName}`);
        const $popularTags = $widget.find(`#popularTags-${fieldName}`);
        const $suggestions = $widget.find(`#tagSuggestions-${fieldName}`);
        const $hiddenInputs = $widget.find(`#hiddenInputs-${fieldName}`);
        const $addBtn = $widget.find('.add-tag-btn');

        let selectedTags = [];
        let allTags = [];
        let currHlght = -1;
        let debnTmr = null;

        loadPopularTags();
        loadInitialTags();

        function loadPopularTags(){
            $.ajax({
                url: '/tag-suggestions/',
                method: 'GET',
                success: function(data){
                    allTags = data.suggestions;
                    renderPopularTags(data.suggestions.slice(0, 8));
                },
                error: function(){
                    console.error('Failed to load popular tags');
                }
            });
        }

        function loadInitialTags(){
            const initialTagInputs = $hiddenInputs.find('input[type="checkbox"]:checked');
            initialTagInputs.each(function(){
                const tagId = $(this).val();
                const tagName = $(this).data('tag-name') || $(this).next('label').text();
                if(tagName){ addSelectedTag(tagName, tagId, false);}
            });
        }

        function renderPopularTags(tags){
            $popularTags.empty();
            tags.forEach(tag =>{
                const $tagElement = $(`
                    <div class="popular-tag" data-tag-id="${tag.id}" data-tag-name="${tag.name}">
                        <span>${tag.name}</span>
                        <span class="tag-count">${tag.post_count}</span>
                    </div>
                `);
                $popularTags.append($tagElement);
            });
            updatePopularTagsState();
        }

        function addSelectedTag(tagName, tagId = null, isNew = false){
            if(selectedTags.some(tag => tag.name.toLowerCase() === tagName.toLowerCase())){ return;} // if alr sekected
            const tag ={
                id: tagId || `new_${Date.now()}`,
                name: tagName.trim(),
                isNew: isNew
            };

            selectedTags.push(tag);
            renderSelectedTags();
            updateHiddenInputs();
            clearInput();
            updatePopularTagsState();
            validateTags();
        }

        function removeSelectedTag(tagId){
            selectedTags = selectedTags.filter(tag => tag.id != tagId);
            renderSelectedTags();
            updateHiddenInputs();
            updatePopularTagsState();
            validateTags();
        }

        function renderSelectedTags(){
            $selectedTags.empty();

            selectedTags.forEach(tag =>{
                const $tagElement = $(`
                    <div class="selected-tag ${tag.isNew ? 'new-tag' : ''}" data-tag-id="${tag.id}">
                        <span>${tag.name}</span>
                        <button type="button" class="tag-remove" data-tag-id="${tag.id}">
                            <i class="bi bi-x"></i>
                        </button>
                    </div>
                `);
                $selectedTags.append($tagElement);
            });
        }

        function updateHiddenInputs(){
            $hiddenInputs.empty();

            selectedTags.forEach(tag =>{ // new or existing tag
                const $input = $(`<input type="hidden" name="${fieldName}_${tag.isNew ? 'new' : 'existing'}" value="${tag.isNew ? tag.name : tag.id}">`);
                $hiddenInputs.append($input);
            });
        }

        function updatePopularTagsState(){
            $popularTags.find('.popular-tag').each(function(){
                const tagName = $(this).data('tag-name');
                const isSelected = selectedTags.some(tag => tag.name.toLowerCase() === tagName.toLowerCase());
                $(this).toggleClass('selected', isSelected);
            });
        }

        function clearInput(){
            $tagInput.val('');
            $suggestions.removeClass('show').empty();
            currHlght = -1;
        }

        function showSuggestions(query){
            if(!query.trim()){ $suggestions.removeClass('show').empty(); return;}

            // DEBOUNCE API CALLS
            clearTimeout(debnTmr);
            debnTmr = setTimeout(() =>{
                $.ajax({
                    url: '/tag-suggestions/',
                    method: 'GET',
                    data:{ q: query },
                    success: function(data){
                        renderSuggestions(data.suggestions, query);
                    },
                    error: function(){ console.error('Failed to load tag suggestions');}
                });
            }, 300);
        }

        function renderSuggestions(suggestions, query){
            $suggestions.empty();

            // filtering out alr selected tags
            const filteredSuggestions = suggestions.filter(tag => !selectedTags.some(selected => selected.name.toLowerCase() === tag.name.toLowerCase()));

            // == TAG SUGGESTIONS ==
            filteredSuggestions.forEach((tag, index) =>{
                const $suggestionElement = $(`
                    <div class="suggestion-item ${index === 0 ? 'highlighted' : ''}" data-tag-id="${tag.id}" data-tag-name="${tag.name}">
                        <span>${tag.name}</span>
                        <span class="suggestion-meta">
                            <i class="bi bi-tag"></i> ${tag.post_count} posts
                        </span>
                    </div>
                `);
                $suggestions.append($suggestionElement);
            });

            // == IF NO MATCH → CREATE NEW TAG OPTION
            const exactMatch = filteredSuggestions.some(tag => tag.name.toLowerCase() === query.toLowerCase());

            if(!exactMatch && query.trim()){
                const $createNewElement = $(`
                    <div class="suggestion-item create-new" data-tag-name="${query}" data-is-new="true">
                        <span><i class="bi bi-plus-circle"></i> Create "${query}"</span>
                        <span class="suggestion-meta">
                            <i class="bi bi-star"></i> New tag
                        </span>
                    </div>
                `);
                $suggestions.append($createNewElement);
            }

            currHlght = filteredSuggestions.length > 0 ? 0 : $suggestions.children().length - 1;
            updateHighlight();
            $suggestions.addClass('show');
        }

        function updateHighlight(){
            $suggestions.find('.suggestion-item').removeClass('highlighted');
            $suggestions.find('.suggestion-item').eq(currHlght).addClass('highlighted');
        }

        function validateTags(){
            const isValid = selectedTags.length > 0;
            $widget.find('.tag-input-container').toggleClass('is-invalid', !isValid);
            return isValid;
        }

        $tagInput.on('input', function(){
            const query = $(this).val();
            showSuggestions(query);
        });

        // == EVENT HANDLER == //
        $tagInput.on('keydown', function(e){
            const $suggestionItems = $suggestions.find('.suggestion-item');

            if(e.key === 'ArrowDown'){
                e.preventDefault();
                currHlght = Math.min(currHlght + 1, $suggestionItems.length - 1);
                updateHighlight();
            } else if(e.key === 'ArrowUp'){
                e.preventDefault();
                currHlght = Math.max(currHlght - 1, 0);
                updateHighlight();
            } else if(e.key === 'Enter' || e.key === ','){
                e.preventDefault();
                const $highlighted = $suggestionItems.eq(currHlght);
                if($highlighted.length){
                    const tagName = $highlighted.data('tag-name');
                    const tagId = $highlighted.data('tag-id');
                    const isNew = $highlighted.data('is-new');
                    addSelectedTag(tagName, tagId, isNew);
                } else{
                    const query = $(this).val().trim();
                    if(query){ addSelectedTag(query, null, true);}
                }
            } else if(e.key === 'Escape'){ clearInput();}
            else if(e.key === 'Backspace' && $(this).val() === ''){
                // NFEAT -- rm last tag if input is empty n backspace is pressed
                if(selectedTags.length>0){ removeSelectedTag(selectedTags[selectedTags.length-1].id);}
            }
        });

        // 'ADD TAG' BTN
        $addBtn.on('click', function(){
            const query = $tagInput.val().trim();
            if(query){ addSelectedTag(query, null, true);}
        });

        $popularTags.on('click', '.popular-tag:not(.selected)', function(){
            const tagName = $(this).data('tag-name');
            const tagId = $(this).data('tag-id');
            addSelectedTag(tagName, tagId, false);
        });

        $selectedTags.on('click', '.tag-remove', function(e){
            e.stopPropagation();
            const tagId = $(this).data('tag-id');
            removeSelectedTag(tagId);
        });

        $suggestions.on('click', '.suggestion-item', function(){
            const tagName = $(this).data('tag-name');
            const tagId = $(this).data('tag-id');
            const isNew = $(this).data('is-new');
            addSelectedTag(tagName, tagId, isNew);
        });

        $(document).on('click', function(e){
            if(!$(e.target).closest($widget).length){ $suggestions.removeClass('show');}
        });

        // form valid during submit
        $widget.closest('form').on('submit', function(e){
            if(!validateTags()){
                e.preventDefault();
                $tagInput.focus();

                const $errorMsg = $widget.find('.invalid-feedback');
                $errorMsg.show();

                $('html, body').animate({ scrollTop: $widget.offset().top-100}, 500);
                return false;
            }
        });

        // clicking tag input container → AUTO FOCUS
        $widget.find('.tag-input-container').on('click', function(e){
            if($(e.target).closest('.selected-tag, .tag-remove').length === 0){ $tagInput.focus();}
        });
    }
});