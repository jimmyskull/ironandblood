
import csv
import json

MAP_NAME = 'denmark'
USER_COUNT = 4

COLORS = ['#FFA630', '#D7E8BA', '#4DA1A9', '#2E5077', '#611C35']

with open(MAP_NAME + '.csv', 'rt', encoding='utf8') as csvfile:
  csv_data = csv.reader(csvfile, delimiter=',', quotechar='"')
  data = [row for row in csv_data]

  territory_per_user = len(data) / USER_COUNT

  json_data = list()
  color_data = list()

  for i, territory in enumerate(data):
    if i == 0:
      continue
    owner = int(territory[4])
    code = territory[0]
    json_data.append("""
  {{
    "model": "game.territory",
    "pk": {pk},
    "fields": {{
      "owner": {owner},
      "code": "{code}",
      "name": "{name}",
      "land_area": {land_area}
    }}
  }}""".format(pk=i,
      owner=owner,
      code=code,
      name=territory[1],
      land_area=territory[3]))

    color_data.append("'{code}': '{color}'".format(code=code,
      color=COLORS[owner ]))

  with open('jvectormap-'+MAP_NAME+'.json', 'w') as outfile:
    objs = json.loads('[' + ', '.join(json_data) + ']')
    json.dump(objs, outfile,
      indent=2,
      separators=(',', ': '),
      ensure_ascii=False)

  with open('colordata-'+MAP_NAME+'.js', 'w') as outfile:
    outfile.write('var colorData = {{ {lst} }};\n'.format(lst=','.join(color_data)))
