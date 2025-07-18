from app.mods.types.base import Jinja
from app.mods.decorators.base import component
from app.models import Div, Button, FlexSearch
from app.components.inputs  import input_search
from app.components.buttons import button_search
from app.helper import if_div, if_class, if_id

@component
def flexsearch(
        search_div: Div=Div(),
        search:     FlexSearch=FlexSearch(),
        button_div: Div=Div(),
        button:     Button=Button(),
        depends_on=[button_search, input_search]
    ) -> Jinja:

    search_div_         = if_div(search_div)
    button_div_         = if_div(button_div)
    input_div           = if_div(search.input_div)
    results_div         = if_div(search.results_div)
    results_cover_div   = if_div(search.results.cover.cover_div)
    results_cover_id    = if_id(search.results.cover.cover_id)
    results_cover_class = if_class(search.results.cover.cover_class)
    results_title_div   = if_div(search.results.title.title_div)
    results_title_id    = if_id(search.results.title.title_id)
    results_title_class = if_class(search.results.title.title_class)
    results_kind_div    = if_div(search.results.kind.kind_div)
    results_kind_id     = if_id(search.results.kind.kind_id)
    results_kind_class  = if_class(search.results.kind.kind_class)
    results_desc_div    = if_div(search.results.desc.desc_div)
    results_desc_id     = if_id(search.results.desc.desc_id)
    results_desc_class  = if_class(search.results.desc.desc_class)
    no_results_div      = if_div(search.no_results_div)
    null_button         = Button()
    results_div_style = "position: absolute; top: 101%; left: 0; width: 100%; z-index: 10;"

    return """jinja
<div {{ search_div_ }}> 
    <div {{ input_div }} >
        {{ input_search(search.input) }}
    </div>
    {% if not button == null_button %}
    <div {{ button_div_ }}>
        {{ button_search(button) }}
    </div>
    {% endif %}
</div>
<div {{ results_div }} x-show="hasSearchResults" x-cloak
    style="{{ results_div_style }}"
>
</div>
<script src="{{ search.script_url }}"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
    let index = new FlexSearch.Document({
        tokenize: "forward",
        document: {
            id: "id",
            index: {{ search.index.index_types | tojson }},
            store: {{ search.index.index_store_types | tojson }}
        }
    });
    const searchInput = document.getElementById('{{ search.input.input_id }}');
    const searchResultsDiv = document.getElementById('{{ search.results_div.div_id }}');
    function getAlpineScope() {
        return document.body.__x && document.body.__x.$data ? document.body.__x.$data : null;
    } 
    fetch("{{ search.index.index_json_file }}")
        .then(response => {
            if (!response.ok) throw new Error("Missing searchindex.json");
            return response.json();
        })
        .then(data => {
            data.docs.forEach(doc => {
                index.add(doc);
            });
            searchInput.addEventListener('input', function(e) {
                const alpineScope = getAlpineScope();
                let query = e.target.value;
                if (!query || !query.trim()) {
                    searchResultsDiv.innerHTML = "";
                    if (alpineScope) {
                       alpineScope.hasSearchResults = false;
                    } else {
                       searchResultsDiv.style.display = 'none';
                    }
                    return;
                }
                let results = index.search(query, {limit: {{ search.results.limit }}, enrich: true});
                let docs = [];
                results.forEach(result => docs.push(...result.result));
                const uniqueDocsById = {};
                docs.forEach(d => {
                    const id = d.doc.id;
                    if (!uniqueDocsById[id]) {
                        uniqueDocsById[id] = d.doc;
                    }
                });
                const uniqueDocs = Object.values(uniqueDocsById);
                if (uniqueDocs.length > 1) {
                    searchResultsDiv.innerHTML = uniqueDocs.map(d => {
                        const prettyTitle = t =>
                            typeof t === "string" ? t :
                            (t && typeof t === "object" && t.name ? t.name : "");  
                        return `
                            <div {{ results_div }}>
                                <div style="display: flex; width: 101%;">
                                    {% if search.results.cover.display %}
                                        <div {{ results_cover_div }}>
                                            <img src="${d.cover ?? "#"}" {{ results_cover_id }} {{ results_cover_class }}>
                                        </div>
                                        {% if search.results.kind.display %}
                                        <div style="display: flex;">
                                            <div {{ results_kind_div }}>
                                                <span {{ results_kind_id }} {{ results_kind_class }} >${ results_kind_content[d.kind] ?? d.kind }</span>
                                            </div>
                                            {% if search.results.title.display %}
                                            <div {{ results_title_div }}>
                                                <a href="${d.href ?? "#"}" {{ results_title_id }} {{ results_title_class }}>${prettyTitle(d.title)}</a>
                                            </div>
                                            {% endif %}
                                        </div>
                                        {% else %}    
                                        <div {{ results_title_div }}>
                                            <a href="${d.href ?? "#"}" id="{{ results_title_id }}" class="{{ results_title_class }}">${prettyTitle(d.title)}</a>
                                        </div> 
                                        {% endif %}
                                    {% else %}
                                        {% if search.results.kind.display %}
                                        <div style="display: flex;">
                                            <div {{ results_kind_div }}>
                                                <span {{ results_kind_id }} {{ results_kind_class }} >${ results_kind_content[d.kind] ?? d.kind }</span>
                                            </div>
                                            {% if search.results.title.display %}
                                            <div {{ results_title_div }}>
                                                <a href="${d.href ?? "#"}" {{ results_title_id }} {{ results_title_class }}>${prettyTitle(d.title)}</a>
                                            </div>
                                            {% endif %}
                                        </div>
                                        {% else %}    
                                        <div {{ results_title_div }}>
                                            <a href="${d.href ?? "#"}" id="{{ results_title_id }}" class="{{ results_title_class }}">${prettyTitle(d.title)}</a>
                                        </div> 
                                        {% endif %}
                                    {% endif %}
                                </div>
                                {% if search.results.desc.display %}
                                <div {{ results_desc_div }}>
                                    <span {{ results_desc_id }} {{ results_desc_class }}>${d.content ? d.content.substring(1,{{search.results.desc.desc_lenght}}) : ""}</span>
                                </div>
                                {% endif %}
                            </div>
                        `; 
                    }).join('');
                    if (alpineScope) {
                       alpineScope.hasSearchResults = true;
                    } else {
                       searchResultsDiv.style.display = '';
                    }
                } else {
                    searchResultsDiv.innerHTML = `<div {{ no_results_div }}>{{ search.no_results }}</div>`;
                    if (alpineScope) {
                        alpineScope.hasSearchResults = true;
                    } else {
                       searchResultsDiv.style.display = '';
                    }
                }
            });
            searchInput.addEventListener('blur', function() {
                const alpineScope = getAlpineScope();
                setTimeout(() => {
                    if (!searchResultsDiv.contains(document.activeElement)) {
                        if (alpineScope) {
                            alpineScope.hasSearchResults = false;
                        } else {
                            searchResultsDiv.style.display = 'none';
                        }
                        searchResultsDiv.innerHTML = "";
                    }
                }, 101);
            });
            searchResultsDiv.addEventListener('mousedown', function(e) {
                e.preventDefault();
            });
        })
        .catch(err => {   
            const alpineScope = getAlpineScope();
            searchResultsDiv.innerHTML = `<div {{ no_results_div }}>{{ search.no_results }}</div>`;
            console.error("Search index loading failed:", err);
            if (alpineScope) {
                alpineScope.hasSearchResults = true;
            } else {
                searchResultsDiv.style.display = '';
                console.warn("Alpine scope not ready in fetch catch block. Manually showing results div.");
            }
        }); 
});
</script>
"""
