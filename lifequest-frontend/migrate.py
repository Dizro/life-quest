import re

def migrate():
    reg_path = "src/components/register.vue"
    foot_path = "src/components/LQfooter.vue"
    
    with open(reg_path, "r", encoding="utf-8") as f:
        reg_content = f.read()
        
    # Extract mountains container
    mountain_match = re.search(r'<div class="mountains-container">[\s\S]*?</div>', reg_content)
    mountains_html = mountain_match.group(0) if mountain_match else ""
    
    # Remove mountains container from register.vue
    if mountains_html:
        reg_content = reg_content.replace(mountains_html, "")
        
    # Remove footer from register.vue
    footer_match = re.search(r'<footer class="footer">[\s\S]*?</footer>', reg_content)
    if footer_match:
        reg_content = reg_content.replace(footer_match.group(0), "")
        
    # Remove mountains-container css
    css_match = re.search(r'/\* SVG Горы \*/[\s\S]*?/\* Подвал \*/', reg_content)
    if css_match:
        reg_content = reg_content.replace(css_match.group(0), "/* Подвал */")
        
    # Remove footer css
    footer_css_match = re.search(r'/\* Подвал \*/[\s\S]*?/\* Адаптивность для мобильных устройств \*/', reg_content)
    if footer_css_match:
        reg_content = reg_content.replace(footer_css_match.group(0), "/* Адаптивность для мобильных устройств */")

    # Update LQfooter.vue
    with open(foot_path, "r", encoding="utf-8") as f:
        foot_content = f.read()
        
    # We want to replace <div class="mountains-svg">...</div> with the new mountains_html
    # And maybe adjust classes
    new_footer_template = f"""<template>
  <footer class="lq-footer">
{mountains_html}
    <div class="footer-base">
      <span class="footer-text">LifeQuest © 2026. Твоя жизнь — твоя игра.</span>
    </div>
  </footer>
</template>

<style scoped>
.lq-footer {{
  width: 100%;
  flex-shrink: 0;
  background: transparent;
  margin-top: auto;
}}

.mountains-container {{
  width: 100%;
  background-color: transparent; /* Changed from #36205d to match */
  line-height: 0; 
}}

.mountains-container svg {{
  width: 100%;
  height: auto;
  max-height: 300px; 
  display: block;
  object-fit: cover;
}}

.footer-base {{
  background-color: #2a154a;
  padding: 20px 24px;
  text-align: center;
}}

.footer-text {{
  font-family: 'Varela Round', sans-serif;
  font-size: 14px;
  color: #bda8ff;
}}
</style>
"""

    with open(reg_path, "w", encoding="utf-8") as f:
        f.write(reg_content)
        
    with open(foot_path, "w", encoding="utf-8") as f:
        f.write(new_footer_template)
        
migrate()
