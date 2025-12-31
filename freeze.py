from flask_frozen import Freezer
from niski84 import app, CONTENT_PATH
import os

# Configurable build directory
BUILD_DIR = os.environ.get('BUILD_DIR', 'build')

# Set the build directory for Frozen-Flask
app.config['FREEZER_DESTINATION'] = BUILD_DIR

freezer = Freezer(app, with_static_files=True)

# Go through the filesystem to find content (usually article images)
# for the serve_article_asset() function:
@freezer.register_generator
# route('/articles/<id>/<content>')
def serve_article_asset():
	# We don't really need to recurse:
	try:
		articles = os.listdir( os.path.join(CONTENT_PATH, 'articles') )
	except OSError:
		return
	for articleid in articles:
		try:
			for filename in os.listdir( os.path.join(CONTENT_PATH, 'articles', articleid) ):
				if filename in ['README.md', 'metadata']:
					continue
				yield {'id': articleid, 'content': filename }
		except OSError:
			continue

@freezer.register_generator
def serve_static_assets():
	for file in ['robots.txt', 'favicon.ico']:
		yield '/{file}'.format(file=file)

if __name__ == '__main__':
	freezer.freeze()
	print(f"Site built successfully to {BUILD_DIR}/")
	#freezer.run(debug=True)
