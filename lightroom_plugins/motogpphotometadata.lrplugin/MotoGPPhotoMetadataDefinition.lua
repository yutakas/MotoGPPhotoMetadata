return {

	metadataFieldsForPhotos = {

		{
			id = 'siteId',
		},

		{
			id = 'laplacianvariance',
			title = "Laplacian Variance",
			dataType = 'string', -- Specifies the data type for this field.
			readOnly = true,
			searchable = true,
			browsable = true,
			version = 2,
		},

		{
			id = 'inframed',
			title = "In Framed",
			dataType = 'enum',
			readOnly = true,
			searchable = true,
			browsable = true,
			version = 2,
			values = {
				{
					value = 'true',
					title = "True",
				},
				{
					value = 'false',
					title = "False",
				},
			},
		},

		{
			id = 'motorcyclesize',
			title = "Motorcycle Size",
			dataType = 'string', -- Specifies the data type for this field.
			readOnly = true,
			searchable = true,
			browsable = true,
			version = 3,
		},
		{
			id = 'tenengrad',
			title = "Tenengrad",
			dataType = 'string',
			readOnly = true,
			searchable = true,
			browsable = true,
			version = 2,
		},
		{
			id = 'centered',
			title = "Centered",
			dataType = 'enum',
			readOnly = true,
			searchable = true,
			browsable = true,
			version = 2,
			values = {
				{
					value = 'true',
					title = "True",
				},
				{
					value = 'false',
					title = "False",
				},
			},
		},
		{
			id = 'motogp_team',
			title = "MotoGP Team",
			dataType = 'string',
			readOnly = true,
			searchable = true,
			browsable = true,
			version = 1,
		},
		{
			id = 'bike_color',
			title = "Bike Color",
			dataType = 'string',
			readOnly = true,
			searchable = true,
			browsable = true,
			version = 1,
		},
		{
			id = 'sponsor_names',
			title = "Sponsor Names",
			dataType = 'string',
			readOnly = true,
			searchable = true,
			browsable = true,
			version = 1,
		},
		{
			id = 'logos',
			title = "Logos",
			dataType = 'string',
			readOnly = true,
			searchable = true,
			browsable = true,
			version = 1,
		},
	},
	
	schemaVersion = 1,

}
