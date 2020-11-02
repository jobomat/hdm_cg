MAYA_SETTINGS = {
    'path_prefixes': {
        'base': '',  # <--- If empty "../../" will be base-path
        # 'archive': 'scripts/archive',
    },
    'maya_env_vars': [
        {
            'name': 'PYTHONPATH',
            'values': [
                '{base}/cg',
                '{base}/maya/scripts/python'
            ]
        },
        {
            'name': 'MAYA_SCRIPT_PATH',
            'recursive': True,
            'values': [
                '{base}/maya/scripts/mel'
            ],
        },
        # {
        #     'name': 'MAYA_SCRIPT_PATH',
        #     'values': [
        #         '{base}/maya/BonusTools/Contents/scripts/pc.versions.shortName()'
        #     ],
        # },
        {
            'name': 'MAYA_PLUG_IN_PATH',
            'values': [
                '{base}/maya/plugins/pc.versions.shortName()/platform.system()',
                # '{base}/maya/BonusTools/Contents/plug-ins/pc.versions.shortName()/platform.system()'
            ]
        },
        {
            'name': 'XBMLANGPATH',
            'recursive': True,
            'values': [
                '{base}/maya/icons',
            ],
        },
        {
            'name': 'MAYA_FORCE_C_LOCALE',
            'replace': True,
            'values': ['1']
        }
    ],
    'json_shelf_dir': '{base}/maya/shelfes/json',
    'maya_shelfes':[]
}
