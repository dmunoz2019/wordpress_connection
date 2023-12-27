# -*- coding: utf-8 -*-
from odoo import models, fields, api
import requests
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class WordpressSyncAbstract(models.AbstractModel):
    _name = 'wordpress.sync.abstract'
    _description = 'WordPress Synchronization process'

    @api.model
    def fetch_wordpress_posts(self):
        # Logic to fetch posts from WordPress
        url = "https://demos-dkg.site/demo/wp-json/wp/v2/posts"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _logger.error(f"Error fetching WordPress posts: {e}")
            return []


    @api.model
    def process_and_update_posts(self, posts_data, wordpress_post_model):
        for post in posts_data:
            post_id = post['id']
            existing_post = wordpress_post_model.search([('post_id', '=', post_id)])
            
            # Parse the 'modified' date string into a datetime object
            modified_date = datetime.strptime(post['modified'], '%Y-%m-%dT%H:%M:%S')

            # Prepare the data for a new post or updating an existing one
            new_data = {
                'post_id': post_id,
                'title': post['title']['rendered'],
                'content': post['content']['rendered'],
                # Parse the 'date' string into a datetime object
                'date_published': datetime.strptime(post['date'], '%Y-%m-%dT%H:%M:%S'),
                'link': post['link'],
                'last_modified': modified_date  # This is a datetime object
            }

            # Check if the post exists and if it was last modified before the new modified date
            if existing_post and (existing_post.last_modified < modified_date):
                # Check for any changes between the existing post and new data
                changes = {field: value for field, value in new_data.items() if getattr(existing_post, field) != value}
                if changes:
                    # Update the existing post with the new changes
                    existing_post.write(changes)
            elif not existing_post:
                # Create a new post if it does not exist
                wordpress_post_model.create(new_data)

    @api.model
    def sync_wordpress_posts(self):
        wordpress_post_model = self.env['wordpress.post']
        posts_data = self.fetch_wordpress_posts()
        if posts_data:
            self.process_and_update_posts(posts_data, wordpress_post_model)


class WordpressPost(models.Model):
    _name = 'wordpress.post'
    _description = 'WordPress Post'

    title = fields.Char(string='Title', required=True)
    content = fields.Html(string='Content')
    post_id = fields.Integer(string='Post ID', required=True, index=True)
    date_published = fields.Datetime(string='Date Published')
    link = fields.Char(string='Link', required=True)
    last_modified = fields.Datetime(string='Last Modified')
