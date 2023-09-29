import json
import os
import pathlib
import re

from jinja2 import Environment, FileSystemLoader


class TargetSettingsFileParser:

  @staticmethod
  def parse(settings: dict, fallbacks: dict) -> dict:

    try:

      # lib_root_path = pathlib.Path(__file__).resolve().parent.parent.parent

      current_dir = os.path.dirname(os.path.abspath(__file__))
      templates_path = os.path.join(current_dir, 'templates')

      env = Environment(loader=FileSystemLoader(templates_path))
      template = env.get_template('default.j2')

      rendered_str = template.render({
        'settings': settings,
        'fallbacks': fallbacks
      })

      rendered_json = json.loads(re.sub(r',\s*}', '}', re.sub(r',\s*]', ']', rendered_str)))

    except Exception as e:
      return {
        'error': e
      }

    return rendered_json
