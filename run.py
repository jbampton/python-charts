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


print("sleep for 45 seconds")
time.sleep(45)

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
#
apple_data = []
day_endings = {
    1: 'st',
    2: 'nd',
    3: 'rd',
    21: 'st',
    22: 'nd',
    23: 'rd',
    31: 'st'
}
# build the 3 element sub arrays for the line chart
for k, v in stock_prices['Close'].to_dict().items():
    k = int(time.mktime(k.timetuple()))
    t = datetime.fromtimestamp(k)
    # [date, price, tooltip]
    apple_data.append([t.strftime('%Y-%m-%d'), v, '{d}\nPrice: {p}'.format(d=t.strftime('%A the %-d' + day_endings.get(int(t.strftime('%-d')), 'th') + ' of %B %Y'), p=v)])


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

# sort by value descending
data = sorted(([k, v] for k, v in data.items()), key=lambda d: d[1], reverse=True)
# debug
print(data)

# sort by date ascending
apple_data = sorted(([i, j, k] for i, j, k in apple_data), key=lambda d: d[0])
# debug
print(apple_data)

page = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <title>Python Charts</title>
    <link rel="stylesheet" href="assets/bootstrap-4.0.0-beta.2-dist/css/bootstrap.min.css">
    <style>
        .chart { width: 100%; min-height: 450px; }
    </style>
  </head>
  <body>
    <div class="row">
        <div class="col-md-12">
            <div id="piechart_3d" class="chart"></div>
            <div id="apple_chart" class="chart"></div>
        </div>
    </div>
    """
page += """<footer>Last built: {t}</footer>""".format(t=datetime.now())
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
          is3D: true
        };
        var chart = new google.visualization.PieChart(document.getElementById('piechart_3d'));
        chart.draw(data, options);
      }
      function drawChartApple() {
        var data = new google.visualization.DataTable();
        data.addColumn('date', 'Date');
        data.addColumn('number', 'Price');
        data.addColumn({type: 'string', role: 'tooltip'});"""
page += """
        var arr = {data}""".format(data=apple_data)
page += """        
        for(var i=0; i<arr.length; i++){
            var arr_date = arr[i][0].split('-');
            arr[i][0] = new Date(arr_date[0], parseInt(arr_date[1])-1, arr_date[2]);
        }        
        data.addRows(arr);
        var options = {
          title: 'Apple share price over the last year.',
          is3D: true,
          legend: {position: 'top', alignment: 'start'},
          selectionMode: 'multiple',
          trendlines: {
            0: {
              type: 'linear',
              color: 'green',
              lineWidth: 3,
              opacity: 0.3,
              tooltip: false,
              labelInLegend: 'Trend Line',
              visibleInLegend: true
            }
          }
        };
        var chart = new google.visualization.LineChart(document.getElementById('apple_chart'));
        chart.draw(data, options);
      }
    </script>
    <!-- Latest compiled and minified JavaScript -->
    <script src="assets/js/jquery-3.2.1.min.js"></script>
    <script src="assets/js/popper-1.12.6.min.js"></script> 
    <script src="assets/bootstrap-4.0.0-beta.2-dist/js/bootstrap.min.js"></script>
    <script>
      $(window).resize(function(){
        drawChart();
        drawChartApple();
      });
    </script>   
  </body>
</html>"""

target = open('site/index.html', 'w')
target.write(page)
target.close()
