# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response
import logging

_logger = logging.getLogger(__name__)

class WordpressSyncController(http.Controller):
    @http.route('/wordpress_sync', type='http', auth='user', methods=['POST'], csrf=False)
    def wordpress_sync(self):
        try:
            request.env['wordpress.sync.abstract'].sync_wordpress_posts()
            return Response("{'status': 'success'}", content_type='application/json')
        except Exception as e:
            _logger.error("Error syncing WordPress posts: %s", e)
            return Response("{'status': 'error', 'message': '%s'}" % str(e), status=500, content_type='application/json')
