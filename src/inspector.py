from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from markdown import Markdown
import markdown
from datetime import datetime
import os

from pymdownx import superfences

from mdgen import *

# pip install pymdown-extensions

entries=get_entries()

app = Flask(__name__, instance_relative_config=True)

@app.route('/')
def index():
    message="Hello"
    return render_template('index.html',message=message)

@app.route('/task/<string:id>', methods=['GET', 'POST'])
def task_page(id):

    if request.args.get('max') is not None:
        max_= request.args.get('max')
        max_size=min(int(max_),300)
    else:
        max_size=100

    print(f'{id=},{max_size=}')

    content=make_mermaid_data(id,max_size=max_size)
    #print(f'{content=}')
    md = Markdown(
        extensions=[
            'pymdownx.superfences',
            'tables'
        ],
        extension_configs={
            'pymdownx.superfences': {
                'custom_fences': [
                    {
                        'name': 'mermaid',
                        'class': 'mermaid',
                        'format': custom_mermaid_formatter
                    }
                ]
            }
        }
    )
    html_content = md.convert(content)
    return render_template('view.html', page=id, html_content=html_content)

def custom_mermaid_formatter(source, language, class_name, options, md, **kwargs):
    print("custom_mermaid_formatter called")
    return f'<div class="mermaid">\n{source}\n</div>'

if __name__ == '__main__':
    app.run(port=5009,debug=True)
