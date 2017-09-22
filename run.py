"""
Top 100 most starred GitHub projects grouped by topic description and visualized as a
interactive 3D pie chart in HTML 5 hosted on GitHub Pages using Google Charts JavaScript library.
"""

import datetime
import os
import time
from lxml import html
import requests


print("sleep for 30 seconds")
time.sleep(30)


def get_topics(topic_xpath, data):
    """
    build topic 2D array
    """
    topics = tree.xpath(topic_xpath)
    for x in topics:
        x = x.strip()
        if x in data:
            data[x] += 1
        else:
            data[x] = 1
    return data


# most starred repositories first page
page = requests.get('https://github.com/search?utf8=%E2%9C%93&q=stars%3A10000..1000000&type=Repositories')
tree = html.fromstring(page.content)

data = {}
topic_xpath = '//div/a[contains(@class,"topic-tag")]/text()'

data = get_topics(topic_xpath, data)

# retrieve total 10 pages of results
while tree.xpath('//div[@class="pagination"]/a[@class="next_page"]'):
    page = requests.get('https://github.com' + tree.xpath('//div[@class="pagination"]/a[@class="next_page"]/@href')[0])
    tree = html.fromstring(page.content)
    data = get_topics(topic_xpath, data)

data = sorted(([k, v] for k, v in data.items()), key=lambda d: d[1], reverse=True)

print(data)

page = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <title>Python Charts</title>
  </head>
  <body>
    <div id="piechart_3d" style="width: 900px; height: 600px;"></div>
    <footer>Last built: {t}</footer>""".format(t=datetime.datetime.now())
page += """
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load("current", {packages:["corechart"]});
      google.charts.setOnLoadCallback(drawChart);
      function drawChart() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Topic');
        data.addColumn('number', 'Amount');"""
page += """
        data.addRows({data});""".format(data=data)
page += """
        var options = {
          title: 'Top 100 most starred GitHub repositories grouped by topic',
          is3D: true,
        };
        var chart = new google.visualization.PieChart(document.getElementById('piechart_3d'));
        chart.draw(data, options);
      }
    </script>
  </body>
</html>"""

try:
    os.makedirs('site')
except OSError:
    pass

target = open('site/index.html', 'w')
target.write(page)
target.close()
