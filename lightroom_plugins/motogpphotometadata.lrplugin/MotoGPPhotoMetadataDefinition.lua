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
	},
	
	schemaVersion = 1,

}
