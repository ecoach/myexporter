from django.core.urlresolvers import reverse

def steps_nav(user, selected):
    
    all_steps = [
            #'text'         
            #   'styling_class(es)',    
            #       'links_to'
            #           'permission_required'
            #               'selected'
            ['1. Select Table', 
                '',  
                    reverse('myexporter:select_table'),
                        'staff',
                            'select_table',

            ],
            ['2. Select Columns', 
                '',  
                    reverse('myexporter:select_columns'),
                        'staff',
                            'select_columns',
            ],
            ['3. Create File', 
                '',  
                    reverse('myexporter:download_trigger'),
                        'staff',
                            'download_trigger',
            ],
            ['4. Archive', 
                '',  
                    reverse('myexporter:archive'),
                        'staff',
                            'archive',
            ],
            ['Dump SQL', 
                '',  
                    reverse('myexporter:dump_sql'),
                        'staff',
                            'dump_sql',
            ]
        ]

    steps_nav = []
    for nn in all_steps:
        # style the selected option
        if nn[4] == selected:
            nn[1] = 'current'
        # permission?
        if nn[3] == 'any':
            steps_nav.append(nn)
        elif nn[3] == 'staff' and user.is_staff:
            steps_nav.append(nn)

    return steps_nav

