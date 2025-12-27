# thebuildmaestro-website

The code for the website [thebuildmaestro.com](http://thebuildmaestro.com)

A personal website/blog built as a content-focused, responsive site that prioritizes simplicity and control over corporate blogging platforms.

## Overview

This is a personal website built using Python and Flask, designed to read content from directories containing Markdown files. The site is generated as static HTML using Frozen-Flask and deployed to AWS S3 + CloudFront.

## Technology Stack

- **Backend**: Python with Flask
- **Static Site Generation**: Frozen-Flask (generates static HTML files)
- **Content Format**: Markdown files (stored as `README.md` for easy offline access)
- **Frontend**: Bootstrap, Pure CSS, custom SCSS
- **JavaScript Libraries**: jQuery, Masonry (for photo layout), TinySort
- **Deployment**: AWS S3 + CloudFront (infrastructure defined in CloudFormation)

## Key Features

1. **File-based Content Management**
   - Content stored in directories with Markdown `README.md` files
   - Each content item has a `metadata` file with title, author, dates, description
   - Supports articles and code projects
   - Images and files can be stored alongside content directories

2. **Main Sections**
   - **Articles**: Blog posts and articles
   - **Code**: Code projects and repositories
   - **Photos**: Photo gallery with thumbnails
   - **Contact**: Contact page
   - **Atom Feed**: RSS feed for recent articles

3. **Design Philosophy**
   - Content-focused, responsive design
   - Mobile-friendly layout
   - Sidebar navigation menu
   - Code syntax highlighting (via Pygments)
   - Custom SCSS styling

## Project Structure

- `niski84.py` - Main Flask application with routes and content loading
- `freeze.py` - Script to generate static HTML files using Frozen-Flask
- `static/content/` - Content directories (articles, code) containing Markdown files
- `static/files/photos/` - Photo gallery images and thumbnails
- `templates/` - Jinja2 templates for rendering pages
- `aws-cloudformation.json` - AWS infrastructure definition

## Deployment

The site uses AWS CloudFormation to provision:

- **S3 bucket** for static website hosting
- **CloudFront CDN** distribution
- **Route53** DNS configuration
- **Lambda function** for automated deployments (triggered by GitHub webhooks)
- **EC2 instances** for building and deploying the site

The build process uses Grunt to run `freeze.py`, which generates static HTML files. The static site is then synced to S3 for hosting.

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. Run the Flask development server:
   ```bash
   python niski84.py
   ```

3. Generate static site:
   ```bash
   python freeze.py
   # or
   npm run grunt
   ```

## License

BSD
