"""
Top 100 most starred GitHub projects grouped by topic description.

Visualized as a interactive 3D pie chart in HTML 5 hosted on GitHub Pages
using Google Charts JavaScript library.
"""

from datetime import datetime, timedelta
import time
from lxml import html
import requests
from pandas_datareader.data import DataReader


print("sleep for 30 seconds")
time.sleep(30)

# most starred repositories first page
page = requests.get('https://github.com/search?utf8=%E2%9C%93&q=stars%3A10000..1000000&type=Repositories')
tree = html.fromstring(page.content)
data = {}
topic_xpath = '//div/a[contains(@class,"topic-tag")]/text()'

# start code for line chart
now = datetime.now()
start = (now - timedelta(days=365)).date()
end = now.date()
# debug
print(start)
print(end)
# Set the ticker
ticker = 'AAPL'  #Apple
# Set the data source
data_source = 'google'  #use google finance
# Import the stock prices
stock_prices = DataReader(ticker, data_source, start, end)
# build the 2d array for the line chart
apple_data = []
for k, v in stock_prices['Close'].to_dict().items():
    k = int(time.mktime(k.timetuple()))
    t = datetime.fromtimestamp(k)
    apple_data.append([t.strftime('%Y-%m-%d'), v])



def get_topics():
    """Build topic 2D array."""
    topics = tree.xpath(topic_xpath)
    for x in topics:
        x = x.strip()
        if x in data:
            data[x] += 1
        else:
            data[x] = 1


# get first page of results
get_topics()
# retrieve total 10 pages of results based on GitHub limits
while tree.xpath('//div[@class="pagination"]/a[@class="next_page"]'):
    page = requests.get('https://github.com' +
                        tree.xpath('//div[@class="pagination"]/a[@class="next_page"]/@href')[0])
    tree = html.fromstring(page.content)
    get_topics()

data = sorted(([k, v] for k, v in data.items()), key=lambda d: d[1], reverse=True)
print(data)

# debug
apple_data = sorted(([k, v] for k, v in apple_data), key=lambda d: d[0])
print(apple_data)

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
    <div id="apple_chart" style="width: 900px; height: 600px;"></div>
    <footer>Last built: {t}</footer>""".format(t=datetime.now())
page += """
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load("current", {packages:["corechart"]});
      google.charts.setOnLoadCallback(drawChart);
      google.charts.setOnLoadCallback(drawChartApple);
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
      function drawChartApple() {
        var data = new google.visualization.DataTable();
        data.addColumn('string', 'Date');
        data.addColumn('number', 'Price');"""
page += """
        data.addRows({data});""".format(data=apple_data)
page += """
        var options = {
          title: 'Apple share price over the last year.',
          is3D: true,
        };
        var chart = new google.visualization.LineChart(document.getElementById('apple_chart'));
        chart.draw(data, options);
      }
    </script>
  </body>
</html>"""

target = open('site/index.html', 'w')
target.write(page)
target.close()
