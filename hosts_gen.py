#!/usr/bin/env python3

import jinja2

my_template = '''
{%- for i in range(1, 255) %}
switch-{{ i }}:
    hostname: 10.0.0.{{ i }}
    groups:
        - selab
{% endfor %}
'''

data = jinja2.Template(my_template).render()

with open('hosts.yaml', 'w') as f:
    f.write(data)