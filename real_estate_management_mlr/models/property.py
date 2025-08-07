from odoo import models, fields


class Property(models.Model):
    _name = 'real.estate.property'
    _description = 'Property'

    name = fields.Char(string='Property Name', required=True)
    property_type_id = fields.Many2one(
        'real.estate.property.type',
        string='Property Type',
        required=True,
    )
    address = fields.Text(string='Address')
    city = fields.Char(string='City')
    state = fields.Char('State')
    zip_code = fields.Char('Zip Code')
    description = fields.Text(string='Description')
    latitude = fields.Float('Latitude')
    longitude = fields.Float('Longitude')
    country_id = fields.Many2one('res.country', string='Country')
    price = fields.Float(string='Price')
    status = fields.Selection(
        [
            ('available', 'Available'),
            ('pending', 'Pending'),
            ('sold', 'Sold'),
            ('rented', 'Rented'),
        ],
        string='Status',
        default='available',
    )
    area = fields.Float('Area (sqft)', required=True)
    num_rooms = fields.Integer('Number of Rooms')
    num_bathrooms = fields.Integer('Number of Bathrooms')
    num_floors = fields.Integer('Number of Floors')
    amenities = fields.Many2many('real.estate.amenity', string='Amenities')
    # Relationships
    agent_id = fields.Many2one('real.estate.agent', string='Agent')
    tenant_id = fields.Many2one('real.estate.tenant', string='Tenant')
    sale_id = fields.Many2one('real.estate.sale', string='Sale')
    lease_id = fields.Many2one('real.estate.lease', string='Lease')
    # Images
    image_1920 = fields.Image(
        'Property Image',
        max_width=1920,
        max_height=1920,
    )
    image_gallery = fields.One2many(
        'real.estate.property.image',
        'property_id',
        string='Image Gallery',
    )

    # Customizable Features
    condition = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('needs_renovation', 'Needs Renovation')
    ], string='Condition', required=True)


class PropertyType(models.Model):
    _name = 'real.estate.property.type'
    _description = 'Property Type'

    name = fields.Char(string='Type Name', required=True)


class PropertyImage(models.Model):
    _name = 'real.estate.property.image'
    _description = 'Property Image'

    image_1920 = fields.Image(
        'Image',
        max_width=1920,
        max_height=1920,
        required=True,
    )
    description = fields.Char('Image Description')
    property_id = fields.Many2one(
        'real.estate.property',
        string='Property',
        ondelete='cascade',
    )
