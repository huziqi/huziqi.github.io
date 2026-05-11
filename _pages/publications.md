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
.pub-section-title {
  font-size: 1.2em;
  font-weight: 700;
  color: #2c3e50;
  margin-top: 1.8em;
  margin-bottom: 0.8em;
  padding-bottom: 0.3em;
  border-bottom: 2px solid #005F73;
}

.publication-item {
  margin-bottom: 1.2em;
  padding-bottom: 1em;
  border-bottom: 1px solid #eee;
  line-height: 1.6;
}

.publication-number {
  font-weight: bold;
  color: #555;
  margin-right: 0.4em;
}

.author-highlight {
  font-weight: bold;
}

.pub-url-link {
  color: #005F73;
  text-decoration: none;
  font-size: 0.92em;
  margin-left: 0.4em;
}

.pub-url-link:hover {
  text-decoration: underline;
  color: #0A9396;
}
</style>

{% assign all_pubs = site.publications | sort: 'date' | reverse %}

{% assign first_author_pubs = "" | split: "" %}
{% assign other_pubs        = "" | split: "" %}

{% for pub in all_pubs %}
  {% if pub.author_position == 1 or pub.corresponding == true %}
    {% assign first_author_pubs = first_author_pubs | push: pub %}
  {% else %}
    {% assign other_pubs = other_pubs | push: pub %}
  {% endif %}
{% endfor %}

<!-- Multi-key sort for co-authored: author_position ASC, then date DESC.
     Liquid only supports single-key sort, so we iterate positions explicitly.
     other_pubs is already date-DESC, so within each position group the order is preserved. -->
{% assign other_sorted = "" | split: "" %}
{% for pos in (1..20) %}
  {% for post in other_pubs %}
    {% if post.author_position == pos %}
      {% assign other_sorted = other_sorted | push: post %}
    {% endif %}
  {% endfor %}
{% endfor %}
<!-- Papers with no author_position (0 or missing) go at the end -->
{% for post in other_pubs %}
  {% unless post.author_position %}
    {% assign other_sorted = other_sorted | push: post %}
  {% endunless %}
{% endfor %}

<div class="pub-section-title">First / Corresponding Author</div>

{% assign counter = 1 %}
{% for post in first_author_pubs %}
<div class="publication-item">
  <span class="publication-number">[{{ counter }}]</span>
  {% assign citation_text = post.citation | replace: 'Hu, Z.', '<span class="author-highlight">Hu, Z.</span>' | replace: 'Ziqi Hu', '<span class="author-highlight">Ziqi Hu</span>' %}
  {{ citation_text }}
  {% if post.venue_url %}
    <a href="{{ post.venue_url }}" class="pub-url-link" target="_blank">[Link]</a>
  {% endif %}
</div>
{% assign counter = counter | plus: 1 %}
{% endfor %}

<div class="pub-section-title">Co-authored Publications</div>

{% for post in other_sorted %}
<div class="publication-item">
  <span class="publication-number">[{{ counter }}]</span>
  {% assign citation_text = post.citation | replace: 'Hu, Z.', '<span class="author-highlight">Hu, Z.</span>' | replace: 'Ziqi Hu', '<span class="author-highlight">Ziqi Hu</span>' %}
  {{ citation_text }}
  {% if post.venue_url %}
    <a href="{{ post.venue_url }}" class="pub-url-link" target="_blank">[Link]</a>
  {% endif %}
</div>
{% assign counter = counter | plus: 1 %}
{% endfor %}
