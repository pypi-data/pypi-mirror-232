from urllib.parse import urljoin
from pelican import signals
from pelican.contents import Page, Static
from pelican.generators import StaticGenerator
from mailscrambler import javascriptify, deobfuscator
import re
import os

# This will match anchor tags with attributes in any order, e.g.
# <a href="mailto:email" class="class1 class2" id="id1" ...>...</a>
TAG_REGEX = r'(?:<a(?P<attributes>(?:\s*[a-zA-Z0-9-]+=\"[^\"]*\")*)>[^\>]*</a>|(?P<mailto>mailto\:)?(?P<addr>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+))'

EMAIL_REGEX = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'

class DeobfGenerator(object):
   def __init__(self, context, settings, path, theme, output_path, *null):
    self.context = context
    self.settings = settings
    self.output_path = output_path
    
   def generate_output(self, writer):
      # Adds deobf.js to output root
      path = os.path.join(self.output_path, "deobf.js")
      with open(path, "w") as f:
        f.write(deobfuscator().replace('<script type="text/javascript">', "").replace("</script>", "").strip())

def email_cloak(base_path: str, content: Page):
  did_some_replacements = False

  def replacement_callback(match):
    nonlocal did_some_replacements
    if match.group("attributes") is not None:
      # Explicit anchor tags: no replacement
      return match.group(0)
    elif (match.group("mailto") is not None and match.group("addr") is not None) or\
      (match.group("mailto") is None and match.group("addr") is not None):
      # Plaintext e-mail: replace with obfuscated e-mail
      did_some_replacements = True
      return javascriptify(match.group("addr"), do_scramble=True)
    else:
      # Anything else: no replacement
      return match.group(0)
    
  content._content = re.sub(TAG_REGEX, replacement_callback, content._content)
  
  # Add a script tag at the end of the page to deobfuscate the emails only if
  # we actually replaced something in this page
  if did_some_replacements:
      # Insert before </body>
      # if base_path is empty, we'll default to root (/), otherwise
      # we'll use the base_path as the base path and for safety we'll append a
      # trailing slash (if there's one already, urljoin will merge them)
      deobf_path = urljoin(base_path + "/", "deobf.js")
      content._content += "<script type=\"text/javascript\" src=\"" + deobf_path + "\"></script>"
  
  return content._content

def _generator_write(generator, content: Page):
  site_base_path = generator.settings.get("SITEURL", "")
  email_cloak(site_base_path, content)

def _generator_enrich_context(generator):
    generator.context["javascriptify"] = javascriptify

def get_generators(generators):
  return DeobfGenerator

def register():
  signals.get_generators.connect(get_generators)
  signals.page_generator_init.connect(_generator_enrich_context)
  signals.page_generator_write_page.connect(_generator_write)
  signals.article_generator_init.connect(_generator_enrich_context)
  signals.article_generator_write_article.connect(_generator_write)