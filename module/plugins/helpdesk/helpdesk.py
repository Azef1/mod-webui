#!/usr/bin/python
#!/usr/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2009-2014:
#    Gabes Jean, naparuba@gmail.com
#    Gerhard Lausser, Gerhard.Lausser@consol.de
#    Gregory Starck, g.starck@gmail.com
#    Hartmut Goebel, h.goebel@goebel-consult.de
#    Frederic Mohier, frederic.mohier@gmail.com
#
# This file is part of Shinken.
#
# Shinken is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Shinken is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Shinken.  If not, see <http://www.gnu.org/licenses/>.

import json

from shinken.log import logger

### Will be populated by the UI with it's own value
app = None

def create_ticket(name):
    if not app.helpdesk_module.is_available():
        app.redirect404()

    logger.info("[WebUI-helpdesk] request to create a ticket for %s", name)

    app.response.content_type = 'application/json'
    callback = app.request.query.get('callback', None)
    response_text = app.request.query.get('response_text', 'Ticket creation succeeded')

    parameters = {}
    parameters['name']          = app.request.query.get('name', name)
    parameters['itemtype']      = app.request.query.get('itemtype', 'Computer')
    parameters['item']          = app.request.query.get('item', '')
    parameters['entity']        = app.request.query.get('entity', '')

    parameters['type']          = app.request.query.get('ticket_type', '')
    parameters['category']      = app.request.query.get('ticket_category', '')
    parameters['title']         = app.request.query.get('ticket_title', '')
    parameters['content']       = app.request.query.get('ticket_content', '')
    logger.info("[WebUI-helpdesk] request to create a ticket with %s", parameters)

    result = { 'status': 405, 'message': "Ticket creation failed", 'ticket': None}

    try:
        # Request for ticket creation
        ticket = None
        if app.create_ticket:
            ticket = app.create_ticket(parameters)
            if ticket:
                result = { 'status': 200, 'message': response_text, 'ticket': ticket}

        if callback:
            return '''%s(%s)''' % (callback, json.dumps(result))
        else:
            return json.dumps(result)
    except Exception:
        logger.info("[WebUI-helpdesk] ticket creation failed!")
        return json.dumps(result)

def add_ticket(name):
    if not app.helpdesk_module.is_available():
        app.redirect404()

    user = app.request.environ['USER']
    elt = app.datamgr.get_element(name, user) or app.redirect404()
    logger.info("[WebUI-helpdesk] adding a ticket for %s from %s", name, user)

    try:
        itemtype = elt.customs['_ITEMTYPE']
        items_id = elt.customs['_ITEMSID']
        entities_id = elt.customs['_ENTITIESID']

        # helpdesk_configuration = app.helpdesk_module.get_ui_helpdesk_configuration()
        session = app.helpdesk_module.get_ui_session()
        logger.info("[WebUI-helpdesk] session: %s", session)
        types = app.helpdesk_module.get_ui_types()
        logger.info("[WebUI-helpdesk] types: %s", types)
        categories = app.helpdesk_module.get_ui_categories()
        logger.info("[WebUI-helpdesk] categories: %s", categories)
        templates = app.helpdesk_module.get_ui_templates()
        logger.info("[WebUI-helpdesk] templates: %s", templates)

        return {'name': name, 'itemtype': itemtype, 'items_id': items_id, 'entities_id': entities_id, 'types': types, 'categories': categories, 'templates': templates}
    except Exception as e:
        logger.info("[WebUI-helpdesk] ticket creation is not possible for %s, exception: %s", name, e)
        return {'name': None}

def get_element_tickets(name):
    if app.helpdesk_module.is_available():
        logger.info("[WebUI-helpdesk] requesting tickets for %s", name)

        tickets = app.helpdesk_module.get_ui_tickets(name)
        return {'app': app, 'tickets': tickets}

    return {'tickets': None}

pages = {
    create_ticket:{
        'name': 'TicketCreate',
        'route': '/helpdesk/ticket/create/:name'
    },
    add_ticket:{
        'name': 'TicketAdd',
        'route': '/helpdesk/ticket/add/:name',
        'view': 'add_ticket'
    },
    get_element_tickets:{
        'name': 'TicketList',
        'route': '/helpdesk/tickets/:name',
        'view': 'helpdesk'
    }
}
