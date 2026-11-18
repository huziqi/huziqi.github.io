---
permalink: /
title: "About me"
author_profile: true
redirect_from:
  - /about/
  - /about.html
---

I'm a Ph.D. student in Civil Engineering at Hong Kong University of Science and Technology (HKUST). My current research interests include Intelligent building control, Semantic models (e.g., Brick), Large language model, Robotics, SLAM, Machine learning. I'm currently supervised by [Prof. Zhe Wang](https://walterzwang.github.io/).

Prior to joining HKUST, I was an algorithm engineer at Meituan, Beijing from 2023 to 2024. I received my Bachelor and M.Phil at Nankai University, majoring in Intelligent Science and Robotics, supervised by Prof. Jing Yuan.

I'm currently looking for post-doc positions starting from Fall 2027. Please feel free to reach out if you have any questions or opportunities. [[EMAIL]](mailto:zhubg@connect.ust.hk)

# News

<div style="max-height: 300px; overflow-y: auto; margin-bottom: 30px;">
  <div style="display: flex; flex-direction: column; gap: 12px;">
    {% for item in site.data.news %}
      <div style="display: flex; gap: 15px; align-items: baseline;">
        <div style="font-weight: 700; color: #005F73; font-family: 'Roboto', sans-serif; min-width: 70px;">
          {{ item.date | date: "%Y.%m" }}
        </div>
        <div style="flex: 1; line-height: 1.5; color: #34495e;">
          {{ item.content }}
        </div>
      </div>
    {% endfor %}
  </div>
</div>

# Featured Works

{% include base_path %}
{% include featured-works.html %}

---

## 🌍 Visitor Map

<div style="
  display: flex;
  align-items: flex-start;
  gap: 28px;
  flex-wrap: wrap;
  margin: 8px 0 24px 0;
  padding: 24px 28px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 12px rgba(0,95,115,0.06);
">

  <!-- Left: visitor map, generated daily by .github/workflows/update_visitor_map.yml from Flag Counter data -->
  <div style="flex: 2; min-width: 280px;">
    <p style="margin: 0 0 10px 0; font-size: 0.82em; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Visitor Locations</p>
    <a href="https://info.flagcounter.com/pYAe"><img src="{{ base_path }}/images/visitor_map.svg?v={{ site.time | date: '%s' }}" alt="World map of visitors by country" border="0" loading="lazy" style="display:block; width:100%; height:auto; border-radius:8px; border: 1px solid #e2e8f0; background:#fff;"></a>
  </div>

  <!-- Right: Flag Counter -->
  <div style="flex: 1; min-width: 200px;">
    <p style="margin: 0 0 10px 0; font-size: 0.82em; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Visits by Countries and Regions</p>
    <a href="https://info.flagcounter.com/pYAe"><img src="https://s01.flagcounter.com/count2/pYAe/bg_FFFFFF/txt_000000/border_CCCCCC/columns_2/maxflags_20/viewers_0/labels_0/pageviews_1/flags_0/percent_0/" alt="Flag Counter" border="0" style="max-width:100%; border-radius:8px; border: 1px solid #e2e8f0;"></a>
  </div>

</div>
