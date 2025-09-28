---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% if site.author.googlescholar %}
  <div class="wordwrap">You can also find my articles on <a href="{{site.author.googlescholar}}">my Google Scholar profile</a>.</div>
{% endif %}

{% include base_path %}

<style>
.publication-item {
  margin-bottom: 2em;
  padding-bottom: 1em;
  border-bottom: 1px solid #eee;
}

.publication-number {
  font-weight: bold;
  color: #2c3e50;
  margin-right: 0.5em;
}

.publication-citation {
  margin-bottom: 0.5em;
  line-height: 1.6;
}

.author-highlight {
  font-weight: bold;
}

.publication-links {
  margin-top: 0.5em;
}

.publication-links a {
  display: inline-block;
  margin-right: 1em;
  padding: 0.3em 0.8em;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  text-decoration: none;
  font-size: 0.9em;
  color: #495057;
  transition: all 0.2s;
}

.publication-links a:hover {
  background-color: #e9ecef;
  text-decoration: none;
}

.publication-links .pdf-link {
  background-color: #005F73;
  color: white;
  border-color: #005F73;
}

.publication-links .pdf-link:hover {
  background-color: #004d5c;
  color: white;
}

.publication-links .bib-link {
  background-color: #0A9396;
  color: white;
  border-color: #0A9396;
}

.publication-links .bib-link:hover {
  background-color: #087a7c;
  color: white;
}

.publication-links .web-link {
  background-color: #94D2BD;
  color: #333;
  border-color: #94D2BD;
}

.publication-links .web-link:hover {
  background-color: #7bc5a7;
  color: #333;
}
</style>

{% assign sorted_publications = site.publications | sort: 'date' | reverse %}
{% assign counter = 1 %}

{% for post in sorted_publications %}
<div class="publication-item">
  <div class="publication-citation">
    <span class="publication-number">[{{ counter }}]</span>
    {% assign citation_text = post.citation | replace: 'Hu, Z.', '<span class="author-highlight">Hu, Z.</span>' | replace: 'Ziqi Hu', '<span class="author-highlight">Ziqi Hu</span>' %}
    {{ citation_text }}
  </div>
  
  <div class="publication-links">
    {% if post.paperurl %}
      <a href="{{ post.paperurl }}" class="pdf-link" target="_blank">
        <i class="fas fa-file-pdf"></i> PDF
      </a>
    {% endif %}
    
    <a href="{{ base_path }}/files/bibtex/{{ post.title | slugify }}.bib" class="bib-link" target="_blank">
      <i class="fas fa-quote-left"></i> CITE
    </a>
    
    {% if post.venue_url %}
      <a href="{{ post.venue_url }}" class="web-link" target="_blank">
        <i class="fas fa-external-link-alt"></i> URL
      </a>
    {% endif %}
  </div>
</div>
{% assign counter = counter | plus: 1 %}
{% endfor %}
