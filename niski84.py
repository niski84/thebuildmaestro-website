from __future__ import print_function
from flask import Flask, url_for, render_template, send_from_directory, redirect, request
try:
	from markupsafe import Markup
except ImportError:
	# Fallback for older Flask versions
	try:
		from flask import Markup
	except ImportError:
		from jinja2 import Markup
try:
	from werkzeug.contrib.atom import AtomFeed
except ImportError:
	# werkzeug.contrib.atom was removed in Werkzeug 1.0+
	# Using feedgen as alternative
	try:
		from feedgen.feed import FeedGenerator
		AtomFeed = None  # Will handle differently
	except ImportError:
		AtomFeed = None
from datetime import datetime, timedelta
import os
import sys
try:
	from urllib.parse import urljoin
except ImportError:
	from urlparse import urljoin
try:
	import configparser
except ImportError:
	import ConfigParser as configparser
import markdown

app = Flask(__name__)

# Environment-based configuration
CANONICAL_DOMAIN = os.environ.get('CANONICAL_DOMAIN', 'https://thebuildmaestro.com')
ATOM_FEED = os.environ.get('ATOM_FEED', '/atom.xml')
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
CONTENT_PATH = os.path.join(CURRENT_PATH, 'static/content')
PHOTO_PATH = os.path.join(CURRENT_PATH, 'static/files/photos')
CACHE_TIMEOUT = 604800

# Traverse the /content/ directory at startup
# rather than with every page load, and create a
# dict with all the content details
# Articles and Code are treated similarly
# So we'll keep a structure like:
# site_content_registry = { 'articles' => {'id1'=>{author,url,etc}}, {'id2'=> ... }
#		               'code' => {'id1'=>{author,url,etc},  } }

site_content_registry = {}
for content_type_category in [ 'articles', 'code' ]:
	content_dir_path = os.path.join(CONTENT_PATH, content_type_category)
	content_dirs = os.listdir(content_dir_path)

	type_specific_dict = {}
	# For each dir here, read the metadata file
	for content_dir in content_dirs:
		item_metadata_dict = {}
		config = configparser.ConfigParser()
		metadata_path = os.path.join(content_dir_path, content_dir, 'metadata')
		if not os.path.isfile(metadata_path):
			print("Could not read metadata file: {0}".format(metadata_path), file=sys.stderr)
			continue
		config.read( metadata_path )
		content_item_id = content_dir
		for key in [ 'title', 'author', 'last_updated', 'written_on', 'distributions', 'description', 'url' ]:
			try:
				item_metadata_dict[key] = config.get('metadata', key)
			except:
				item_metadata_dict[key] = ""
		type_specific_dict[content_item_id] = item_metadata_dict
	site_content_registry[content_type_category] = type_specific_dict

@app.route('/')
def render_homepage_redirect():
	return redirect(url_for('display_articles_listing'))

@app.route('/articles/')
def display_articles_listing():
	return render_template('articles.html', metadata = site_content_registry['articles'])

@app.route('/code/')
def display_code_projects_listing():
	return render_template('code.html', metadata = site_content_registry['code'])

@app.route('/articles/<id>')
@app.route('/articles/<id>/')
def render_single_article(id):

	# First see if the id exists in our bootup metadata scan:
	if not id in site_content_registry['articles']:
			return "404", 404

	# The above test should be enough, but just in case (since it involves the filesystem):
	id = id.replace("..","")

	# Get the absolute path to the README.md file
	readme_path = os.path.join(CONTENT_PATH, 'articles', id, 'README.md')

	# Triple check the id, by seeing if the resulting path is in CONTENT_PATH
	if not os.path.realpath(readme_path).startswith(CONTENT_PATH):
		return "Forbidden", 403

	# Read file
	with open(readme_path, 'r') as readme_f:
		# Generate markdown HTML
		content = Markup( markdown.markdown( text = readme_f.read(), extensions = [
			'markdown.extensions.nl2br', 'markdown.extensions.extra', 'markdown.extensions.codehilite' ],
			extension_configs = { 'markdown.extensions.codehilite': {
						'guess_lang': False }} ))

	return render_template('article-display.html',
		content = content,
		metadata = site_content_registry['articles'][id],
		url = urljoin(CANONICAL_DOMAIN, '/articles/{id}/'.format(id=id)),
		id = id
	)


# This is for images and files kept in the article dir
# referenced with relative links in the markdown
@app.route('/articles/<id>/<content>')
def serve_article_asset(id, content):

	if not id in site_content_registry['articles']:
			return "404", 404

	id = id.replace("..","")

	# send_from_directory does the is-file-in-content-path check automatically:
	return send_from_directory( os.path.join(CONTENT_PATH, 'articles'), os.path.join(id, content), cache_timeout=CACHE_TIMEOUT )


# Photos
@app.route('/photos/')
def display_photo_gallery():
	thumbnails = 'thumbnails'
	# Get a list of filenames from the photopath
	photos = os.listdir(PHOTO_PATH);
	if thumbnails in photos:
		photos.remove(thumbnails);
	photos.sort();
	photo_relative_path = 'files/photos'
	photo_thumbnails_relative_path = 'files/photos/' + thumbnails
	return render_template('photos.html', photos=enumerate(photos),
		photo_relative_path=photo_relative_path,
		photo_thumbnails_relative_path=photo_thumbnails_relative_path)


# Contact page
@app.route('/contact/')
def render_contact_page():
	return render_template('contact.html')


# 404 page
@app.route('/404/')
def render_error_404():
	return render_template('404.html')

# Atom feed
@app.route(ATOM_FEED)
def generate_atom_rss_feed():
	if AtomFeed is None:
		# AtomFeed not available (werkzeug.contrib.atom was removed)
		# Return a simple text response indicating feed is not available
		from flask import Response
		return Response('Atom feed generation not available. Please install feedgen or use an older werkzeug version.', 
		                mimetype='text/plain', status=503)
	
	feed = AtomFeed('thebuildmaestro - Articles',
		feed_url=urljoin(CANONICAL_DOMAIN, ATOM_FEED), url=CANONICAL_DOMAIN,
		icon=url_for('static', filename='favicon.ico'))
	for article_id,article_metadata in site_content_registry['articles'].items():
		title = article_metadata['title'];
		summary = article_metadata['description']
		url = urljoin(CANONICAL_DOMAIN, '/articles/{id}/'.format(id=article_id))
		try:
			updated = datetime.strptime(article_metadata['last_updated'], '%Y-%m-%d')
			published = datetime.strptime(article_metadata['written_on'], '%Y-%m-%d')
		except (ValueError, KeyError):
			# Skip articles with invalid or missing dates
			continue
		author = article_metadata['author']

		# Only publish articles less than around 4 months old
		months = 4
		oldest_allowed = datetime.now() - timedelta(days=months*30)
		if updated < oldest_allowed:
			continue

		feed.add(title=title, summary=summary, summary_type='text', url=url,
			updated=updated, author=author, published=published)

	return feed.get_response()

# Static files
@app.route('/robots.txt')
@app.route('/favicon.ico')
def serve_static_assets():
	return send_from_directory(app.static_folder, request.path[1:])

# Health check endpoint for monitoring
@app.route('/health')
def health_check():
	return {'status': 'healthy', 'service': 'thebuildmaestro'}, 200

if __name__ == '__main__':
	app.debug = DEBUG
	app.run(host='0.0.0.0')
